"""Model training wrappers for Assignment 2."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42


def build_ridge_pipeline(alpha: float = 1.0) -> Pipeline:
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=alpha, random_state=RANDOM_STATE)),
        ]
    )


def build_logistic_pipeline(C: float = 1.0) -> Pipeline:
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(C=C, max_iter=1000, random_state=RANDOM_STATE),
            ),
        ]
    )


@dataclass
class SearchResult:
    best_estimator: Pipeline
    best_params: dict
    best_cv_mae: float
    n_candidates: int
    train_time_s: float
    search_notes: str


def _engine_subsample(groups: pd.Series, n_engines: int = 50) -> pd.Series:
    unique = groups.unique()
    rng = np.random.default_rng(RANDOM_STATE)
    chosen = set(rng.choice(unique, size=min(n_engines, len(unique)), replace=False))
    return groups.isin(chosen)


def _cv_mae(pipe: Pipeline, X: pd.DataFrame, y: pd.Series, groups: pd.Series, n_splits: int = 5) -> float:
    from src.evaluation import regression_metrics

    cv = GroupKFold(n_splits=n_splits)
    maes = []
    for tr, te in cv.split(X, y, groups):
        m = clone(pipe)
        m.fit(X.iloc[tr], y.iloc[tr])
        pred = m.predict(X.iloc[te])
        maes.append(regression_metrics(y.iloc[te].values, pred)["MAE"])
    return float(np.mean(maes))


def random_search(
    pipe: Pipeline,
    param_grid: dict[str, list],
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    *,
    n_iter: int = 25,
    n_splits: int = 5,
    subsample_engines: int = 50,
) -> SearchResult:
    """Custom RandomizedSearch with progress logging (>=25 candidates)."""
    rng = np.random.default_rng(RANDOM_STATE)
    mask = _engine_subsample(groups, subsample_engines)
    Xs, ys, gs = X.loc[mask], y.loc[mask], groups.loc[mask]

    keys = list(param_grid.keys())
    best_mae = np.inf
    best_params: dict = {}
    t0 = time.perf_counter()

    for i in range(n_iter):
        params = {k: rng.choice(param_grid[k]) for k in keys}
        candidate = clone(pipe)
        candidate.set_params(**params)
        mae = _cv_mae(candidate, Xs, ys, gs, n_splits=n_splits)
        print(f"  candidate {i + 1}/{n_iter}: MAE={mae:.2f} params={params}", flush=True)
        if mae < best_mae:
            best_mae = mae
            best_params = params

    best = clone(pipe)
    best.set_params(**best_params)
    best.fit(X, y)
    elapsed = time.perf_counter() - t0
    notes = f"Search on {subsample_engines} engines subsample; refit on full {groups.nunique()} engines"
    return SearchResult(best, best_params, best_mae, n_iter, elapsed, notes)


def tune_random_forest(X, y, groups, *, n_iter: int = 25) -> SearchResult:
    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=1)),
        ]
    )
    param_grid = {
        "model__n_estimators": [50, 80, 100, 120],
        "model__max_depth": [8, 12, 16, None],
        "model__min_samples_leaf": [1, 2, 4],
        "model__max_features": ["sqrt", 0.5],
    }
    print("Random Forest random search...", flush=True)
    return random_search(pipe, param_grid, X, y, groups, n_iter=n_iter)


def tune_gradient_boosting(X, y, groups, *, n_iter: int = 25) -> SearchResult:
    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", GradientBoostingRegressor(random_state=RANDOM_STATE)),
        ]
    )
    param_grid = {
        "model__n_estimators": [50, 80, 100],
        "model__learning_rate": [0.05, 0.1, 0.15],
        "model__max_depth": [3, 4, 5],
        "model__subsample": [0.8, 1.0],
    }
    print("Gradient Boosting random search...", flush=True)
    return random_search(pipe, param_grid, X, y, groups, n_iter=n_iter)


def extract_feature_importance(
    fitted_pipeline: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    feature_names: list[str],
) -> pd.DataFrame:
    model = fitted_pipeline.named_steps["model"]
    if hasattr(model, "feature_importances_"):
        gain = model.feature_importances_
    elif hasattr(model, "coef_"):
        gain = np.abs(model.coef_).ravel()
    else:
        gain = np.zeros(len(feature_names))

    sample_idx = X.sample(min(2000, len(X)), random_state=RANDOM_STATE).index
    perm = permutation_importance(
        fitted_pipeline,
        X.loc[sample_idx],
        y.loc[sample_idx],
        n_repeats=3,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )
    return pd.DataFrame(
        {
            "feature": feature_names,
            "gain_importance": gain,
            "perm_importance_mean": perm.importances_mean,
            "perm_importance_std": perm.importances_std,
        }
    ).sort_values("perm_importance_mean", ascending=False)


def save_model(pipeline: Pipeline, path: Path, metadata: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)
    path.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")


def inference_time_seconds(model, X_sample: pd.DataFrame, *, repeats: int = 50) -> float:
    t0 = time.perf_counter()
    for _ in range(repeats):
        model.predict(X_sample)
    return (time.perf_counter() - t0) / repeats
