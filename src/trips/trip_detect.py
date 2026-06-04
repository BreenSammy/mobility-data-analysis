import geopandas as gpd
import numpy as np
from geopy.distance import distance
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
    my_mobility_data_cont: gpd.GeoDataFrame,
    n_biggest_hotspots=30,
    factor_binsize=8,
    crs="epsg:4326",
) -> list[gpd.GeoDataFrame]:
    """
    Identify geographic hotspots (popular places) from mobility data using spatial binning.

    This function performs spatial density clustering by dividing the geographic area into
    a grid and identifying the cells with the highest concentration of data points. The
    grid size is automatically calculated based on the geographic extent of the data.

    Parameters
    ----------
    my_mobility_data_cont : GeoDataFrame
        Input mobility data with Point geometries containing latitude (y) and longitude (x) columns.
    n_biggest_hotspots : int
        Number of hotspots to identify (default: 30). The threshold is set to the minimum
        visit count among the N biggest hotspot cells. Cells with visit counts above this threshold
        are considered hotspots.
    factor_binsize : int, optional
        Scaling factor for grid resolution (default: 8). Higher values create finer grids.
        The bin size is calculated as: distance_in_km * factor_binsize.
    crs : str, optional
        Coordinate reference system for output GeoDataFrames (default: "epsg:4326").

    Returns
    -------
    list of GeoDataFrame
        List of GeoDataFrames, each representing one hotspot. Each GeoDataFrame contains:
        - geometry: A circular polygon (Point buffered by 0.002 degrees) representing the hotspot location
        - n_visits: The number of data points in that grid cell
    """
    min_lat = min(my_mobility_data_cont.geometry.y)
    max_lat = max(my_mobility_data_cont.geometry.y)
    min_lon = min(my_mobility_data_cont.geometry.x)
    max_lon = max(my_mobility_data_cont.geometry.x)
    d_lat_km = distance((min_lat, min_lon), (max_lat, min_lon)).kilometers
    d_lon_km = distance((min_lat, min_lon), (min_lat, max_lon)).kilometers

    binsize = [int(d_lat_km * factor_binsize), int(d_lon_km * factor_binsize)]

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

    hotspots = np.sort(pop_places_matrix[0].flatten())[-n_biggest_hotspots:]

    THRESHOLD_HISTO_DYN = np.min(hotspots)

    gdf_hotspots_polygons: list[gpd.GeoDataFrame] = []
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


def trip_detector(
    my_mobility_data: gpd.GeoDataFrame,
    gdf_hotspot_polygons: list[gpd.GeoDataFrame],
    minimum_trip_length_km: float = 0.1,
    minimum_speed_kmh: float = 2.0,
) -> list[gpd.GeoDataFrame]:
    """
    Detect trips from mobility data using hotspot-based state machine.

    A trip is defined as a movement sequence that:
    1. Starts when the user leaves a hotspot
    2. Ends when the user enters a different hotspot with speed < 2 km/h (arrival)
    3. Is longer than the minimum trip length

    Parameters
    ----------
    my_mobility_data : GeoDataFrame
        Mobility data with index as timestamp and columns including geometry and speed_corr
    gdf_hotspot_polygons : list of GeoDataFrame
        List of hotspot polygons returned from get_popular_places()
    minimum_trip_length_km : float, optional
        Minimum length of a trip in kilometers, by default 0.1
    minimum_speed_kmh : float, optional
        Minimum speed for a trip to be considered valid in km/h, by default 2

    Returns
    -------
    list of GeoDataFrame
        List of trip dataframes, each containing the trajectory of one detected trip
    """
    flag_start_track = False
    flag_left_start_polygon = False
    trips: list[gpd.GeoDataFrame] = []
    idx_start = None

    for counter_general, (idx, row) in enumerate(my_mobility_data.iterrows()):
        is_inside, inside_idx = polygons_contain_geometry(gdf_hotspot_polygons, row)

        # State 1: Enter a hotspot while not tracking
        if is_inside and not flag_start_track:
            flag_start_track = True
            flag_left_start_polygon = False
            idx_start = counter_general

        # State 2: Leave the current hotspot
        elif not is_inside and flag_start_track and not flag_left_start_polygon:
            flag_left_start_polygon = True

        # State 3: Enter a hotspot while tracking with low speed (trip end)
        elif (
            is_inside
            and flag_start_track
            and flag_left_start_polygon
            and row.speed_corr < minimum_speed_kmh
        ):
            idx_end = counter_general
            trip = my_mobility_data.iloc[idx_start : idx_end + 1, :]

            if total_distance(trip) > minimum_trip_length_km:
                trips.append(trip)

            # Reset for next trip
            flag_start_track = False
            flag_left_start_polygon = False
            idx_start = None

    return trips
