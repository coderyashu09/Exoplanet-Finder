"""Unit tests for dataset loading, label conversion, and data leakage elimination."""
import numpy as np
import pandas as pd
import pytest

from src.data_loader import clean_and_filter_tce_data


def test_clean_and_filter_tce_data_basic():
    """Test standard filtering: PC -> 1, AFP/NTP -> 0, UNK dropped."""
    synthetic_df = pd.DataFrame({
        "kepid": [1001, 1002, 1003, 1004, 1005],
        "tce_plnt_num": [1, 1, 1, 1, 1],
        "tce_period": [10.5, 5.2, 12.1, 8.0, 0.0],  # 0.0 is invalid
        "tce_time0bk": [133.0, 134.0, 135.0, 136.0, 137.0],
        "tce_duration": [3.2, 4.1, 2.8, 1.5, 2.0],
        "av_training_set": ["PC", "AFP", "NTP", "UNK", "PC"],
        "av_pred_class": ["PC", "AFP", "NTP", "UNK", "PC"],  # Leakage column
        "av_pp_pc": [0.99, 0.01, 0.05, 0.50, 0.90],          # Leakage column
    })

    clean_df, audit = clean_and_filter_tce_data(synthetic_df)

    # UNK dropped, period=0.0 dropped -> 3 rows remain (PC, AFP, NTP)
    assert len(clean_df) == 3
    assert audit["exclusions"]["unknown_or_missing_label"] == 1
    assert audit["exclusions"]["invalid_period"] == 1

    # Verify binary target
    assert (clean_df["planet"].to_numpy() == [1, 0, 0]).all()

    # Verify leakage columns are eliminated
    assert "av_pred_class" not in clean_df.columns
    assert "av_pp_pc" not in clean_df.columns


def test_clean_and_filter_missing_values():
    """Test dropping rows with NaNs in critical orbital ephemeris."""
    df_missing = pd.DataFrame({
        "kepid": [2001, 2002, None],
        "tce_plnt_num": [1, 1, 1],
        "tce_period": [15.0, np.nan, 20.0],
        "tce_time0bk": [np.nan, 130.0, 140.0],
        "tce_duration": [2.5, 3.0, -1.0],  # negative duration invalid
        "av_training_set": ["PC", "PC", "AFP"],
    })

    clean_df, audit = clean_and_filter_tce_data(df_missing)
    assert len(clean_df) == 0
    assert audit["final_valid_rows"] == 0

