import sys
import os
import pickle
import geopandas as gpd

current_directory = os.path.dirname(os.path.abspath(__file__))
functions_directory = "functions"
full_path = os.path.join(current_directory, functions_directory)
sys.path.append(full_path)

from preprocessing import preprocess, mapmatch, filtering
from visualize import plotrouteperday, plot_acc_lin, folium_plot
from trip_detect import get_popular_places, trip_detector

with open("gdf1.pkl", "rb") as f:
    gdf_1 = pickle.load(f)
with open("gdf2.pkl", "rb") as f:
    gdf_2 = pickle.load(f)


m = folium_plot()
m.add_to_folium(gdf_1)
m.show_map()
m.save_map("gdf_1_total.html")

m = folium_plot()
m.add_to_folium(gdf_2)
m.show_map()
m.save_map("gdf_2_total.html")

# create polygons 1
gdf_hotspots_polygons_1 = None
gdf_hotspots_polygons_1 = get_popular_places(gdf_1)

# plot polygons_1
m2 = folium_plot()
m2.add_to_folium(gdf_1)

for idx, gdf_poly in enumerate(gdf_hotspots_polygons_1):
    tooltip = "Nr: {}. n_visits: {}".format(idx, gdf_poly["n_visits"][0])
    m2.add_geojson_to_folium(gdf_poly.to_crs(epsg="4326").to_json(), tooltip)

m2.save_map("polygons_gdf_1.html")
m2.show_map()

# create polygons 2
gdf_hotspots_polygons_2 = None
gdf_hotspots_polygons_2 = get_popular_places(gdf_2)

# plot polygons 2
m2 = folium_plot()
m2.add_to_folium(gdf_2)

for idx, gdf_poly in enumerate(gdf_hotspots_polygons_2):
    tooltip = "Nr: {}. n_visits: {}".format(idx, gdf_poly["n_visits"][0])
    m2.add_geojson_to_folium(gdf_poly.to_crs(epsg="4326").to_json(), tooltip)

m2.save_map("polygons_gdf_2.html")
m2.show_map()


# generate trips
trips_1 = None
trips_1 = trip_detector(gdf_1, gdf_hotspots_polygons_1)
trips_2 = None
trips_2 = trip_detector(gdf_2, gdf_hotspots_polygons_2)

# plot trip 1
m3 = folium_plot()
m3.add_many_to_folium(trips_1)

for idx, gdf_poly in enumerate(gdf_hotspots_polygons_1):
    tooltip = "Nr: {}. n_visits: {}".format(idx, gdf_poly["n_visits"][0])
    m3.add_geojson_to_folium(gdf_poly, tooltip)

m3.save_map(os.path.join("trips_1.html"))
m3.show_map()

# plot trip 2
m3 = folium_plot()
m3.add_many_to_folium(trips_2)

for idx, gdf_poly in enumerate(gdf_hotspots_polygons_2):
    tooltip = "Nr: {}. n_visits: {}".format(idx, gdf_poly["n_visits"][0])
    m3.add_geojson_to_folium(gdf_poly, tooltip)

m3.save_map(os.path.join("trips_2.html"))
m3.show_map()
