"""Feature engineering for Smart Factory RUL prediction (Assignment 2)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

TOP_SENSORS = [
    "sensor_11",
    "sensor_4",
    "sensor_12",
    "sensor_7",
    "sensor_15",
    "sensor_21",
    "sensor_20",
    "sensor_2",
    "sensor_17",
    "sensor_3",
]

FEATURE_CATALOG: list[dict] = []


def _register(name: str, formula: str, rationale: str, deployable: bool = True) -> None:
    FEATURE_CATALOG.append(
        {
            "feature_name": name,
            "formula": formula,
            "rationale": rationale,
            "deployable_at_prediction_time": deployable,
        }
    )


def _rolling_slope(series: pd.Series, window: int = 20) -> pd.Series:
    def slope(arr: np.ndarray) -> float:
        if len(arr) < 3 or np.allclose(arr, arr[0]):
            return 0.0
        x = np.arange(len(arr))
        return float(np.polyfit(x, arr, 1)[0])

    return series.rolling(window, min_periods=3).apply(slope, raw=True)


def _ewma(series: pd.Series, alpha: float) -> pd.Series:
    return series.ewm(alpha=alpha, adjust=False).mean()


def engineer_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build Assignment 2 advanced features on top of A1 cleaned data."""
    global FEATURE_CATALOG
    FEATURE_CATALOG = []

    out = df.copy()
    group = out.groupby("unit_number", group_keys=False)

    # 1. Rolling slope for top sensors
    for s in TOP_SENSORS[:3]:
        col = f"{s}_slope20"
        out[col] = group[s].transform(lambda x: _rolling_slope(x, 20))
        _register(
            col,
            f"Linear slope of {s} over 20-cycle window per engine",
            "Captures degradation speed; A1 Finding 5 monotonic lifecycle separation",
        )

    # 2. Rolling std (volatility)
    for s in TOP_SENSORS[:3]:
        col = f"{s}_std20"
        out[col] = group[s].transform(lambda x: x.rolling(20, min_periods=3).std())
        _register(
            col,
            f"Rolling std of {s} over 20 cycles",
            "Late-stage variance inflation observed in A1 Figure 7",
        )

    # 3. Rolling min/max
    for s in TOP_SENSORS[:2]:
        out[f"{s}_min20"] = group[s].transform(lambda x: x.rolling(20, min_periods=3).min())
        out[f"{s}_max20"] = group[s].transform(lambda x: x.rolling(20, min_periods=3).max())
        _register(f"{s}_min20", f"20-cycle rolling min of {s}", "Range compression/expansion near failure")
        _register(f"{s}_max20", f"20-cycle rolling max of {s}", "Range compression/expansion near failure")

    # 4. Sensor interaction (standardized product)
    s4 = (out["sensor_4"] - out["sensor_4"].mean()) / (out["sensor_4"].std() + 1e-9)
    s11 = (out["sensor_11"] - out["sensor_11"].mean()) / (out["sensor_11"].std() + 1e-9)
    out["sensor_4_x_sensor_11"] = s4 * s11
    _register(
        "sensor_4_x_sensor_11",
        "Standardized sensor_4 × standardized sensor_11",
        "Interaction between two strongest RUL-correlated channels (A1 Figure 9)",
    )

    # 5. Lag features for top 3 sensors
    for s in TOP_SENSORS[:3]:
        for lag in (1, 5, 10):
            col = f"{s}_lag{lag}"
            out[col] = group[s].shift(lag)
            _register(
                col,
                f"{s} value lagged {lag} cycles within engine",
                "Temporal memory of degradation trajectory",
            )

    # 6. Operational regime change indicators
    out["setting1_change"] = group["operational_setting_1"].diff().abs().fillna(0)
    out["setting2_change"] = group["operational_setting_2"].diff().abs().fillna(0)
    _register(
        "setting1_change",
        "|diff(operational_setting_1)| per engine",
        "Detects operational regime shifts",
    )
    _register(
        "setting2_change",
        "|diff(operational_setting_2)| per engine",
        "Detects operational regime shifts",
    )

    # 7. Cumulative deviation from early-life baseline (first 30 cycles)
    def baseline_deviation(g: pd.DataFrame) -> pd.Series:
        baseline = g[TOP_SENSORS].iloc[: min(30, len(g))].mean()
        return ((g[TOP_SENSORS] - baseline) ** 2).sum(axis=1) ** 0.5

    out["baseline_deviation"] = group.apply(baseline_deviation).reset_index(level=0, drop=True)
    _register(
        "baseline_deviation",
        "Euclidean distance from engine early-life (≤30 cycles) sensor mean",
        "Engine-specific wear offset beyond calendar age",
    )

    # 8. EWMA features
    for s in TOP_SENSORS[:2]:
        for alpha in (0.1, 0.3):
            col = f"{s}_ewma_a{str(alpha).replace('.', '')}"
            out[col] = group[s].transform(lambda x, a=alpha: _ewma(x, a))
            _register(
                col,
                f"EWMA(α={alpha}) of {s} per engine",
                "Smoothed degradation trend with configurable memory",
            )

    # 9. PCA scores from top 10 sensors (fit per full train — caller refits on train only for CV)
    pca_cols = TOP_SENSORS
    scaler = StandardScaler()
    scaled = scaler.fit_transform(out[pca_cols].fillna(out[pca_cols].median()))
    pca = PCA(n_components=2, random_state=42)
    scores = pca.fit_transform(scaled)
    out["pca_score_1"] = scores[:, 0]
    out["pca_score_2"] = scores[:, 1]
    _register(
        "pca_score_1",
        "PC1 of standardized top-10 sensors",
        "A1 PCA explained ~74.7% variance on PC1 with life-stage stratification",
    )
    _register(
        "pca_score_2",
        "PC2 of standardized top-10 sensors",
        "Secondary latent degradation axis",
    )

    # 10. Time-since-anomaly (rolling z-score breach counter)
    def anomaly_counter(g: pd.DataFrame) -> pd.Series:
        z = (g["sensor_11"] - g["sensor_11"].rolling(20, min_periods=5).mean()) / (
            g["sensor_11"].rolling(20, min_periods=5).std() + 1e-9
        )
        breach = (z.abs() > 2).astype(int)
        counter = []
        c = 0
        for b in breach:
            c = 0 if b else c + 1
            counter.append(c)
        return pd.Series(counter, index=g.index)

    out["time_since_anomaly_s11"] = group.apply(anomaly_counter).reset_index(level=0, drop=True)
    _register(
        "time_since_anomaly_s11",
        "Cycles since |z-score|>2 on sensor_11 rolling window",
        "Duration since last anomalous reading on primary sensor",
    )

    # Fill NaNs from lags/rolling with group median then global median
    new_cols = [c for c in out.columns if c not in df.columns]
    for col in new_cols:
        out[col] = out.groupby("unit_number")[col].transform(lambda x: x.fillna(x.median()))
        out[col] = out[col].fillna(out[col].median())

    catalog = pd.DataFrame(FEATURE_CATALOG)
    return out, catalog


def select_features(
    df: pd.DataFrame,
    feature_cols: list[str],
    target: str = "RUL",
    corr_threshold: float = 0.95,
) -> list[str]:
    """Correlation pruning then return ordered feature list."""
    X = df[feature_cols].copy()
    corr = X.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    drop = {column for column in upper.columns if any(upper[column] > corr_threshold)}
    kept = [c for c in feature_cols if c not in drop]
    return kept


def get_deployable_feature_columns(df: pd.DataFrame) -> list[str]:
    """All columns safe for model input."""
    from src.leakage_guard import FORBIDDEN_INPUT_COLUMNS

    exclude = FORBIDDEN_INPUT_COLUMNS | {"unit_number"}
    raw_sensors = {f"sensor_{i}" for i in range(1, 22)}
    # Include raw sensors, roll20 from A1, and new engineered cols
    candidates = [
        c
        for c in df.columns
        if c not in exclude
        and c != "life_stage"
        and not c.startswith("Unnamed")
    ]
    return sorted(candidates)
