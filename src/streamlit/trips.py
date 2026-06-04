import numpy as np
import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
import matplotlib.colors
import seaborn as sns
from pathlib import Path
from geopy.geocoders import Nominatim

from streamlit_folium import st_folium

from src.streamlit.components.create_map import create_map
from src.streamlit.components.select_user import select_user
from src.trips.trip_detect import get_popular_places, trip_detector
from src.data_manager import UserDataManager


@st.cache_data
def get_mobility_data(path: Path) -> pd.DataFrame:
    df = pd.read_pickle(path)
    # Downsample the data to 2% of the original size for better performance in Streamlit
    df = df.iloc[::50, :]
    return df


@st.cache_data
def cached_get_popular_places(_df, n_biggest_hotspots, user: str):
    return get_popular_places(_df, n_biggest_hotspots)


@st.cache_data
def cached_trip_detector(_df, _popular_places, user: str):
    return trip_detector(_df, _popular_places)


data_manager: UserDataManager = select_user()
df = get_mobility_data(data_manager.get_preprocessed_data_path())

trajectory = np.array(list(zip(df["geometry"].y, df["geometry"].x)))

center_start = np.mean(trajectory, axis=0).tolist()
ZOOM_START = 8
m = create_map(center_start, ZOOM_START)


folium_trajectory = folium.PolyLine(
    trajectory, weight=4.5, opacity=1, tooltip="Trip Path"
)
m.add_child(folium_trajectory)

st_folium(
    m,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="trajectory",
    width="100%",
)

st.markdown("""
    ### Understanding User Movement Patterns

    Analyzing raw GPS traces gives us location points, but doesn't tell us *when* trips occurred. 
    To extract meaningful trips, we need to identify when a user is stationary versus traveling. 
    Our algorithm combines hotspot detection with trip segmentation to automatically identify journeys.

    ### How It Works

    **Step 1: Identify Popular Places (Hotspots)**
    We start by detecting where the user spends significant time. Using spatial density clustering, 
    we divide the geographic area into a grid and count location points per cell. Cells with high 
    point density become "hotspots". Hotspots can be interpreted as meaningful locations like home, 
    work, or frequently visited places and serve as start and end points for trips.

    **Step 2: Track State Transitions**
    The algorithm tracks when the user enters and exits hotspots:
    - **Enters a hotspot**: Trip may be starting (user arriving at a destination)
    - **Leaves a hotspot**: Trip is starting (user departing from a location)
    - **Low speed in hotspot**: Trip ends (user has arrived and stopped moving)

    **Step 3: Segment into Trips**
    Once a trip begins (user leaves a hotspot), the algorithm records all movement until:
    - The user enters another hotspot AND
    - The speed drops below 2 km/h (indicating arrival)

    Only segments longer than the minimum trip length (100 meters) are kept.

    **Step 4: Extract Trip Statistics**
    Each detected trip now contains:
    - Start location and time
    - End location and time  
    - Distance traveled
    - Full trajectory of GPS points

""")

st.markdown("""
    ### Visualizing Detected Hotspots and Trips
    Let's visualize the detected hotspots and trips on the map. You can adjust the number of hotspots to see how it affects trip detection. """)

n_hotspots = st.slider("How many hotspots?", 1, 100, 30)

# Get data needed for plots
# Use the user ID as part of the cache key to ensure that different users get their own cached results
popular_places = cached_get_popular_places(
    df, n_biggest_hotspots=n_hotspots, user=data_manager.user_id
)
trips = cached_trip_detector(df, popular_places, user=data_manager.user_id)

m_with_popular_places = create_map(center_start, ZOOM_START)

fg_popular_places = folium.FeatureGroup(name="popular-places")
for idx, gdf_poly in enumerate(popular_places):
    n_visits = int(gdf_poly["n_visits"][0])
    tooltip = "Nr: {}. Visits: {}".format(idx, n_visits)

    # Get centroid of the polygon
    centroid = gdf_poly.geometry.centroid[0]

    folium.Circle(
        location=[centroid.y, centroid.x],
        radius=100,
        popup=tooltip,
        tooltip=tooltip,
        color="#ff7f0e",
        fill=True,
        fillColor="#ff7f0e",
        fillOpacity=0.3,
    ).add_to(fg_popular_places)

# Create markers for top 3 popular places
df_popular_places_all = gpd.GeoDataFrame(
    {
        "geometry": [gdf_poly.geometry[0].centroid for gdf_poly in popular_places],
        "n_visits": [gdf_poly["n_visits"][0] for gdf_poly in popular_places],
    }
)
df_top_3 = df_popular_places_all.sort_values("n_visits", ascending=False).head(3)


# Reverse geocode to get addresses
@st.cache_data
def get_addresses(coordinates):
    geocoder = Nominatim(user_agent="mobility_analysis")
    addresses = []
    for lat, lon in coordinates:
        try:
            location = geocoder.reverse(f"{lat}, {lon}")
            addresses.append(location.address)
        except:
            addresses.append("Address not found")
    return addresses


# Get addresses for top 3
coordinates = [(row.geometry.y, row.geometry.x) for _, row in df_top_3.iterrows()]
addresses = get_addresses(coordinates)

# # Format dataframe for display with addresses
df_display = pd.DataFrame(
    {
        "Location": df_top_3["geometry"].apply(lambda x: f"({x.y:.4f}, {x.x:.4f})"),
        "Visits": df_top_3["n_visits"].astype(int),
        "Address": addresses,
    }
)

fg_top_3_markers = folium.FeatureGroup(name="top-3-hotspots")
for idx, ((_, row), address) in enumerate(zip(df_top_3.iterrows(), addresses), 1):
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=f"Top {idx}: {int(row['n_visits'])} visits<br>{address}",
        tooltip=f"Top {idx}: {address}",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(fg_top_3_markers)

m_with_popular_places.add_child(folium_trajectory)
m_with_popular_places.add_child(fg_top_3_markers)

st_folium(
    m_with_popular_places,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="popular_places",
    feature_group_to_add=fg_popular_places,
    width="100%",
)


st.markdown("""
    The orange circles represent the detected hotspots, with the size indicating the number of visits.
    
    The table below shows the most visited detected hotspots with their visit counts and approximate addresses. 
    These locations might be significant places in the user's life, such as home, work, or favorite hangouts.
""")

st.dataframe(df_display, hide_index=True)

st.markdown("""    
    With the hotspots identified, we can now detect trips based on the user's movement between these hotspots. 
    The next section will show you how many trips were detected and visualize them on the map.
""")

st.write("Total number of trips detected: {}".format(len(trips)))

m_with_trips = create_map(center_start, ZOOM_START)

fg_trips = folium.FeatureGroup(name="trips")

# Create colormap for trips
if len(trips) > 0:
    colors = sns.color_palette("Paired", len(trips))

    for idx, trip in enumerate(trips):
        tooltip = "Trip {}: {} to {}".format(
            idx + 1,
            trip.index[0].strftime("%Y-%m-%d %H:%M"),
            trip.index[-1].strftime("%Y-%m-%d %H:%M"),
        )
        trajectory = np.array(list(zip(trip["geometry"].y, trip["geometry"].x)))
        # Get color from colormap for this trip
        color = matplotlib.colors.to_hex(colors[idx])
        folium.PolyLine(
            trajectory, weight=4.5, opacity=1, tooltip=tooltip, color=color
        ).add_to(fg_trips)

st_folium(
    m_with_trips,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="trips",
    feature_group_to_add=[fg_trips, fg_popular_places],
    width="100%",
)
