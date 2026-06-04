from datetime import datetime
import zipfile

import matplotlib

import streamlit as st
import pandas as pd
from src.data_manager import UserDataManager
from pathlib import Path
import folium
from streamlit_folium import st_folium
import numpy as np
import matplotlib.pyplot as plt

from os import path
import urllib.request

if path.exists("data/processed.zip"):
    pass
else:
    with st.spinner("Please wait while we are downloading the dataset."):
        urllib.request.urlretrieve(
            "https://github.com/BreenSammy/mobility-data-analysis/releases/download/data/processed.zip", "data/processed.zip"
        )
        with zipfile.ZipFile("data/processed.zip", 'r') as zip_ref:
            zip_ref.extractall("data")
    st.success("Dataset has been downloaded !")


st.title("Mobility Data Analysis")

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

raw_data_page = st.Page("raw_data.py", title="Raw data", icon=":material/data_array:")
trips_page = st.Page("trips.py", title="Trips", icon=":material/trip:")
ml_page = st.Page("ml.py", title="ML", icon=":material/experiment:")

pg = st.navigation([raw_data_page, trips_page, ml_page])
st.set_page_config(
    page_title="Mobility Data Analysis", page_icon=":material/pin_road:", layout="wide"
)
pg.run()
# st.sidebar.success("")
