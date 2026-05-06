import logging
import os

from src.data_manager import UserDataManager
from src.preprocessor import Preprocessor
from src.trips.create_trips import create_trips, read_trip_times
from src.trips.get_trip_times_from_data import get_trip_times_from_data
import pandas as pd


class UserProcessingPipeline:
    """Processes a single user - uses data manager and processors"""

    def __init__(
        self, data_manager: UserDataManager, logger=None, rerun_preprocessing=False
    ):
        self.data_manager = data_manager
        self.logger = logger or logging.getLogger(f"Pipeline.{data_manager.user_id}")
        self.rerun_preprocessing = rerun_preprocessing

    def run(self) -> dict:
        """Process single user and return results"""
        self.logger.info(f"Starting pipeline for {self.data_manager.user_id}")

        try:
            # Load data
            day_paths = self.data_manager.get_day_paths()
            df = Preprocessor.load_user_data(day_paths)

            # Preprocess
            gdf = Preprocessor.preprocess(df, self.data_manager.get_trip_times_path())
            self.data_manager.save_processed_data(gdf)

            user_trip_times = pd.DataFrame()
            for day_path in day_paths:
                path = day_path / "labels_track_main.txt"
                trip_times = get_trip_times_from_data(path)
                user_trip_times = pd.concat([user_trip_times, trip_times])

            path_trip_times = self.data_manager.save_trip_times_from_data(
                user_trip_times
            )
            # # Extract features
            # features = FeatureExtractor.extract_all_features(gdf)
            # self.data_manager.save_dataframe(
            #     features, "features", "extracted_features.csv"
            # )

            trip_times = read_trip_times(path_trip_times)
            trips = create_trips(gdf, trip_times)
            self.data_manager.save_trips_from_data(trips)

            self.logger.info(f"Completed pipeline for {self.data_manager.user_id}")
            # return {"status": "SUCCESS", "features": features, "gdf": gdf}

        except Exception as e:
            self.logger.error(f"Failed: {e}")
            # return {"status": "ERROR", "error": str(e)}
