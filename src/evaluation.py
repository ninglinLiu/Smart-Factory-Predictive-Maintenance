"""Evaluation metrics for RUL regression and near-failure classification."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)
    mask = y_true != 0
    mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100) if mask.any() else float("nan")
    return {"MAE": mae, "RMSE": rmse, "R2": r2, "MAPE": mape}


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray | None = None) -> dict[str, float]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    out = {
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred, zero_division=0),
        "Recall": recall_score(y_true, y_pred, zero_division=0),
        "F1": f1_score(y_true, y_pred, zero_division=0),
    }
    if y_prob is not None and len(np.unique(y_true)) > 1:
        out["ROC_AUC"] = roc_auc_score(y_true, y_prob)
    else:
        out["ROC_AUC"] = float("nan")
    return out


def nasa_phm08_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Asymmetric scoring from PHM08 challenge (lower is better)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    diff = y_pred - y_true
    scores = np.where(diff < 0, np.exp(-diff / 13.0) - 1.0, np.exp(diff / 10.0) - 1.0)
    return float(np.sum(scores))


def metrics_to_row(model_name: str, metrics: dict[str, float], split: str) -> dict:
    row = {"model": model_name, "split": split}
    row.update(metrics)
    return row


def save_metrics_table(rows: list[dict], path: str) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df
