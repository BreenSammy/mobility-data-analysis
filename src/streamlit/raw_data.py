from datetime import datetime

import matplotlib

import streamlit as st
import pandas as pd
from src.data_manager import UserDataManager
from src.preprocessor import readinuser
from pathlib import Path
import folium
from streamlit_folium import st_folium
import numpy as np
import matplotlib.pyplot as plt


st.title("Raw data")

choice = st.selectbox("Choose user", ["User1", "User2"])


data_manager = UserDataManager(
    user_id=choice,
    raw_data_dir=Path("data") / "raw",
    processed_data_dir=Path("data") / "processed",
    results_dir=Path("results"),
)


paths = data_manager.get_day_paths()
dates = [datetime.strptime(path.name, "%d%m%y").strftime("%Y-%m-%d") for path in paths]

selected_date = st.selectbox("Choose date", dates)

st.write("Available days: {}".format(dates))

columns = [
    "latitude",
    "longitude",
    "altitude_x",
    "acc_x",
    "acc_y",
    "acc_z",
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "mag_x",
    "mag_y",
    "mag_z",
    "or_w",
    "or_x",
    "or_y",
    "or_z",
    "grav_x",
    "grav_y",
    "grav_z",
    "lin_acc_x",
    "lin_acc_y",
    "lin_acc_z",
    "press_hPa",
    "altitude_y",
    # "label",
    "distance",
    "speed_gps",
    "acc_gps",
    # "speed_corr",
    # "speed_ma",
    "acc_down",
    "acc_forw",
    "acc_down_ma",
    "acc_forw_ma",
    "acc_down_shift_ma",
]

df = pd.read_pickle(data_manager.processed_data_dir / "data_preprocessed.pickle")

df = df[columns]

# Filter by selected date
selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
df_filtered = df[df.index.date == selected_date_obj]

df_downsampled = (
    df_filtered.sample(frac=0.001, random_state=1)
    if len(df_filtered) > 0
    else df_filtered
)

st.write(df)

st.write(df.columns)

st.line_chart(
    data=df_downsampled,
    y=["acc_x", "acc_y", "acc_z"],
)
