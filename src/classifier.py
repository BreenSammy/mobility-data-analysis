"""Classification module with data manager integration"""

from pathlib import Path
from typing import Optional, Tuple, List, Dict
import logging
import pickle

import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt


class KNNModel:
    """KNN classifier wrapper with model management"""

    def __init__(self, n_neighbors: int = 3, p: int = 2):
        self.n_neighbors = n_neighbors
        self.p = p
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_fitted = False

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "KNNModel":
        """Train KNN model"""
        X_scaled = self.scaler.fit_transform(X_train)
        self.model = KNeighborsClassifier(self.n_neighbors, p=self.p)
        self.model.fit(X_scaled, y_train)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def cross_validate(self, X: np.ndarray, y: np.ndarray, cv: int = 5) -> np.ndarray:
        """Perform cross-validation"""
        X_scaled = self.scaler.fit_transform(X)
        return cross_val_score(
            KNeighborsClassifier(self.n_neighbors, p=self.p), X_scaled, y, cv=cv
        )

    def save(self, path: Path):
        """Save model to disk"""
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "n_neighbors": self.n_neighbors,
            "p": self.p,
        }
        with open(path, "wb") as f:
            pickle.dump(model_data, f)

    @staticmethod
    def load(path: Path) -> "KNNModel":
        """Load model from disk"""
        with open(path, "rb") as f:
            model_data = pickle.load(f)

        knn = KNNModel(model_data["n_neighbors"], model_data["p"])
        knn.model = model_data["model"]
        knn.scaler = model_data["scaler"]
        knn.is_fitted = True
        return knn


class Classifier:
    """Classifies trips or points using KNN with multi-user training data"""

    def __init__(self, results_dir: Path, logger: Optional[logging.Logger] = None):
        self.results_dir = Path(results_dir)
        self.logger = logger or logging.getLogger("TripClassifier")

    def find_best_k(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        k_range: range = range(1, 10),
        cv: int = 5,
    ) -> int:
        """Find best k value using cross-validation"""
        self.logger.info(f"Finding best k using cross-validation (range: {k_range})")

        best_k = 3
        best_score = 0
        scores = []

        for k in k_range:
            model = KNNModel(n_neighbors=k)
            cv_scores = model.cross_validate(X_train, y_train, cv=cv)
            mean_score = np.mean(cv_scores)
            scores.append(mean_score)

            self.logger.debug(f"k={k}: score={mean_score:.4f}")

            if mean_score > best_score:
                best_score = mean_score
                best_k = k

        self.logger.info(f"Best k: {best_k} (score: {best_score:.4f})")

        # Plot results
        plt.figure(figsize=(10, 6))
        plt.plot(list(k_range), scores, marker="o")
        plt.xlabel("k")
        plt.ylabel("Cross-Validation Accuracy")
        plt.title("KNN Performance vs k")
        plt.grid(True)
        return best_k

    def train(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        n_neighbors: int = 5,
    ) -> Dict[str, float]:
        """Train classifier on multi-user data"""
        self.logger.info(f"Training Classifier with {n_neighbors} neighbors")

        # Train model
        self.model = KNNModel(n_neighbors=n_neighbors)
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        self.logger.info(f"Test Accuracy: {accuracy:.4f}")

        return {"accuracy": accuracy, "test_predictions": y_pred, "test_labels": y_test}

    def predict(self, X: np.ndarray) -> pd.DataFrame:
        """Predict for a single user"""
        if self.model is None:
            raise ValueError("Model not trained yet")

        # Make predictions
        y_pred = self.model.predict(X)

        return y_pred
