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
