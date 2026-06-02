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

st.title("Mobility Data Analysis")


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

raw_data_page = st.Page("raw_data.py", title="Raw data", icon=":material/add_circle:")
delete_page = st.Page("delete.py", title="Delete entry", icon=":material/delete:")

pg = st.navigation([raw_data_page, delete_page])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()
# st.sidebar.success("")
