"""Unit tests for grouped star-level splitting with 0% star leakage."""
import pandas as pd
import pytest

from src.data_loader import create_grouped_splits


def test_grouped_star_splits_isolation():
    """Verify that no star ID ever appears in multiple splits."""
    # Create 30 stars, some with multiple planets
    kepids = []
    tce_nums = []
    labels = []
    periods = []

    for s_idx in range(30):
        kid = 100000 + s_idx
        n_planets = 1 if s_idx % 3 != 0 else 3
        for p in range(1, n_planets + 1):
            kepids.append(kid)
            tce_nums.append(p)
            labels.append(1 if s_idx % 2 == 0 else 0)
            periods.append(10.0 * p)

    df_test_stars = pd.DataFrame({
        "kepid": kepids,
        "tce_plnt_num": tce_nums,
        "planet": labels,
        "tce_period": periods,
        "av_training_set": ["PC" if l == 1 else "AFP" for l in labels],
    })

    train_df, val_df, test_df, split_info = create_grouped_splits(
        df_test_stars, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, random_seed=42
    )

    train_stars = set(train_df["kepid"])
    val_stars = set(val_df["kepid"])
    test_stars = set(test_df["kepid"])

    # Strict isolation verification
    assert len(train_stars & val_stars) == 0, "Train-Val overlap detected!"
    assert len(train_stars & test_stars) == 0, "Train-Test overlap detected!"
    assert len(val_stars & test_stars) == 0, "Val-Test overlap detected!"

    # Total stars match
    all_stars = set(df_test_stars["kepid"])
    assert (train_stars | val_stars | test_stars) == all_stars

