import pandas as pd
import os
import numpy as np
import geopandas as gpd
from datetime import datetime
from shapely import Point
from typing import Optional

from src.trip_detect import get_popular_places, trip_detector
from src.calculate_distance import calculate_distance


def texttodf(filepath, columnnames):
    df = pd.read_csv(filepath, sep=" ", header=None, names=columnnames)
    return df


def readinuser(path: str) -> pd.DataFrame:
    """
    Reads motion data of a single user and single day, which is spread across multiple files, into a single dataframe.
    """
    location_df = texttodf(
        os.path.join(path, "Torso_Location.txt"),
        [
            "time_ms",
            "Ignore",
            "Ignore2",
            "accuracy_m",
            "latitude",
            "longitude",
            "altitude",
        ],
    )
    location_df = location_df.drop(columns=["Ignore", "Ignore2"])
    location_df["geometry"] = location_df.apply(
        func=lambda x: Point(x["latitude"], x["longitude"]), axis=1
    )
    location_df["timestamp"] = location_df["time_ms"].apply(
        func=lambda x: datetime.utcfromtimestamp(x / 1000)
    )
    location_df = location_df.set_index("timestamp")
    location_df = location_df[~location_df.index.duplicated(keep="first")]
    location_df_resampled = location_df.resample("1s").ffill()

    motion_df = texttodf(
        os.path.join(path, "Torso_Motion.txt"),
        [
            "time_ms",
            "acc_x",
            "acc_y",
            "acc_z",
            "gyro_x",
            "gyro_y",
            "gyro_z",
            "mag_x",
            "mag_y",
            "mag_z",
            "or_w",
            "or_x",
            "or_y",
            "or_z",
            "grav_x",
            "grav_y",
            "grav_z",
            "lin_acc_x",
            "lin_acc_y",
            "lin_acc_z",
            "press_hPa",
            "altitude",
            "temp",
        ],
    )
    motion_df["timestamp"] = motion_df["time_ms"].apply(
        func=lambda x: datetime.utcfromtimestamp(x / 1000)
    )
    motion_df = motion_df.set_index("timestamp")
    motion_df_resampled = motion_df.resample("1s").ffill()

    labels_df = texttodf(
        os.path.join(path, "labels_track_main.txt"),
        ["time_start_ms", "time_end_ms", "label"],
    )
    labels_df["start_time"] = labels_df["time_start_ms"].apply(
        func=lambda x: datetime.utcfromtimestamp(x / 1000)
    )
    labels_df["end_time"] = labels_df["time_end_ms"].apply(
        func=lambda x: datetime.utcfromtimestamp(x / 1000)
    )
    # filter out rows where start_time is after the end_time
    labels_df = labels_df[labels_df["start_time"] <= labels_df["end_time"]]
    intervals = pd.IntervalIndex.from_arrays(
        labels_df["start_time"], labels_df["end_time"], closed="both"
    )
    labels_df.index = intervals

    def get_label(timestamp):
        label = labels_df[labels_df.index.contains(timestamp)]["label"]
        return label.values[0] if not label.empty else None

    # df = pd.merge_asof(location_df_resampled, motion_df_resampled, left_index=True, right_index=True)
    df = pd.merge_asof(location_df_resampled, motion_df_resampled, on="timestamp")
    df = df.set_index("timestamp")
    df["label"] = df.index.to_series().apply(get_label)

    return df


def calculate_speed(array_distances, array_deltatime):
    if len(array_distances) != len(array_deltatime):
        print("input vector length does not match!")
        return np.nan
    else:
        speed = [0] * (len(array_distances) - 1)
        for i in range(0, len(array_distances) - 1):
            speed[i] = array_distances.iloc[i] / array_deltatime.iloc[i] * 3.6
        speed = np.append(speed, [0])
        return speed


def calculate_acceleration(speed, array_deltatime):
    acceleration = np.diff(speed)
    acceleration = np.append(acceleration, [0]) / array_deltatime
    return acceleration


def correct_speed(speed, acceleration, threshold):
    if len(speed) != len(acceleration):
        print("input vector length does not match!")
        return np.nan
    else:
        speed_corr = np.zeros((len(speed), 1))
        speed_corr = speed
        for i in range(0, len(speed) - 3):
            # speed_corr[i] = speed[i]
            if abs(acceleration.iloc[i]) > threshold:
                # speed_corr[i:i+3] = np.NaN
                speed_corr[i - 3 : i + 3] = np.nan
        return speed_corr


def delete_rows_with_unchanged_geometry(gdf):
    unchanged_count = 0
    last_geometry = None
    rows_to_delete = []
    temp_rows_to_delete = []
    check = False

    for index, row in gdf.iterrows():
        current_geometry = row.geometry

        if current_geometry == last_geometry:
            unchanged_count += 1
            if check == False:
                check = True
            else:
                temp_rows_to_delete.append(index)
        else:
            if row.distance > 50 & unchanged_count >= 5:  # jump detected
                rows_to_delete.extend(temp_rows_to_delete)
            temp_rows_to_delete = []
            check = False
            unchanged_count = 0  # Reset the count if there's a change

        last_geometry = current_geometry
    gdf = gdf.drop(rows_to_delete)

    return gdf


def movingaverage(values, window):
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(values, weights, "same")
    return sma


# Function to convert quaternion to rotation matrix
def quaternion_to_rotation_matrix(q):
    w, x, y, z = q
    R = np.array(
        [
            [1 - 2 * y**2 - 2 * z**2, 2 * x * y - 2 * w * z, 2 * x * z + 2 * w * y],
            [2 * x * y + 2 * w * z, 1 - 2 * x**2 - 2 * z**2, 2 * y * z - 2 * w * x],
            [2 * x * z - 2 * w * y, 2 * y * z + 2 * w * x, 1 - 2 * x**2 - 2 * y**2],
        ]
    )
    return R


# Function to transform local acceleration to global coordinates
def transform_local_acceleration(quaternion, acceleration_local):
    R = quaternion_to_rotation_matrix(quaternion)

    acceleration_local = np.array(acceleration_local).reshape((3, 1))
    acceleration_global = np.dot(R, acceleration_local)

    return acceleration_global


# Function to for inculding Quaternion functions in GeoDataFrame
def get_data_from_acc(gdf):
    gdf["acc_down"] = np.nan
    gdf["acc_forw"] = np.nan

    for i, row in gdf.iterrows():
        quaternion = [row["or_w"], row["or_x"], row["or_y"], row["or_z"]]
        acceleration_local = [row["acc_x"], row["acc_y"], row["acc_z"]]

        acceleration_global = transform_local_acceleration(
            quaternion, acceleration_local
        )

        downward_acceleration = acceleration_global[2, 0]
        orthogonal_acceleration = np.sqrt(
            acceleration_global[0, 0] ** 2 + acceleration_global[1, 0] ** 2
        )

        gdf.at[i, "acc_down"] = downward_acceleration
        gdf.at[i, "acc_forw"] = orthogonal_acceleration

    return gdf


def acc_down_shift_ma(gdf, window):
    gdf["acc_down_shift_ma"] = gdf["acc_down"].copy()
    avg = sum(gdf["acc_down"]) / len(gdf["acc_down"])
    gdf["acc_down_shift_ma"] = gdf["acc_down_shift_ma"] - avg
    gdf["acc_down_shift_ma"] = abs(gdf["acc_down_shift_ma"])
    gdf["acc_down_shift_ma"] = movingaverage(gdf["acc_down_shift_ma"], window)

    return gdf


def get_trip_times(gdf):
    hotspot_polygons = get_popular_places(gdf)
    trips = trip_detector(gdf, hotspot_polygons)
    times = []
    for trip in trips:
        times.append({"start": trip.index[0], "end": trip.index[-1]})
    times = sorted(times, key=lambda x: x["start"])
    return pd.DataFrame(times)


def load_trip_times(gdf: gpd.GeoDataFrame, filename: str) -> pd.DataFrame:
    """
    Trip time calculation takes some time, therefore trip times are cached as separate csv file
    """
    trip_times: pd.DataFrame
    if os.path.isfile(filename):
        print("Reading trip times from {}".format(filename))
        trip_times = pd.read_csv(filename, parse_dates=["start", "end"])
    else:
        print("Calculating trip times for {}".format(filename))
        trip_times = get_trip_times(gdf)
        trip_times.to_csv(filename)

    return trip_times


def add_trip_kpis(df, trip_times):
    """Calculates the average speed during a trip and duration of the trip and writes these into the dataframe as new columns"""
    df["trip_speed"] = 0.0
    df["trip_duration"] = 0.0
    for _, trip in trip_times.iterrows():
        trip_indices = (df.index >= trip.start) & (df.index <= trip.end)
        df_trip = df.loc[trip_indices]
        avg_speed = df_trip["speed_gps"].mean()
        trip_time = trip.end - trip.start
        df.loc[trip_indices, "trip_speed"] = avg_speed
        df.loc[trip_indices, "trip_duration"] = trip_time.total_seconds()


def preprocess(
    df: pd.DataFrame,
    file_path_trip_times: str,
    acceleration_threshold: Optional[float] = 15.0,
) -> gpd.GeoDataFrame:

    # Sort by time stamp
    df = df.sort_index()

    # save date as column
    df["date"] = df.index.date

    # filter nan geometry
    df = df[df["geometry"].notna()]

    # convert df to gdf
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    # change lon and lat
    gdf["geometry"] = gdf["geometry"].apply(lambda geom: Point(geom.y, geom.x))

    # calculate distances and deltatimes (from gps)
    gdf["distance"] = calculate_distance(gdf.geometry.y, gdf.geometry.x)

    # delete row, if geometry hasn't changed for at least 5 entries and there is a distance jump
    gdf = delete_rows_with_unchanged_geometry(gdf)

    delta_times = gdf.index.to_series().diff().apply(lambda x: x.total_seconds())

    # add speed column (from GPS data)
    speed = calculate_speed(gdf["distance"], delta_times)
    gdf["speed_gps"] = speed

    acc = calculate_acceleration(speed, delta_times)
    gdf["acc_gps"] = acc

    # add corrected speed (from GPS data)
    speed_corr = correct_speed(speed, acc, acceleration_threshold)
    gdf["speed_corr"] = speed_corr

    # add moving average of speed (from GPS data)
    gdf["speed_ma"] = movingaverage(gdf["speed_corr"], 10)

    # add data from acc (IMU)
    gdf = get_data_from_acc(gdf)

    # add moving average for acc_down
    gdf["acc_down_ma"] = movingaverage(gdf["acc_down"], 10)

    # add moving average for acc_forw
    gdf["acc_forw_ma"] = movingaverage(gdf["acc_forw"], 300)

    # calculation shifted acc_down mean
    gdf = acc_down_shift_ma(gdf, 300)

    # Calculate KPIs for trips
    trip_times = load_trip_times(gdf, file_path_trip_times)
    add_trip_kpis(gdf, trip_times)

    return gdf
