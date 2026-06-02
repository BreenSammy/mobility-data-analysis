from datetime import datetime

import matplotlib

import streamlit as st
import pandas as pd
from src.data_manager import UserDataManager
from pathlib import Path
import folium
from streamlit_folium import st_folium
import numpy as np
import matplotlib.pyplot as plt

st.write("Here's our first attempt at using data to create a table:")
base_data_dir = Path("data")
processed_data_dir = base_data_dir / "processed"
results_dir = Path("results")
users = ["User1", "User2"]

data_manager = UserDataManager(
    user_id="User1",
    raw_data_dir=base_data_dir / "raw",
    processed_data_dir=processed_data_dir,
    results_dir=results_dir,
)
# df = pd.read_csv(data_manager.raw_data_dir / 220617 / "labels_track_main.txt")
trips = pd.read_csv(data_manager.processed_data_dir / "trips_from_data.csv")
df = pd.read_pickle(data_manager.processed_data_dir / "data_preprocessed.pickle")
# st.write(df.index)
# st.write(type(df.index))
# st.write(df.index)
# st.write(df.index.dtype)
# st.write(isinstance(df.index, pd.DatetimeIndex))
st.write(trips)
# st.write(df)


# call to render Folium map in Streamlit
if st.button("Send balloons!"):
    st.balloons()

    import numpy as np
import pandas as pd
import streamlit as st


# @st.cache_data
# def get_profile_dataset(number_of_items: int = 20, seed: int = 0) -> pd.DataFrame:
#     new_data = []

#     np.random.seed(seed)

#     for i in range(number_of_items):
#         new_data.append(
#             {
#                 "name": "test",
#                 "daily_activity": np.random.rand(25),
#                 "activity": np.random.randint(2, 90, size=12),
#             }
#         )

#     profile_df = pd.DataFrame(new_data)
#     return profile_df


column_configuration = {
    "name": st.column_config.TextColumn(
        "Name", help="The name of the user", max_chars=100, width="medium"
    ),
    "activity": st.column_config.LineChartColumn(
        "Activity (1 year)",
        help="The user's activity over the last 1 year",
        width="large",
        y_min=0,
        y_max=100,
    ),
    "daily_activity": st.column_config.BarChartColumn(
        "Activity (daily)",
        help="The user's activity in the last 25 days",
        width="medium",
        y_min=0,
        y_max=1,
    ),
}

select, compare = st.tabs(["Select members", "Compare selected"])

st.header("All members")

# df = get_profile_dataset()

event = st.dataframe(
    trips,
    # column_config=column_configuration,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
)

st.header("Selected members")
selected_trips = event.selection.rows
filtered_df = trips.iloc[selected_trips]
st.dataframe(
    filtered_df,
    column_config=column_configuration,
    use_container_width=True,
)

# center on Liberty Bell, add marker
CENTER_START = [51.2, 0.0]
ZOOM_START = 8
if "center" not in st.session_state:
    st.session_state["center"] = CENTER_START

if "zoom" not in st.session_state:
    st.session_state["zoom"] = ZOOM_START

m = folium.Map(location=CENTER_START, zoom_start=ZOOM_START)
fg = folium.FeatureGroup(name="trajectories")


# Create colormap for trajectories
n_trajectories = len(filtered_df)
cmap = plt.cm.get_cmap("tab20", n_trajectories)

for position, (idx, row) in enumerate(filtered_df.iterrows()):
    start_time, end_time = (
        datetime.strptime(row["start"], "%Y-%m-%d %H:%M:%S.%f"),
        datetime.strptime(row["end"], "%Y-%m-%d %H:%M:%S.%f"),
    )
    mask = (df.index >= start_time) & (df.index <= end_time)
    points_of_trip = df.loc[mask]
    df_downsampled = points_of_trip.iloc[::50, :]
    trajectory = np.array(
        list(zip(df_downsampled["geometry"].y, df_downsampled["geometry"].x))
    )
    # Get color from colormap for this trajectory
    color = matplotlib.colors.to_hex(cmap(position))
    fg.add_child(
        folium.PolyLine(
            trajectory, color=color, weight=4.5, opacity=1, tooltip="Trip Path"
        )
    )

st_folium(
    m,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="new",
    feature_group_to_add=fg,
    height=400,
    width=700,
)
# st_data = st_folium(m, width=725)


# activity_df = {}
# for person in people:
#     activity_df[df.iloc[person]["name"]] = df.iloc[person]["activity"]
# activity_df = pd.DataFrame(activity_df)

# daily_activity_df = {}
# for person in people:
#     daily_activity_df[df.iloc[person]["name"]] = df.iloc[person]["daily_activity"]
# daily_activity_df = pd.DataFrame(daily_activity_df)

# if len(people) > 0:
#     st.header("Daily activity comparison")
#     st.bar_chart(daily_activity_df)
#     st.header("Yearly activity comparison")
#     st.line_chart(activity_df)
# else:
#     st.markdown("No members selected.")
