import geopandas as gpd
import numpy as np
import geopy
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from shapely.geometry import Point

from src.calculate_distance import calculate_distance

MINIMUM_TRIP_LENGTH_KM = 0.1


def total_distance(my_mobility_data):
    total_distance = 0
    distances = calculate_distance(
        my_mobility_data.geometry.y, my_mobility_data.geometry.x
    )
    total_distance = distances.sum() / 1000

    return total_distance


def get_popular_places(
    my_mobility_data_cont, N_BIGGEST_HOTSPOTS=30, FACTOR_BINSIZE=8, crs="epsg:4326"
):
    min_lat = min(my_mobility_data_cont.geometry.y)
    max_lat = max(my_mobility_data_cont.geometry.y)
    min_lon = min(my_mobility_data_cont.geometry.x)
    max_lon = max(my_mobility_data_cont.geometry.x)
    d_lat_km = geopy.distance.distance(
        (min_lat, min_lon), (max_lat, min_lon)
    ).kilometers
    d_lon_km = geopy.distance.distance(
        (min_lat, min_lon), (min_lat, max_lon)
    ).kilometers

    binsize = [int(d_lat_km * FACTOR_BINSIZE), int(d_lon_km * FACTOR_BINSIZE)]

    fig, ax = plt.subplots(1)
    pop_places_matrix = ax.hist2d(
        my_mobility_data_cont.geometry.y,
        my_mobility_data_cont.geometry.x,
        bins=binsize,
        norm=mcolors.PowerNorm(0.1),
    )
    ax.set_title("Histogram lat/Lon, number of visists per bin")
    ax.set_ylabel("Longitude")
    ax.set_xlabel("Latitude")

    hotspots = np.sort(pop_places_matrix[0].flatten())[-N_BIGGEST_HOTSPOTS:]

    THRESHOLD_HISTO_DYN = np.min(hotspots)

    gdf_hotspots_polygons = []
    for i in range(0, pop_places_matrix[0].shape[0]):
        for j in range(0, pop_places_matrix[0].shape[1]):
            if pop_places_matrix[0][i][j] >= THRESHOLD_HISTO_DYN:
                lat1 = pop_places_matrix[1][i]
                lat2 = pop_places_matrix[1][i + 1]
                lon1 = pop_places_matrix[2][j]
                lon2 = pop_places_matrix[2][j + 1]

                circle = Point((lon1 + lon2) / 2, (lat1 + lat2) / 2).buffer(0.002)

                gdf_hotspots_polygons.append(
                    gpd.GeoDataFrame(
                        {"n_visits": pop_places_matrix[0][i][j]},
                        index=[0],
                        crs=crs,
                        geometry=[circle],
                    )
                )

    return gdf_hotspots_polygons


def polygons_contain_geometry(polygons, geometry):
    if not isinstance(polygons, list):
        raise "ERROR: We need lists of gdf containing polygons!"

    for idx, polygon in enumerate(polygons):
        is_inside = polygon.geometry.contains(geometry.geometry)[0]
        if is_inside:
            return is_inside, idx
    else:
        return False, -1


def trip_detector(my_mobility_data, gdf_hotspot_polygons):
    flag_start_track = False
    flag_left_start_polygon = None
    trips = []
    counter_general = 0

    for idx, row in my_mobility_data.iterrows():
        is_inside, inside_idx = polygons_contain_geometry(gdf_hotspot_polygons, row)

        if is_inside and not flag_start_track:
            flag_left_start_polygon = None
            flag_start_track = None
            idx_start = None
            flag_left_start_polygon = False
            flag_start_track = True
            idx_start = counter_general

        if not is_inside and not flag_left_start_polygon:
            flag_left_start_polygon = True
            idx_start = counter_general - 1

        if is_inside and flag_start_track and not flag_left_start_polygon:
            if row.speed_corr < 2:
                flag_start_track = False
                idx_end = counter_general

                trip = my_mobility_data.iloc[idx_start : idx_end + 1, :]

                if total_distance(trip) > MINIMUM_TRIP_LENGTH_KM:
                    trips.append(trip)

        counter_general += 1

    return trips
