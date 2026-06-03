import numpy as np
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from src.streamlit.components.select_user import select_user
from src.streamlit.components.create_map import create_map

data_manager = select_user()
trips = pd.read_csv(data_manager.get_trips_from_data_path())
df = pd.read_pickle(data_manager.get_preprocessed_data_path())

df = df.iloc[::50, :]
trajectory = np.array(list(zip(df["geometry"].y, df["geometry"].x)))

center_start = np.mean(trajectory, axis=0).tolist()
ZOOM_START = 8
m = create_map(center_start, ZOOM_START)
fg = folium.FeatureGroup(name="trajectories")

fg.add_child(folium.PolyLine(trajectory, weight=4.5, opacity=1, tooltip="Trip Path"))

st_folium(
    m,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="new",
    feature_group_to_add=fg,
    width="100%",
)

# st.write(df)

# event = st.dataframe(
#     trips,
#     # column_config=column_configuration,
#     use_container_width=True,
#     hide_index=True,
#     on_select="rerun",
#     selection_mode="multi-row",
# )

# selected_trips = event.selection.rows
# filtered_df = trips.iloc[selected_trips]
# st.dataframe(
#     filtered_df,
#     use_container_width=True,
# )

# Create colormap for trajectories
# n_trajectories = len(filtered_df)
# cmap = plt.cm.get_cmap("tab20", n_trajectories)

# for position, (idx, row) in enumerate(filtered_df.iterrows()):
#     start_time, end_time = (
#         datetime.strptime(row["start"], "%Y-%m-%d %H:%M:%S.%f"),
#         datetime.strptime(row["end"], "%Y-%m-%d %H:%M:%S.%f"),
#     )
#     mask = (trips.index >= start_time) & (trips.index <= end_time)
#     points_of_trip = trips.loc[mask]
#     df_downsampled = points_of_trip.iloc[::50, :]
#     trajectory = np.array(
#         list(zip(df_downsampled["geometry"].y, df_downsampled["geometry"].x))
#     )
#     # Get color from colormap for this trajectory
#     color = matplotlib.colors.to_hex(cmap(position))
#     # fg.add_child(
#     #     folium.PolyLine(
#     #         trajectory, color=color, weight=4.5, opacity=1, tooltip="Trip Path"
#     #     )
#     # )
