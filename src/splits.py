"""Engine-grouped cross-validation utilities (G4)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit


def make_group_kfold(n_splits: int = 5, *, random_state: int = 42) -> GroupKFold:
    return GroupKFold(n_splits=n_splits)


def train_val_test_engine_split(
    df: pd.DataFrame,
    *,
    group_col: str = "unit_number",
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split entire engines — never individual rows — into train/val/test."""
    engines = df[group_col].unique()
    rng = np.random.default_rng(random_state)

    shuffled = rng.permutation(engines)
    n_test = max(1, int(len(shuffled) * test_size))
    n_val = max(1, int(len(shuffled) * val_size))

    test_engines = set(shuffled[:n_test])
    val_engines = set(shuffled[n_test : n_test + n_val])
    train_engines = set(shuffled[n_test + n_val :])

    train = df[df[group_col].isin(train_engines)].copy()
    val = df[df[group_col].isin(val_engines)].copy()
    test = df[df[group_col].isin(test_engines)].copy()
    return train, val, test


def group_shuffle_split(
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    *,
    test_size: float = 0.2,
    random_state: int = 42,
):
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(splitter.split(X, y, groups=groups))
    return train_idx, test_idx
