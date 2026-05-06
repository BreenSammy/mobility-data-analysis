from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing, metrics
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import shapely
import pickle

import seaborn as sns

from sklearn.model_selection import cross_val_score
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


import numpy as np


current_directory = os.path.dirname(os.path.abspath(__file__))
functions_directory = "functions"
full_path = os.path.join(current_directory, functions_directory)
sys.path.append(full_path)


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

# LABEL_MAP = {
#     0: "standing",
#     1: "standing",
#     2: "standing",
#     3: "standing",
#     4: "walking",
#     5: "walking",
#     6: "running",
#     7: "bike",
#     8: "car",
#     9: "car",
#     10: "car",
#     11: "car",
#     12: "car",
#     13: "car",
#     14: "train",
#     15: "train",
#     16: "train",
#     17: "train",
# }


def encode_labels(df, label_column="label"):
    # Apply label map to label column
    df[label_column] = df[label_column].apply(lambda x: LABEL_MAP[x])
    le = preprocessing.LabelEncoder()
    y = df[label_column]
    le.fit(y)
    df["label_encoded"] = le.transform(y)
    return le


def get_features_and_labels(df, features):
    X = df.loc[:, features]
    y = df["label_encoded"]
    return X, y


def create_train_test_sets(df, features, test_size=0.4, random_state=4):
    # Delete all rows that have NaN values in feature columns
    df = df.dropna(subset=features)
    # Slice X and y from dataframe
    X, y = get_features_and_labels(df, features)
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test


def k_nearest_neighbor(X, y, n_neighbors=3):
    knn = KNeighborsClassifier(n_neighbors, p=2)
    knn.fit(X, y)
    return knn


def post_process_predictions(predictions):
    # Apply rolling median onto predictions to remove outliers
    predictions["pred"] = predictions["pred"].rolling(13, min_periods=1).median()
    predictions["pred"] = predictions["pred"].apply(lambda x: round(x))
    return predictions


def point_classification():

    # Load data
    # first user
    df1 = pd.read_csv("df1_new.csv", parse_dates=["timestamp"])
    df1 = df1.set_index("timestamp")
    df1["geometry"] = df1["geometry"].apply(lambda x: shapely.wkt.loads(x))
    df1["user"] = 1
    gdf1 = gpd.GeoDataFrame(df1, geometry="geometry")

    # second user
    df2 = pd.read_csv("df2_new.csv", parse_dates=["timestamp"])
    df2 = df2.set_index("timestamp")
    df2["geometry"] = df2["geometry"].apply(lambda x: shapely.wkt.loads(x))
    df2["user"] = 2
    gdf2 = gpd.GeoDataFrame(df2, geometry="geometry")

    # combine dataframes
    gdf = pd.concat([gdf1, gdf2])
    # gdf = gdf1

    # # Filter for only rows that are labeled
    gdf = gdf[gdf["label"].notnull()]
    encode_labels(gdf)

    # Use these features for the classifier dataset
    features = [
        # "altitude_x",
        # "latitude",
        # "longitude",
        "speed_ma",
        # "acc_down_ma",
        "acc_forw_ma",
        "acc_down_shift_ma",
        "trip_speed",
        "trip_duration",
    ]
    gdf = gdf.dropna(subset=features)
    X, y = get_features_and_labels(gdf, features)

    X_train, y_train = get_features_and_labels(gdf.loc[gdf["user"] == 1], features)
    X_test, y_test = get_features_and_labels(gdf.loc[gdf["user"] == 2], features)

    # X_train, X_test, y_train, y_test = create_train_test_sets(
    # gdf.loc[gdf["user"] == 1], features, test_size=0.4)

    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.fit_transform(X_test)
    # Only for plotting
    X = scaler.fit_transform(X)
    normalized_feature_df = pd.DataFrame(data=X, columns=features)
    normalized_feature_df["label"] = gdf["label"].values

    knn = k_nearest_neighbor(X_train, y_train, n_neighbors=3)

    k_pred = knn.predict(X_test)
    # X_test = pd.DataFrame(X_test)
    # X_test["pred"] = k_pred
    # X_test["y"] = y_test
    # X_test.sort_index(inplace=True)
    # X_test = post_process_predictions(X_test)

    print("Without post processing: {}".format(metrics.accuracy_score(y_test, k_pred)))
    # print(
    #     "With post processing: {}".format(
    #         metrics.accuracy_score(X_test["y"], X_test["pred"])
    #     )
    # )

    sns.FacetGrid(normalized_feature_df, hue="label", height=6).map(
        plt.scatter, "trip_duration", "speed_ma"
    ).add_legend()

    plt.show()

    # saving model to pickle file to submit the model
    pickle.dump(knn, open("knn_model", "wb"))


def get_trip_dataset(files):
    dfs = []
    for filename in files:
        # for filename in files:
        df = pd.read_csv(os.path.join("trips", filename))
        dfs.append(df)

    # combine dataframes
    df = pd.concat(dfs)
    df = df.dropna(subset=["label"])
    df = df[(df["max_speed"] >= 0.01)]

    le = encode_labels(df)
    # Filter classes we do not want to classify, e.g. standing is not a trip
    df = df[~df["label"].isin(["standing", "running"])]

    return df, le


def get_detected_trips_dataset():
    return get_trip_dataset(["trips_user1.csv", "trips_user2.csv"])


def get_trips_from_data_dataset():
    return get_trip_dataset(["trips_from_data_user1.csv", "trips_from_data_user2.csv"])


def analyze_trip_dataset(df):
    print("Amount trips: {}".format(df.shape[0]))
    print("Trips per class:")
    print(df["label"].value_counts())


def reduce_walking_trips(df):
    # Reduce the amount of walking samples
    df_walking = df[df["label"] == "walking"]
    df = df[df["label"] != "walking"]
    df_walking = df_walking.iloc[::3, :]
    df = pd.concat([df, df_walking])


def plot_prediction_results(le, y_test, k_pred):
    decoded_labels = le.inverse_transform(y_test)

    pos_dict = {}
    neg_dict = {}
    amount_dict = {}
    for class_el in list(set(decoded_labels)):
        pos_dict[class_el] = 0
        neg_dict[class_el] = 0
        amount_dict[class_el] = 0

    for i in range(0, len(decoded_labels)):
        amount_dict[decoded_labels[i]] += 1
        if y_test.values[i] == k_pred[i]:
            pos_dict[decoded_labels[i]] += 1
        else:
            neg_dict[decoded_labels[i]] += 1

    pos_arr = np.empty(1)
    neg_arr = np.empty(1)
    categories = np.empty(1)
    for cat in amount_dict:
        pos_arr = np.append(pos_arr, pos_dict[cat])
        neg_arr = np.append(neg_arr, neg_dict[cat])
        categories = np.append(categories, cat)

    pos_arr = np.delete(pos_arr, 0)
    neg_arr = np.delete(neg_arr, 0)
    categories = np.delete(categories, 0)

    plt.bar(categories, neg_arr, color="r", label="correct")
    plt.bar(categories, pos_arr, bottom=neg_arr, color="g", label="false")
    plt.legend()
    plt.show()


def plot_decision_boundary(knn, X, y, X_test, features, le):

    _, ax = plt.subplots(figsize=(12, 5))

    disp = DecisionBoundaryDisplay.from_estimator(
        knn,
        X_test,
        response_method="predict",
        plot_method="pcolormesh",
        xlabel=features[0],
        ylabel=features[1],
        shading="auto",
        alpha=0.5,
        ax=ax,
    )

    scatter = ax.scatter(X[:, 0], X[:, 1], c=y, edgecolors="k")
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)

    handles, labels = scatter.legend_elements(fmt="{x}")
    labels = [int(float(label)) for label in labels]
    ax.legend(handles, le.inverse_transform(labels), loc="upper right", title="Classes")

    plt.show()


def plot_confusion_matrix(y_test, k_pred, le):
    cm = confusion_matrix(y_test, k_pred, normalize="true", labels=y_test.unique())

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm, display_labels=le.inverse_transform(y_test.unique())
    )
    disp.plot()
    plt.show()


def trip_classification():

    # df, le = get_detected_trips_dataset()
    df, le = get_trips_from_data_dataset()
    print(df["label"].unique())
    # reduce_walking_trips(df)

    analyze_trip_dataset(df)
    # Use these features for the classifier dataset
    features = [
        "median_speed",
        # "avg_speed",
        "std_speed",
        # "max_speed",
        # "min_acc_forw",
        "std_acc_forw",
        # "median_acc_forw",
        "std_acc_down",
        # "median_acc_down",
        # "avg_acc_down",
        # "avg_acc_forw",
        # "max_acc_forw",
        # "max_acc_down",
        # "duration",
        # "distance"
    ]

    X = df.loc[:, features]
    y = df["label_encoded"]
    # Normalize features
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)
    # Create a df with the normalized data again, used for plotting
    normalized_feature_df = pd.DataFrame(data=X, columns=features)
    normalized_feature_df["label"] = df["label"].values
    best_accuracy = 0

    scores = []
    for k in range(1, 10):
        cv_scores = cross_val_score(
            KNeighborsClassifier(n_neighbors=k, p=2), X, y, cv=5
        )
        # print each cv score (accuracy) and average them
        print("current k for knn: ", k)
        print(cv_scores)
        print("cv_scores mean: {}\n".format(np.mean(cv_scores)))
        scores.append(np.mean(cv_scores))
        if np.mean(cv_scores) > best_accuracy:
            best_accuracy = np.mean(cv_scores)
            best_k = k

    plt.plot(list(range(1, 10)), scores)
    plt.xlabel("k")
    plt.ylabel("Cross Validation Genauigkeit")
    plt.show()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.4, random_state=4
    )
    knn = k_nearest_neighbor(X_train, y_train, n_neighbors=best_k)
    k_pred = knn.predict(X_test)

    print("best k:", best_k)
    print("Without post processing: {}".format(metrics.accuracy_score(y_test, k_pred)))

    # plot_prediction_results(le, y_test, k_pred)

    # Decision boundary only works when using two features
    # plot_decision_boundary(knn, X, y, X_test, features, le)

    # sns.FacetGrid(normalized_feature_df, hue="label", height=6).map(
    #     plt.scatter, "std_acc_forw", "std_acc_down"
    # ).add_legend()

    plot_confusion_matrix(y_test, k_pred, le)

    sns.pairplot(normalized_feature_df, hue="label", height=3)
    # plt.show()

    # # saving model to pickle file to submit the model
    # pickle.dump(knn, open("knn_model", 'wb'))


if __name__ == "__main__":
    print("Trip classification")
    trip_classification()
    # print("Point classification")
    # point_classification()
