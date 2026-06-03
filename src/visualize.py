import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import LineString
import folium
import os
import numpy as np
from pathlib import Path


from src.trip_detect import get_popular_places, trip_detector


def create_plots(gdf, path: Path):

    m = folium_plot()
    m.add_to_folium(gdf)
    m.show_map()
    m.save_map(path / "gdf_total.html")

    gdf_hotspots_polygons = get_popular_places(gdf)

    # plot polygons_1
    m = folium_plot()
    m.add_to_folium(gdf)

    for idx, gdf_poly in enumerate(gdf_hotspots_polygons):
        tooltip = "Nr: {}. n_visits: {}".format(idx, gdf_poly["n_visits"][0])
        m.add_geojson_to_folium(gdf_poly.to_crs(epsg="4326").to_json(), tooltip)

    m.save_map(path / "polygons_gdf_1.html")
    m.show_map()

    # generate trips
    trips = trip_detector(gdf, gdf_hotspots_polygons)

    m = folium_plot()
    m.add_many_to_folium(trips)

    for idx, gdf_poly in enumerate(gdf_hotspots_polygons):
        tooltip = "Nr: {}. n_visits: {}".format(idx, gdf_poly["n_visits"][0])
        m.add_geojson_to_folium(gdf_poly, tooltip)

    m.save_map(path / "trips.html")
    m.show_map()


def plotrouteperday(gdf: pd.DataFrame, folder):
    for day in list(gdf["date"].unique()):
        gdf_data = gdf[gdf.date == day]

        route = LineString(gdf_data["geometry"])

        centroid = route.centroid

        m = folium.Map(location=[centroid.x, centroid.y], zoom_start=12)
        coords = list(route.coords)
        folium.PolyLine(locations=coords, color="blue", weight=2.5, opacity=0.8).add_to(
            m
        )

        m.save(os.path.join(folder, str(day) + ".html"))

        # fig = plt.figure()
        # plt.plot(*route.xy)
        # mplleaflet.display(fig=fig)


# allgemeine Visualisierung einer Variable eines GDF
def visual_gdf(gdf_var):
    fig, ax = plt.subplots(1)
    ax.plot(gdf_var, marker="*", linestyle="None")
    ax.set_xlabel("time")
    plt.show()


def plot_acc_lin(gdf, title=""):
    plt.figure()
    plt.plot(gdf.lin_acc_x, label="X")
    plt.plot(gdf.lin_acc_y, label="Y")
    plt.plot(gdf.lin_acc_z, label="Z")

    plt.legend()
    plt.title(title)
    plt.xlabel("Acceleration in m/s^2")
    plt.ylabel("Data and Time")
    plt.grid()
    plt.show()


class folium_plot:
    def __init__(self, **kwargs):

        self.width = kwargs.get("width", "100%")
        self.height = kwargs.get("height", "600")
        self.location = kwargs.get(
            "location",
        )
        self.f = folium.Figure(width=self.width, height=self.height)
        self.m = folium.Map(location=self.location, zoom_start=11).add_to(self.f)

        self.color_map = [
            "red",
            "blue",
            "green",
            "purple",
            "orange",
            "darkred",
            "darkblue",
            "darkgreen",
            "cadetblue",
            "pink",
            "lightblue",
            "lightgreen",
            "gray",
            "lightgray",
        ]

    def add_to_folium(self, my_mobility_data, color="red", tooltip=""):

        data2 = np.array(
            list(zip(my_mobility_data["geometry"].y, my_mobility_data["geometry"].x))
        )
        folium.PolyLine(
            data2, color=color, weight=4.5, opacity=1, tooltip=tooltip
        ).add_to(self.m)
        return self.m

    def add_many_to_folium(self, my_mobility_data_list):
        for idx, my_mobility_data in enumerate(my_mobility_data_list):
            self.add_to_folium(
                my_mobility_data,
                color=self.color_map[idx % len(self.color_map)],
                tooltip=idx,
            )

    def add_geojson_to_folium(self, gdf_poly, tooltip=""):
        folium.GeoJson(gdf_poly, tooltip=tooltip).add_to(self.m)

    def add_marker_to_folium(self, lat, lon, popup=""):
        folium.Marker([lon, lat], popup=popup).add_to(self.m)

    def save_map(self, path_name):
        self.m.save(os.path.join(path_name))

    def show_map(self):
        return self.f
