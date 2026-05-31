from pathlib import Path
from typing import Optional, Dict
import pickle

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder as SkLabelEncoder

LABEL_MAP = {
    0: "standing",
    1: "standing",
    2: "standing",
    3: "standing",
    4: "walking",
    5: "walking",
    6: "running",
    7: "bike",
    8: "car",
    9: "car",
    10: "bus",
    11: "bus",
    12: "bus",
    13: "bus",
    14: "train",
    15: "train",
    16: "train",
    17: "train",
}


class LabelEncoding:
    """Handles label encoding and decoding"""

    def __init__(self, label_map: Optional[Dict] = None):
        self.label_map = label_map or LABEL_MAP
        self.encoder = None

    def encode(self, df: pd.DataFrame, label_column: str = "label") -> pd.DataFrame:
        """Apply label map and encode labels"""
        df = df.copy()
        df[label_column] = df[label_column].apply(lambda x: self.label_map.get(x, x))

        self.encoder = SkLabelEncoder()
        self.encoder.fit(df[label_column])
        df["label_encoded"] = self.encoder.transform(df[label_column])

        return df

    def decode(self, encoded_labels: np.ndarray) -> np.ndarray:
        """Decode encoded labels back to original"""
        if self.encoder is None:
            raise ValueError("Encoder not fitted yet")
        return self.encoder.inverse_transform(encoded_labels)

    def save(self, path: Path):
        """Save encoder to disk"""
        with open(path, "wb") as f:
            pickle.dump(self.encoder, f)

    def load(self, path: Path):
        """Load encoder from disk"""
        with open(path, "rb") as f:
            self.encoder = pickle.load(f)
