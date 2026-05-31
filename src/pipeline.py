import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

from src.data_manager import UserDataManager
from src.preprocessor import Preprocessor
from src.trips.create_trips import create_trips, read_trip_times
from src.trips.get_trip_times_from_data import get_trip_times_from_data
from src.visualize import create_plots
from src.classifier import Classifier
from src.label_encoder import LabelEncoding


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

            self.logger.info("Data preprocessing complete, generating visualizations")
            create_plots(gdf, self.data_manager.results_dir / "visualizations")

            self.logger.info(f"Completed pipeline for {self.data_manager.user_id}")
            # return {"status": "SUCCESS", "features": features, "gdf": gdf}

        except Exception as e:
            self.logger.error(f"Failed: {e}")
            # return {"status": "ERROR", "error": str(e)}


class ClassificationPipeline:
    """Orchestrates classification training and prediction for multiple users"""

    def __init__(
        self,
        results_dir: Path,
        features: List[str],
        test_size: float = 0.3,
        classifier_type: str = "trip",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize classification pipeline

        Args:
            results_dir: Base results directory
            features: List of feature columns to use
            classifier_type: "trip" or "point"
            logger: Optional logger instance
        """
        self.results_dir = Path(results_dir)
        self.features = features
        self.test_size = test_size
        self.classifier_type = classifier_type.lower()
        self.logger = logger or logging.getLogger("ClassificationPipeline")

        self.label_encoder = LabelEncoding()

        self.classifier = Classifier(self.results_dir, self.logger)

    def train(
        self,
        user_ids: List[str],
        data_managers: Dict[str, UserDataManager],
        n_neighbors: int = 5,
        **kwargs,
    ) -> Dict:
        """
        Train classifier on data from multiple users

        Args:
            user_ids: List of user IDs
            data_managers: Dictionary mapping user_id to UserDataManager
            features: List of feature columns to use
            n_neighbors: Number of neighbors for KNN
            **kwargs: Additional arguments for training

        Returns:
            Dictionary with training results
        """
        self.logger.info(
            f"Training {self.classifier_type} classifier on {len(user_ids)} users"
        )

        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_training_data(
            user_ids, data_managers, test_size=self.test_size
        )

        results = self.classifier.train(
            X_train, X_test, y_train, y_test, n_neighbors=n_neighbors
        )

        plot_confusion_matrix(
            y_test, results["test_predictions"], self.label_encoder.encoder
        )

        self.logger.info(f"Training complete. Accuracy: {results['accuracy']:.4f}")
        return results

    def predict_all_users(
        self, user_ids: List[str], data_managers: Dict[str, UserDataManager]
    ) -> Dict[str, pd.DataFrame]:
        """
        Make predictions for all users

        Args:
            user_ids: List of user IDs
            data_managers: Dictionary mapping user_id to UserDataManager

        Returns:
            Dictionary mapping user_id to prediction dataframe
        """
        self.logger.info(f"Predicting for {len(user_ids)} users")

        predictions = {}
        for user_id in user_ids:
            try:
                self.logger.info(f"Predicting for {user_id}")
                data_manager = data_managers[user_id]
                # Load features
                features_df = self.load_data(user_id, data_manager)
                X = features_df[self.features].values

                y = self.classifier.predict(X)

                # Create results dataframe
                results_df = features_df.copy()
                results_df["predicted_class_encoded"] = y
                results_df["predicted_class"] = self.label_encoder.decode(y)

                predictions[user_id] = results_df

                # Save predictions
                output_path = (
                    self.results_dir
                    / user_id
                    / "predictions"
                    / f"{self.classifier_type}_classification.csv"
                )

                self.logger.info(f"Saved predictions to {output_path}")
                self.logger.info(f"✓ Predictions for {user_id}")
            except Exception as e:
                self.logger.error(f"✗ Failed to predict for {user_id}: {e}")

        return predictions

    def load_data(self, user_id: str, data_manager: UserDataManager) -> pd.DataFrame:
        """Load trip dataset for a user"""
        try:
            if self.classifier_type == "trip":
                path = data_manager.get_trips_from_data_path()
                df = pd.read_csv(path)
            elif self.classifier_type == "point":
                path = data_manager.get_preprocessed_data_path()
                df = pd.read_pickle(path)
            else:
                raise ValueError(f"Unknown classifier type: {self.classifier_type}")

            df = df.dropna(subset=self.features)
            return df
        except FileNotFoundError:
            self.logger.error(f"Trip data not found for {user_id}")
            return pd.DataFrame()

    def prepare_training_data(
        self,
        user_ids: List[str],
        data_managers: Dict[str, UserDataManager],
        test_size: float = 0.3,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Load and prepare training data from multiple users"""
        self.logger.info(f"Loading trip data for training from {len(user_ids)} users")

        all_dfs = []
        for user_id in user_ids:
            try:
                df = self.load_data(user_id, data_managers[user_id])
                if not df.empty:
                    df["user_id"] = user_id
                    all_dfs.append(df)
            except Exception as e:
                self.logger.error(f"Failed to load data for {user_id}: {e}")

        if not all_dfs:
            raise ValueError("No training data loaded")

        # Combine all data
        df_combined = pd.concat(all_dfs, ignore_index=True)

        df_combined = df_combined.dropna(subset=["label"])
        # df_combined = df_combined[(df_combined["max_speed"] >= 0.01)]

        # Encode labels
        df_combined = self.label_encoder.encode(df_combined)
        df_combined = df_combined.dropna(subset=["label_encoded"])

        # Extract features and labels
        X = df_combined.loc[:, self.features].values
        y = df_combined["label_encoded"].values

        self.logger.info(
            f"Loaded {len(df_combined)} samples with {len(self.features)} features"
        )

        # Split into train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        return X_train, X_test, y_train, y_test


def plot_confusion_matrix(y_test, y_pred, le):
    labels = np.unique(y_test)
    cm = confusion_matrix(y_test, y_pred, normalize="true", labels=labels)

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm, display_labels=le.inverse_transform(labels)
    )
    disp.plot()
    plt.show()
