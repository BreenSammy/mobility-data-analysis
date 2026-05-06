import pandas as pd

df1 = pd.read_csv("trips/trips_from_data_user1.csv")
df2 = pd.read_csv("trips/trips_from_data_user2.csv")

print(df1.columns)

df2 = df2.drop(43)  # outlier

# print(df2[df2['label'] == 4])

LABEL_MAP = {
    0: "standing",
    1: "standing",
    2: "standing",
    3: "standing",
    4: "walking",
    5: "walking",
    6: "running",
    7: "bike",
    8: "car",
    9: "car",
    10: "bus",
    11: "bus",
    12: "bus",
    13: "bus",
    14: "train",
    15: "train",
    16: "train",
    17: "train",
}


def calculate_metadata(df):

    df["label"] = df["label"].apply(lambda x: LABEL_MAP[x])

    total_trips = df["label"].value_counts().reset_index()
    total_trips.columns = ["label", "total_trips"]

    distance = df.groupby("label")["distance"].sum().reset_index()
    distance["distance"] = distance["distance"] / 1000

    duration = df.groupby("label")["duration"].sum().reset_index()
    duration["duration"] = duration["duration"] / 60

    metadata_df = total_trips.merge(distance, on="label").merge(duration, on="label")

    metadata_df["avg_velocity"] = metadata_df["distance"] / metadata_df["duration"] * 60

    max_velocity = df.groupby("label")["max_speed"].max().reset_index()
    max_velocity.columns = ["label", "max_velocity"]
    metadata_df = metadata_df.merge(max_velocity, on="label")

    avg_acceleration = df.groupby("label").apply(
        lambda group: (
            (group["avg_acc_forw"] * group["duration"]).sum() / group["duration"].sum()
        )
    )
    avg_acceleration = avg_acceleration.reset_index()
    avg_acceleration.columns = ["label", "avg_acceleration"]
    metadata_df = metadata_df.merge(avg_acceleration, on="label")

    max_acceleration = df.groupby("label")["max_acc_forw"].max().reset_index()
    max_acceleration.columns = ["label", "max_acceleration"]
    metadata_df = metadata_df.merge(max_acceleration, on="label")

    metadata_df["avg_distance_per_track"] = (
        metadata_df["distance"] / metadata_df["total_trips"]
    )
    metadata_df["avg_duration_per_track"] = (
        metadata_df["duration"] / metadata_df["total_trips"]
    )

    custom_order = ["standing", "walking", "running", "bike", "car", "bus", "train"]

    metadata_df["label"] = pd.Categorical(
        metadata_df["label"], categories=custom_order, ordered=True
    )
    metadata_df = metadata_df.sort_values("label")
    metadata_df.reset_index(drop=True, inplace=True)

    return metadata_df


metadata_1 = calculate_metadata(df1)
metadata_2 = calculate_metadata(df2)

metadata_1.to_csv("metadata1.csv", index=False, encoding="utf8")
metadata_2.to_csv("metadata2.csv", index=False, encoding="utf8")
