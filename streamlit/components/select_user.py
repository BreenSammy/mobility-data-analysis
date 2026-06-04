from pathlib import Path

import streamlit as st
from src.data_manager import UserDataManager


def select_user():
    choice = st.selectbox("Choose user", ["User1", "User2"])

    return UserDataManager(
        user_id=choice,
        raw_data_dir=Path("data") / "raw",
        processed_data_dir=Path("data") / "processed",
        results_dir=Path("results"),
    )
