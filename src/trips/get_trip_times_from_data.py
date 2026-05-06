from datetime import datetime

import pandas as pd


def get_trip_times_from_data(filepath):
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
