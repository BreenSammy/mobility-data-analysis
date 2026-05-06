import os
import pandas as pd
import numpy as np


def read_trip_times(path):
    return pd.read_csv(path, parse_dates=["start", "end"])


def read_data(path):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df = df.set_index("timestamp")
    return df


def create_trips(df, trip_times):
    """Calculates the average speed during a trip and duration of the trip and writes these into the dataframe as new columns"""
    result = []
    for _, trip in trip_times.iterrows():
        trip_dict = {}
        trip_indices = (df.index >= trip.start) & (df.index <= trip.end)
        df_trip = df.loc[trip_indices]
        trip_dict["start"] = trip.start
        trip_dict["end"] = trip.end
        trip_dict["avg_speed"] = round(df_trip["speed_corr"].mean(), 2)
        trip_dict["median_speed"] = round(df_trip["speed_corr"].median(), 2)
        trip_dict["max_speed"] = round(df_trip["speed_corr"].max(), 2)
        trip_dict["min_speed"] = round(df_trip["speed_corr"].min(), 2)
        trip_dict["std_speed"] = round(np.std(df_trip["speed_corr"]), 2)
        trip_dict["std_acc_forw"] = round(np.std(df_trip["acc_forw"]), 2)
        trip_dict["std_acc_down"] = round(np.std(df_trip["acc_down"]), 2)
        trip_dict["min_acc_forw"] = round(df_trip["acc_forw"].min(), 2)
        trip_dict["avg_acc_forw"] = round(df_trip["acc_forw"].mean(), 2)
        trip_dict["median_acc_forw"] = round(df_trip["acc_forw"].median(), 2)
        trip_dict["median_acc_down"] = round(df_trip["acc_down"].median(), 2)
        trip_dict["max_acc_forw"] = round(df_trip["acc_forw"].max(), 2)
        trip_dict["avg_acc_down"] = round(df_trip["acc_down"].mean(), 2)
        trip_dict["max_acc_down"] = round(df_trip["acc_down"].max(), 2)
        trip_dict["duration"] = (trip.end - trip.start).total_seconds()
        trip_dict["distance"] = round(df_trip["distance"].sum(), 2)
        trip_dict["label"] = trip.label
        result.append(trip_dict)
        # print("Start time:" + trip.start.strftime("%m/%d/%Y, %H:%M:%S"))
        # print("End time:" + trip.end.strftime("%m/%d/%Y, %H:%M:%S"))
        # print(trip_time)
    return pd.DataFrame(result)


def getlabel(tripdf, df):
    df = df.reset_index()
    tripdf["label"] = None

    for index, row in tripdf.iterrows():
        start_index = df.index[df["timestamp"] == row.start].tolist()[0]
        end_index = df.index[df["timestamp"] == row.end].tolist()[0]
        labellist = df.iloc[list(np.arange(start_index, end_index + 1))]["label"].values
        unique, counts = np.unique(labellist, return_counts=True)
        label = unique[np.argmax(counts)]
        tripdf.at[index, "label"] = label

    return tripdf


def trip_creation_data():
    users = {
        "User1": {
            "trip_times": "trip_times_from_data_user1.csv",
            "data": "df1_new.csv",
            "filepath": "trips_from_data_user1.csv",
        },
        "User2": {
            "trip_times": "trip_times_from_data_user2.csv",
            "data": "df2_new.csv",
            "filepath": "trips_from_data_user2.csv",
        },
    }

    for user in users.values():
        trip_times = read_trip_times("trips/" + user["trip_times"])
        df = read_data(user["data"])

        trips = create_trips(df, trip_times)
        trips.to_csv(os.path.join("trips", user["filepath"]), index=False)


def trip_creation_data_from_given():
    users = {
        "User1": {
            "trip_times": "trip_times_from_data_User1.csv",
            "data": "df1_new.csv",
            "filepath": "trips_user1_given.csv",
        },
        "User2": {
            "trip_times": "trip_times_from_data_User2.csv",
            "data": "df2_new.csv",
            "filepath": "trips_user2_given.csv",
        },
    }

    for user in users.values():
        trip_times = read_trip_times(os.path.join("trips", user["trip_times"]))
        df = read_data(user["data"])

        trips = create_trips(df, trip_times)
        trips.to_csv(os.path.join("trips", user["filepath"]), index=False)


def trip_creation_data_from_given():
    users = {
        "User1": {
            "trip_times": "trip_times_from_data_User1.csv",
            "data": "df1_new.csv",
            "filepath": "trips_user1_given.csv",
        },
        "User2": {
            "trip_times": "trip_times_from_data_User2.csv",
            "data": "df2_new.csv",
            "filepath": "trips_user2_given.csv",
        },
    }

    for user in users.values():
        trip_times = read_trip_times(os.path.join("trips", user["trip_times"]))
        df = read_data(user["data"])

        trips = create_trips(df, trip_times)
        trips.to_csv(os.path.join("trips", user["filepath"]), index=False)


def trips_from_detector():
    users = {
        "User1": {
            "trip_times": "trip_times_user_1.csv",
            "data": "df1_new.csv",
            "filepath": "trips_user1.csv",
        },
        "User2": {
            "trip_times": "trip_times_user_2.csv",
            "data": "df2_new.csv",
            "filepath": "trips_user2.csv",
        },
    }

    for user in users.values():
        trip_times = read_trip_times(user["trip_times"])
        df = read_data(user["data"])
        trip_times = getlabel(trip_times, df)

        trips = create_trips(df, trip_times)
        trips.to_csv(os.path.join("trips", user["filepath"]), index=False)


if __name__ == "__main__":
    trip_creation_data()
