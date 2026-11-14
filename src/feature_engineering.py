"""Feature extraction and engineering for tabular baseline exoplanet classification."""
import logging
from typing import List, Tuple, Dict, Any, Optional

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler

from src.config import cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASELINE_FEATURES = ["tce_period", "tce_duration", "tce_depth"]


class BaselineFeatureExtractor:
    """Prepares and scales tabular astrophysical features for baseline tree models.

    Strictly fits transformers ONLY on training stars to prevent data leakage.
    """

    def __init__(self, features: Optional[List[str]] = None):
        self.features = features or BASELINE_FEATURES
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = RobustScaler()
        self.is_fitted = False

    def fit(self, df_train: pd.DataFrame) -> "BaselineFeatureExtractor":
        X = df_train[self.features].copy()
        # Log-transform highly skewed features: duration and depth
        X_trans = self._transform_distributions(X)
        self.imputer.fit(X_trans)
        X_imp = self.imputer.transform(X_trans)
        self.scaler.fit(X_imp)
        self.is_fitted = True
        logger.info(f"Fitted BaselineFeatureExtractor on {len(df_train)} training records.")
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("BaselineFeatureExtractor must be fitted before transform.")
        X = df[self.features].copy()
        X_trans = self._transform_distributions(X)
        X_imp = self.imputer.transform(X_trans)
        return self.scaler.transform(X_imp)

    def _transform_distributions(self, df: pd.DataFrame) -> pd.DataFrame:
        df_out = df.copy()
        for col in ["tce_depth", "tce_period", "tce_duration"]:
            if col in df_out.columns:
                # Log1p of strictly non-negative values
                vals = np.maximum(df_out[col].fillna(0).to_numpy(), 0)
                df_out[col] = np.log1p(vals)
        return df_out


def prepare_baseline_data(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, BaselineFeatureExtractor]:
    """Extract and transform baseline features without data leakage across splits."""
    extractor = BaselineFeatureExtractor(BASELINE_FEATURES)
    extractor.fit(df_train)

    X_train = extractor.transform(df_train)
    y_train = df_train["planet"].to_numpy().astype(int)

    X_val = extractor.transform(df_val)
    y_val = df_val["planet"].to_numpy().astype(int)

    X_test = extractor.transform(df_test)
    y_test = df_test["planet"].to_numpy().astype(int)

    return X_train, y_train, X_val, y_val, X_test, y_test, extractor

