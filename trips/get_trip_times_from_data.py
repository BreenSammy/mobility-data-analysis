import os
import sys
from datetime import datetime

import pandas as pd


def get_trip_times_from_data(path):
    filepath = os.path.join(path, "labels_track_main.txt")
    labels_df = pd.read_csv(
        filepath, sep=" ", header=None, names=["start", "end", "label"]
    )

    labels_df["start"] = labels_df["start"].apply(
        func=lambda x: datetime.utcfromtimestamp(x / 1000)
    )
    labels_df["end"] = labels_df["end"].apply(
        func=lambda x: datetime.utcfromtimestamp(x / 1000)
    )
    # filter out rows where start time is after the end time
    labels_df = labels_df[labels_df["start"] <= labels_df["end"]]

    return labels_df


if __name__ == "__main__":
    # current_directory = os.path.dirname(os.path.abspath(__file__))
    # functions_directory = "functions"
    # full_path = os.path.join(current_directory, functions_directory)
    # sys.path.append(full_path)

    folder = {
        "User1": ["220617", "260617", "270617"],
        "User2": ["140617", "140717", "180717"],
    }
    for user in folder.keys():
        user_trip_times = pd.DataFrame()
        for date in folder[user]:
            path = os.path.join(os.path.dirname(__file__), "..", "data", user, date)
            trip_times = get_trip_times_from_data(path)
            user_trip_times = pd.concat([user_trip_times, trip_times])

        user_trip_times.to_csv(
            "trips/trip_times_from_data_{}.csv".format(user), index=False
        )
