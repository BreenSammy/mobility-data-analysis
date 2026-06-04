import folium
import streamlit as st

attr = (
    '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> '
    '&copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> '
    '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
)
tiles = f"https://tiles.stadiamaps.com/tiles/alidade_smooth/{{z}}/{{x}}/{{y}}{{r}}.png?api_key={st.secrets['STADIA_KEY']}"


def create_map(center_start: list[float], zoom_start: int) -> folium.Map:
    if "center" not in st.session_state:
        st.session_state["center"] = center_start

    if "zoom" not in st.session_state:
        st.session_state["zoom"] = zoom_start

    return folium.Map(
        location=center_start, zoom_start=zoom_start, attr=attr, tiles=tiles
    )
