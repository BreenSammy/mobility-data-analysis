import folium
import streamlit as st


def create_map(center_start: list[float], zoom_start: int) -> folium.Map:
    if "center" not in st.session_state:
        st.session_state["center"] = center_start

    if "zoom" not in st.session_state:
        st.session_state["zoom"] = zoom_start

    return folium.Map(location=center_start, zoom_start=zoom_start)
