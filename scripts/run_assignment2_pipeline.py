"""
End-to-end Assignment 2 pipeline: feature engineering, training, evaluation.
Run from repo root: python scripts/run_assignment2_pipeline.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import RocCurveDisplay
from sklearn.model_selection import GroupKFold, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.evaluation import (  # noqa: E402
    classification_metrics,
    nasa_phm08_score,
    regression_metrics,
)
from src.features import engineer_features, get_deployable_feature_columns, select_features  # noqa: E402
from src.leakage_guard import assert_no_leakage  # noqa: E402
from src.models import (  # noqa: E402
    build_logistic_pipeline,
    build_ridge_pipeline,
    extract_feature_importance,
    inference_time_seconds,
    save_model,
    tune_gradient_boosting,
    tune_random_forest,
)

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

RAW_COLS = (
    ["unit_number", "time_in_cycles"]
    + [f"operational_setting_{i}" for i in range(1, 4)]
    + [f"sensor_{i}" for i in range(1, 22)]
)


def load_raw(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=r"\s+", header=None, names=RAW_COLS)
    return df


def add_a1_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Replicate A1 RUL / near_failure for train; test has no failure cycle."""
    out = df.copy()
    max_cycle = out.groupby("unit_number")["time_in_cycles"].transform("max")
    out["max_cycle"] = max_cycle
    out["RUL"] = max_cycle - out["time_in_cycles"]
    out["cycle_ratio"] = out["time_in_cycles"] / out["max_cycle"]
    out["near_failure"] = (out["RUL"] <= 30).astype(int)
    out["capped_RUL"] = out["RUL"].clip(upper=125)
    bins = [0, 0.33, 0.67, 1.01]
    out["life_stage"] = pd.cut(
        out["cycle_ratio"],
        bins=bins,
        labels=["early", "mid", "late"],
        include_lowest=True,
    )
    # Rolling means for top sensors (A1)
    top = [
        "sensor_11", "sensor_4", "sensor_12", "sensor_7", "sensor_15",
        "sensor_21", "sensor_20", "sensor_2", "sensor_17", "sensor_3",
    ]
    for s in top:
        out[f"{s}_roll20"] = (
            out.groupby("unit_number")[s]
            .transform(lambda x: x.rolling(20, min_periods=1).mean())
        )
    return out


def run_cv_regression(model, X, y, groups, model_name: str) -> pd.DataFrame:
    cv = GroupKFold(n_splits=5)
    rows = []
    for fold, (tr, te) in enumerate(cv.split(X, y, groups), start=1):
        m = Pipeline(model.steps)
        m.set_params(**model.get_params())
        m.fit(X.iloc[tr], y.iloc[tr])
        pred = m.predict(X.iloc[te])
        metrics = regression_metrics(y.iloc[te].values, pred)
        metrics.update({"model": model_name, "fold": fold, "task": "RUL_regression"})
        rows.append(metrics)
    return pd.DataFrame(rows)


def main() -> None:
    t_start = time.perf_counter()
    print("=== Assignment 2 Pipeline ===")

    # --- Load train ---
    train_raw = load_raw(ROOT / "data" / "raw" / "train_FD001.txt")
    train_base = add_a1_targets(train_raw)
    assert train_base.shape[0] == 20631, f"Unexpected train rows: {train_base.shape[0]}"

    # --- Feature engineering ---
    print("Feature engineering...")
    train_fe, catalog = engineer_features(train_base)
    catalog_path = ROOT / "outputs" / "feature_catalog.csv"
    catalog.to_csv(catalog_path, index=False)
    assert len(catalog) >= 10, f"Only {len(catalog)} engineered features documented"

    fe_path = ROOT / "data" / "processed" / "SmartFactory_modeling.csv"
    train_fe.to_csv(fe_path, index=False)

    feature_cols = get_deployable_feature_columns(train_fe)
    selected = select_features(train_fe, feature_cols, corr_threshold=0.95)
    assert_no_leakage(selected, context="modeling feature set")
    print(f"Selected {len(selected)} deployable features")

    sel_path = ROOT / "outputs" / "selected_features.csv"
    pd.DataFrame({"feature": selected}).to_csv(sel_path, index=False)

    X = train_fe[selected]
    y_rul = train_fe["RUL"]
    y_nf = train_fe["near_failure"]
    groups = train_fe["unit_number"]

    # --- Model 1: Ridge baseline ---
    print("Training Ridge baseline...")
    ridge = build_ridge_pipeline(alpha=1.0)
    t0 = time.perf_counter()
    ridge.fit(X, y_rul)
    ridge_train_time = time.perf_counter() - t0
    ridge_pred = ridge.predict(X)
    ridge_train_metrics = regression_metrics(y_rul.values, ridge_pred)

    # --- Model 1b: Logistic for near_failure ---
    logit = build_logistic_pipeline(C=1.0)
    logit.fit(X, y_nf)
    logit_pred = logit.predict(X)
    logit_prob = logit.predict_proba(X)[:, 1]
    logit_metrics = classification_metrics(y_nf.values, logit_pred, logit_prob)

    # --- Model 2: Random Forest (tuned) ---
    print("Tuning Random Forest (25 candidates)...", flush=True)
    rf_result = tune_random_forest(X, y_rul, groups, n_iter=25)
    rf_best = rf_result.best_estimator
    rf_train_time = rf_result.train_time_s

    print("Tuning Gradient Boosting (25 candidates)...", flush=True)
    gbm_result = tune_gradient_boosting(X, y_rul, groups, n_iter=25)
    gbm_best = gbm_result.best_estimator
    gbm_train_time = gbm_result.train_time_s

    # --- CV metrics ---
    print("Cross-validation...")
    cv_ridge = run_cv_regression(ridge, X, y_rul, groups, "Ridge")
    cv_rf = run_cv_regression(rf_best, X, y_rul, groups, "RandomForest")
    cv_gbm = run_cv_regression(gbm_best, X, y_rul, groups, "GradientBoosting")
    cv_all = pd.concat([cv_ridge, cv_rf, cv_gbm], ignore_index=True)
    cv_summary = (
        cv_all.groupby("model")[["MAE", "RMSE", "R2", "MAPE"]]
        .agg(["mean", "std"])
        .round(4)
    )
    cv_all.to_csv(ROOT / "outputs" / "cv_results.csv", index=False)
    cv_summary.to_csv(ROOT / "outputs" / "cv_summary.csv")

    # --- Pick final model by CV MAE ---
    cv_mae = cv_all.groupby("model")["MAE"].mean()
    best_name = cv_mae.idxmin()
    final_model = {"Ridge": ridge, "RandomForest": rf_best, "GradientBoosting": gbm_best}[best_name]
    print(f"Final model selected: {best_name} (CV MAE={cv_mae[best_name]:.2f})")

    # --- Inference times ---
    sample = X.head(100)
    ridge_inf = inference_time_seconds(ridge, sample)
    rf_inf = inference_time_seconds(rf_best, sample)
    gbm_inf = inference_time_seconds(gbm_best, sample)

    def improvement(base: float, adv: float) -> float:
        return (base - adv) / base * 100 if base else 0.0

    comparison = pd.DataFrame(
        [
            {
                "model": "Ridge (Baseline)",
                "MAE_train": ridge_train_metrics["MAE"],
                "RMSE_train": ridge_train_metrics["RMSE"],
                "R2_train": ridge_train_metrics["R2"],
                "CV_MAE_mean": cv_ridge["MAE"].mean(),
                "CV_MAE_std": cv_ridge["MAE"].std(),
                "train_time_s": ridge_train_time,
                "inference_time_s": ridge_inf,
            },
            {
                "model": "RandomForest (Advanced)",
                "MAE_train": regression_metrics(y_rul, rf_best.predict(X))["MAE"],
                "RMSE_train": regression_metrics(y_rul, rf_best.predict(X))["RMSE"],
                "R2_train": regression_metrics(y_rul, rf_best.predict(X))["R2"],
                "CV_MAE_mean": cv_rf["MAE"].mean(),
                "CV_MAE_std": cv_rf["MAE"].std(),
                "train_time_s": rf_train_time,
                "inference_time_s": rf_inf,
                "best_params": json.dumps(rf_search.best_params_),
            },
            {
                "model": "GradientBoosting (Advanced)",
                "MAE_train": regression_metrics(y_rul, gbm_best.predict(X))["MAE"],
                "RMSE_train": regression_metrics(y_rul, gbm_best.predict(X))["RMSE"],
                "R2_train": regression_metrics(y_rul, gbm_best.predict(X))["R2"],
                "CV_MAE_mean": cv_gbm["MAE"].mean(),
                "CV_MAE_std": cv_gbm["MAE"].std(),
                "train_time_s": gbm_train_time,
                "inference_time_s": gbm_inf,
                "best_params": json.dumps(gbm_search.best_params_),
            },
        ]
    )
    comparison.to_csv(ROOT / "outputs" / "model_comparison.csv", index=False)

    # --- Feature importance ---
    print("Feature importance...")
    fi = extract_feature_importance(final_model, X, y_rul, selected)
    fi.to_csv(ROOT / "outputs" / "feature_importance.csv", index=False)

    # --- Test set evaluation (NASA FD001) ---
    print("Evaluating on NASA test set...")
    test_raw = load_raw(ROOT / "data" / "raw" / "test_FD001.txt")
    test_base = add_a1_targets(test_raw)
    test_fe, _ = engineer_features(test_base)
    X_test = test_fe[selected]

    # Last cycle per test engine
    last_idx = test_fe.groupby("unit_number")["time_in_cycles"].idxmax()
    test_last = test_fe.loc[last_idx].copy()
    X_test_last = test_last[selected]

    true_rul = pd.read_csv(ROOT / "data" / "raw" / "RUL_FD001.txt", header=None, names=["true_RUL"])
    true_rul["unit_number"] = range(1, len(true_rul) + 1)
    test_last = test_last.merge(true_rul, on="unit_number")

    for name, mdl in [("Ridge", ridge), ("RandomForest", rf_best), ("GradientBoosting", gbm_best)]:
        test_last[f"pred_{name}"] = mdl.predict(X_test_last)

    test_last["pred_final"] = final_model.predict(X_test_last)
    test_metrics_rows = []
    for name, col in [
        ("Ridge", "pred_Ridge"),
        ("RandomForest", "pred_RandomForest"),
        ("GradientBoosting", "pred_GradientBoosting"),
        ("Final", "pred_final"),
    ]:
        m = regression_metrics(test_last["true_RUL"].values, test_last[col].values)
        m["NASA_PHM08_score"] = nasa_phm08_score(
            test_last["true_RUL"].values, test_last[col].values
        )
        m["model"] = name
        test_metrics_rows.append(m)
    test_metrics_df = pd.DataFrame(test_metrics_rows)
    test_metrics_df.to_csv(ROOT / "outputs" / "test_metrics.csv", index=False)

    # Error analysis — worst 20 engines by final model
    test_last["abs_error"] = (test_last["pred_final"] - test_last["true_RUL"]).abs()
    error_analysis = test_last.nlargest(20, "abs_error")[
        ["unit_number", "time_in_cycles", "true_RUL", "pred_final", "abs_error"]
    ]
    error_analysis.to_csv(ROOT / "outputs" / "error_analysis.csv", index=False)

    # --- Save final model ---
    import sklearn

    metadata = {
        "model_name": best_name,
        "random_state": RANDOM_STATE,
        "sklearn_version": sklearn.__version__,
        "n_train_rows": len(train_fe),
        "n_features": len(selected),
        "features": selected,
        "cv_mae_mean": float(cv_mae[best_name]),
        "test_mae": float(test_metrics_df.loc[test_metrics_df["model"] == "Final", "MAE"].iloc[0]),
        "test_rmse": float(test_metrics_df.loc[test_metrics_df["model"] == "Final", "RMSE"].iloc[0]),
        "test_r2": float(test_metrics_df.loc[test_metrics_df["model"] == "Final", "R2"].iloc[0]),
        "test_nasa_phm08": float(
            test_metrics_df.loc[test_metrics_df["model"] == "Final", "NASA_PHM08_score"].iloc[0]
        ),
        "rf_best_params": rf_search.best_params_,
        "gbm_best_params": gbm_search.best_params_,
        "logistic_classification": logit_metrics,
    }
    model_path = ROOT / "models" / "final_model.pkl"
    save_model(final_model, model_path, metadata)
    (ROOT / "models" / "final_model_metadata.json").write_text(
        json.dumps(metadata, indent=2, default=str), encoding="utf-8"
    )
    joblib.dump(logit, ROOT / "models" / "near_failure_classifier.pkl")

    # Save test predictions for dashboard
    test_last.to_csv(ROOT / "outputs" / "test_predictions.csv", index=False)
    test_fe.to_csv(ROOT / "data" / "processed" / "SmartFactory_test_features.csv", index=False)

    # --- Figures ---
    print("Generating figures...")
    fig_dir = ROOT / "figures"
    fig_dir.mkdir(exist_ok=True)
    sns.set_style("whitegrid")

    # Fig A2-01: Actual vs Predicted (test last cycle)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(test_last["true_RUL"], test_last["pred_final"], alpha=0.7, edgecolors="k", linewidths=0.3)
    lim = max(test_last["true_RUL"].max(), test_last["pred_final"].max()) + 5
    ax.plot([0, lim], [0, lim], "r--", label="Perfect prediction")
    ax.set_xlabel("True RUL (cycles)")
    ax.set_ylabel("Predicted RUL (cycles)")
    ax.set_title(f"Test Set: Actual vs Predicted RUL ({best_name})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure_A2_01_actual_vs_predicted.png", dpi=300)
    plt.close(fig)

    # Fig A2-02: Residual histogram
    residuals = test_last["pred_final"] - test_last["true_RUL"]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(residuals, bins=20, edgecolor="black", alpha=0.75)
    ax.axvline(0, color="red", linestyle="--")
    ax.set_xlabel("Prediction Error (cycles)")
    ax.set_ylabel("Count")
    ax.set_title("Test Set Residual Distribution")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure_A2_02_residual_histogram.png", dpi=300)
    plt.close(fig)

    # Fig A2-03: Feature importance
    top_fi = fi.head(15)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top_fi["feature"][::-1], top_fi["perm_importance_mean"][::-1])
    ax.set_xlabel("Permutation Importance")
    ax.set_title(f"Top 15 Features ({best_name})")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure_A2_03_feature_importance.png", dpi=300)
    plt.close(fig)

    # Fig A2-04: Model comparison bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    models_plot = test_metrics_df[test_metrics_df["model"] != "Final"]
    x = np.arange(len(models_plot))
    ax.bar(x, models_plot["MAE"], color=["#4C72B0", "#55A868", "#C44E52"])
    ax.set_xticks(x)
    ax.set_xticklabels(models_plot["model"], rotation=15)
    ax.set_ylabel("MAE (cycles)")
    ax.set_title("Test Set MAE Comparison")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure_A2_04_model_comparison.png", dpi=300)
    plt.close(fig)

    # Fig A2-05: CV MAE with error bars
    fig, ax = plt.subplots(figsize=(8, 5))
    cv_plot = cv_all.groupby("model")["MAE"].agg(["mean", "std"])
    ax.bar(cv_plot.index, cv_plot["mean"], yerr=cv_plot["std"], capsize=5, color="#4C72B0")
    ax.set_ylabel("MAE (cycles)")
    ax.set_title("5-Fold Engine-Grouped CV — MAE (mean ± std)")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure_A2_05_cv_mae.png", dpi=300)
    plt.close(fig)

    # Fig A2-06: ROC for near_failure classifier
    fig, ax = plt.subplots(figsize=(6, 6))
    RocCurveDisplay.from_predictions(y_nf, logit_prob, ax=ax)
    ax.set_title("Near-Failure Classifier ROC (train, in-sample)")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure_A2_06_roc_near_failure.png", dpi=300)
    plt.close(fig)

    # Fig A2-07: Trajectory for 4 test engines
    sample_units = test_last.nlargest(2, "abs_error")["unit_number"].tolist() + test_last.nsmallest(
        2, "abs_error"
    )["unit_number"].tolist()
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    for ax, uid in zip(axes.ravel(), sample_units):
        eng = test_fe[test_fe["unit_number"] == uid]
        preds = final_model.predict(eng[selected])
        ax.plot(eng["time_in_cycles"], preds, label="Predicted RUL", color="#C44E52")
        ax.set_xlabel("Cycle")
        ax.set_ylabel("Predicted RUL")
        ax.set_title(f"Engine {uid}")
        ax.legend(fontsize=8)
    fig.suptitle("Predicted RUL Trajectories (Sample Test Engines)")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure_A2_07_rul_trajectories.png", dpi=300)
    plt.close(fig)

    # --- Recommendations table (A2) ---
    final_mae = test_metrics_df.loc[test_metrics_df["model"] == "Final", "MAE"].iloc[0]
    recs = [
        {
            "id": "R1",
            "title": "Implement Predictive Maintenance Scheduling",
            "problem": "Calendar-based maintenance over-services healthy engines and under-services degrading ones.",
            "solution": f"Schedule inspections when model-predicted RUL < 30 cycles using {best_name} model.",
            "expected_impact": f"Model achieves MAE={final_mae:.1f} cycles on held-out test engines; enables proactive scheduling ~30 cycles ahead.",
            "implementation": "Integrate model scores into weekly maintenance review; pilot on 10 engines first.",
            "timeline": "Short-term (8 weeks)",
            "owner": "Maintenance Director",
            "priority": "High",
            "evidence": "outputs/test_metrics.csv; Figure_A2_01",
        },
        {
            "id": "R2",
            "title": "Prioritise Top Sensor Monitoring",
            "problem": "Monitoring all 21 channels creates noise and bandwidth cost.",
            "solution": f"Focus dashboards on top features: {', '.join(fi.head(5)['feature'].tolist())}.",
            "expected_impact": "Concentrate diagnostic effort on highest permutation-importance channels.",
            "implementation": "Reconfigure SCADA alerts to top-5 sensor rolling statistics.",
            "timeline": "Short-term (4 weeks)",
            "owner": "IoT Engineering Team",
            "priority": "High",
            "evidence": "outputs/feature_importance.csv; Figure_A2_03",
        },
        {
            "id": "R3",
            "title": "Engine-Grouped Model Retraining Protocol",
            "problem": "Row-level validation inflates performance and causes production failures.",
            "solution": "Mandate GroupKFold cross-validation by unit_number for all model updates.",
            "expected_impact": "Realistic generalisation estimates; prevents temporal leakage.",
            "implementation": "Document CV protocol in MLOps runbook; automate in retraining pipeline.",
            "timeline": "Medium-term (3 months)",
            "owner": "Data Science Team",
            "priority": "High",
            "evidence": "outputs/cv_results.csv; Figure_A2_05",
        },
        {
            "id": "R4",
            "title": "Near-Failure Alert Layer",
            "problem": "Continuous RUL alone may miss sudden degradation events.",
            "solution": "Deploy logistic near-failure classifier alongside RUL regression for dual alerts.",
            "expected_impact": f"Classifier ROC-AUC={logit_metrics.get('ROC_AUC', float('nan')):.3f} on training data.",
            "implementation": "Trigger dual alert when RUL<30 OR near-failure probability>0.7.",
            "timeline": "Medium-term (3 months)",
            "owner": "Plant Manager",
            "priority": "Medium",
            "evidence": "Figure_A2_06; models/near_failure_classifier.pkl",
        },
        {
            "id": "R5",
            "title": "Investigate High-Error Engines",
            "problem": "Some test engines show large prediction errors indicating model blind spots.",
            "solution": "Root-cause analysis on worst-20 error engines; collect operational context.",
            "expected_impact": "Identify feature gaps; reduce MAE on outlier engines by 10-15%.",
            "implementation": "Review outputs/error_analysis.csv monthly; augment features for outlier cohorts.",
            "timeline": "Long-term (6 months)",
            "owner": "Reliability Engineering",
            "priority": "Medium",
            "evidence": "outputs/error_analysis.csv",
        },
    ]
    pd.DataFrame(recs).to_csv(ROOT / "outputs" / "recommendations_table_a2.csv", index=False)

    roadmap = pd.DataFrame(
        [
            {"phase": "Phase 1: Quick Wins", "timeline": "0-3 months", "action": "Deploy Streamlit dashboard for fleet RUL visibility", "expected_value": "Real-time risk triage for maintenance teams", "owner": "IoT Team"},
            {"phase": "Phase 1: Quick Wins", "timeline": "0-3 months", "action": "Pilot predictive scheduling on 10 engines", "expected_value": f"Validate MAE={final_mae:.1f} cycle accuracy in operations", "owner": "Maintenance Director"},
            {"phase": "Phase 2: Core Implementation", "timeline": "3-6 months", "action": "Integrate model API into CMMS", "expected_value": "Automated work-order generation from RUL scores", "owner": "IT / Data Team"},
            {"phase": "Phase 2: Core Implementation", "timeline": "3-6 months", "action": "Retrain quarterly with GroupKFold validation", "expected_value": "Sustained model accuracy as fleet ages", "owner": "Data Science Team"},
            {"phase": "Phase 3: Advanced Features", "timeline": "6-12 months", "action": "Multi-condition model (FD002-FD004)", "expected_value": "Generalisation beyond single-regime FD001", "owner": "R&D Engineering"},
            {"phase": "Phase 3: Advanced Features", "timeline": "6-12 months", "action": "Uncertainty quantification (conformal prediction)", "expected_value": "Confidence bands for maintenance decisions", "owner": "Data Science Team"},
        ]
    )
    roadmap.to_csv(ROOT / "outputs" / "roadmap_phases.csv", index=False)

    elapsed = time.perf_counter() - t_start
    print(f"\nPipeline complete in {elapsed:.1f}s")
    print(f"Final model: {best_name}")
    print(f"Test MAE: {final_mae:.2f}")
    print(f"Feature catalog: {len(catalog)} features")
    print("PIPELINE_OK")


if __name__ == "__main__":
    main()
