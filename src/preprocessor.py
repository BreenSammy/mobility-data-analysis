from pathlib import Path
from typing import Optional
import logging

import os
import os.path as osp

import pandas as pd

from src.preprocessing import readinuser, preprocess


class Preprocessor:
    """Stateless preprocessing - no dependencies on file structure"""

    @staticmethod
    def load_user_data(day_paths: list[Path]) -> pd.DataFrame:
        data = []
        for day_path in day_paths:
            df_day = readinuser(str(day_path))
            data.append(df_day)

        df = pd.concat(data)
        df = df.drop(columns=["time_ms_x", "time_ms_y"])
        return df

    @staticmethod
    def preprocess(df: pd.DataFrame, trip_times_path: Path) -> pd.DataFrame:
        """Returns preprocessed GeoDataFrame"""
        return preprocess(df, str(trip_times_path))
