from pathlib import Path

import pandas as pd


class UserDataManager:
    """Manages file I/O and directory structure for a user"""

    def __init__(
        self,
        user_id: str,
        raw_data_dir: Path,
        processed_data_dir: Path,
        results_dir: Path,
    ):
        self.user_id = user_id
        self.raw_data_dir = raw_data_dir / user_id
        self.processed_data_dir = processed_data_dir / user_id
        self.results_dir = results_dir / user_id
        self._ensure_directories()

    def _ensure_directories(self):
        (self.processed_data_dir).mkdir(parents=True, exist_ok=True)

        for subdir in [
            "features",
            "visualizations",
            "predictions",
        ]:
            (self.results_dir / subdir).mkdir(parents=True, exist_ok=True)

    def get_output_path(self, category: str, filename: str) -> Path:
        return self.results_dir / category / filename

    def save_processed_data(self, df: pd.DataFrame):
        path = self.processed_data_dir / "data_preprocessed.pickle"
        df.to_pickle(path)
        return path

    def save_trip_times_from_data(self, trip_times: pd.DataFrame):
        path = self.processed_data_dir / "trip_times_from_data.csv"
        trip_times.to_csv(path, index=False)
        return path

    def save_trips_from_data(self, trips: pd.DataFrame):
        path = self.processed_data_dir / "trips_from_data.csv"
        trips.to_csv(path, index=False)
        return path

    def load_dataframe(self, category: str, filename: str) -> pd.DataFrame:
        path = self.get_output_path(category, filename)
        return pd.read_csv(path)

    def get_trip_times_path(self) -> Path:
        return self.raw_data_dir / "trip_times.csv"

    def get_day_paths(self) -> list[Path]:
        """Get all day directories for this user"""
        return sorted(
            [
                p
                for p in self.raw_data_dir.iterdir()
                if p.is_dir() and not p.name.startswith(".")
            ]
        )
