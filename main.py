import sys
import os
import os.path as osp
import pickle

current_directory = os.path.dirname(os.path.abspath(__file__))
functions_directory = "functions"
full_path = os.path.join(current_directory, functions_directory)
sys.path.append(full_path)
full_path = os.path.join(current_directory, "trips")
sys.path.append(full_path)

from src.preprocessing import preprocess
from visualize import plotrouteperday, plot_acc_lin, folium_plot, visual_gdf
from trip_detect import get_popular_places, trip_detector
from create_trips import trip_creation_data, trip_creation_data_from_given
from classification import trip_classification, point_classification


user_gdfs = [osp.join("gdf1.pkl"), osp.join("gdf2.pkl")]

if not all([osp.isfile(file_path) for file_path in user_gdfs]):
    gdf_1 = preprocess(
        osp.join("data", "user1.pkl"), osp.join("data", "trip_times_user_1.csv")
    )
    gdf_2 = preprocess(
        osp.join("data", "user2.pkl"), osp.join("data", "trip_times_user_2.csv")
    )

    with open("gdf1.pkl", "wb") as f:
        pickle.dump(gdf_1, f)
    with open("gdf2.pkl", "wb") as f:
        pickle.dump(gdf_2, f)

else:
    with open("gdf1.pkl", "rb") as f:
        gdf_1 = pickle.load(f)
    with open("gdf2.pkl", "rb") as f:
        gdf_2 = pickle.load(f)

# plotrouteperday(gdf_1, "user1")
# plotrouteperday(gdf_2, "user2")

# # gdf_1_matched = mapmatch(gdf_1)
# # with open("gdf1_matched.pkl", "wb") as f:
# #     pickle.dump(gdf_1, f)

# plot_acc_lin(gdf_1, "Dataframe_1")
# plot_acc_lin(gdf_2, "Dataframe_2")

# # # create polygons 1
# gdf_hotspots_polygons_1 = get_popular_places(gdf_1)
# gdf_hotspots_polygons_2 = get_popular_places(gdf_2)

# # generate trips
# trips_1 = trip_detector(gdf_1, gdf_hotspots_polygons_1)
# trips_2 = trip_detector(gdf_2, gdf_hotspots_polygons_2)

# trip_creation_data_from_given()

# # Visualisierung einer Variablen
# visual_gdf(gdf_2["acc_down_ma"])

print("\npoint classification...\n")
point_classification()

print("\n\n")
print("\ntrip classification...\n")
trip_classification()
