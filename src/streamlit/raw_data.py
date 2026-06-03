from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd
from src.streamlit.components.select_user import select_user


st.title("Raw data")

data_manager = select_user()

paths: list[Path] = data_manager.get_day_paths()
dates: list[str] = [
    datetime.strptime(path.name, "%d%m%y").strftime("%Y-%m-%d") for path in paths
]

selected_date = st.selectbox("Choose date", dates)

options = {
    "Accelerometer": {"columns": ["acc_x", "acc_y", "acc_z"], "unit": "m/s²"},
    "Gyroscope": {"columns": ["gyro_x", "gyro_y", "gyro_z"], "unit": "rad/s"},
    "Magnetometer": {"columns": ["mag_x", "mag_y", "mag_z"], "unit": "μT"},
    "Orientation": {"columns": ["or_w", "or_x", "or_y", "or_z"], "unit": ""},
    "Gravity": {"columns": ["grav_x", "grav_y", "grav_z"], "unit": "m/s²"},
    "Linear Acceleration": {
        "columns": ["lin_acc_x", "lin_acc_y", "lin_acc_z"],
        "unit": "m/s²",
    },
    "Pressure": {"columns": ["press_hPa"], "unit": "hPa"},
    "Altitude": {"columns": ["altitude_x", "altitude_y"], "unit": "m"},
    "Latitude": {"columns": ["latitude"], "unit": "°"},
    "Longitude": {"columns": ["longitude"], "unit": "°"},
    "Acceleration": {"columns": ["acc_down", "acc_forw"], "unit": "m/s²"},
}

selected_sensor = st.selectbox("Choose sensor", list(options.keys()))

selected_columns = options.get(selected_sensor, []).get("columns", [])
unit = options.get(selected_sensor, []).get("unit", "")

df = pd.read_pickle(data_manager.processed_data_dir / "data_preprocessed.pickle")


# Filter by selected date
selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
df_filtered = df[df.index.date == selected_date_obj]

df_downsampled = (
    # Downsample the data to 1% of the original size for better performance in Streamlit
    df_filtered.sample(frac=0.01, random_state=1)
    if len(df_filtered) > 0
    else df_filtered
)

selected_df = df_downsampled[selected_columns]

plot, table = st.tabs(["Plot", "Table"])

with plot:
    st.line_chart(
        data=selected_df,
        y=selected_columns,
        x_label="Time",
        y_label=f"{selected_sensor} ({unit})",
    )

with table:
    st.write(selected_df)
