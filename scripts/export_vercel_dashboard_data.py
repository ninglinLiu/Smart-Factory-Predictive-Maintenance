"""Export dashboard data as JSON for Vercel static deployment."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "web" / "public" / "data"
SENSORS = ["sensor_11", "sensor_4", "sensor_12", "sensor_7", "sensor_15"]


def rul_band(rul: float, threshold: int = 30) -> str:
    if rul < threshold:
        return "Critical"
    if rul < 60:
        return "Watch"
    return "Healthy"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    train = pd.read_csv(ROOT / "data/processed/SmartFactory_modeling.csv")
    test_pred = pd.read_csv(ROOT / "outputs/test_predictions.csv")
    fi = pd.read_csv(ROOT / "outputs/feature_importance.csv")
    test_metrics = pd.read_csv(ROOT / "outputs/test_metrics.csv")
    recs = pd.read_csv(ROOT / "outputs/recommendations_table_a2.csv")
    model = joblib.load(ROOT / "models/final_model.pkl")
    meta = json.loads((ROOT / "models/final_model_metadata.json").read_text(encoding="utf-8"))
    features = meta["features"]

    threshold = 30
    fleet_rows = []
    for _, row in test_pred.iterrows():
        pred = float(row["pred_final"])
        fleet_rows.append(
            {
                "unit_number": int(row["unit_number"]),
                "true_RUL": float(row["true_RUL"]),
                "pred_final": pred,
                "status": rul_band(pred, threshold),
                "abs_error": float(abs(pred - row["true_RUL"])),
            }
        )

    fleet_payload = {
        "threshold": threshold,
        "engines": fleet_rows,
        "summary": {
            "engines_monitored": len(test_pred),
            "mean_pred_rul": round(float(test_pred["pred_final"].mean()), 1),
            "critical_count": int((test_pred["pred_final"] < threshold).sum()),
            "test_mae": round(float(test_metrics.loc[test_metrics["model"] == "Final", "MAE"].iloc[0]), 1),
            "n_features": meta["n_features"],
            "model_name": meta["model_name"],
        },
    }

    engine_payload: dict = {"engines": {}, "life_stages": {"early": [], "mid": [], "late": []}}
    for uid in sorted(train["unit_number"].unique()):
        eng = train[train["unit_number"] == uid].sort_values("time_in_cycles")
        if eng.empty:
            continue
        preds = model.predict(eng[features]).tolist()
        stage = str(eng["life_stage"].iloc[0])
        engine_payload["life_stages"].setdefault(stage, []).append(int(uid))

        sensor_data = {}
        for s in SENSORS:
            sensor_data[s] = eng[s].astype(float).tolist()
        roll_col = "sensor_11_roll20"
        engine_payload["engines"][str(uid)] = {
            "unit_number": int(uid),
            "life_stage": stage,
            "cycles": eng["time_in_cycles"].astype(int).tolist(),
            "sensors": sensor_data,
            "sensor_11_roll20": eng[roll_col].astype(float).tolist() if roll_col in eng.columns else [],
            "pred_rul": [round(float(x), 2) for x in preds],
            "last_rul": round(float(preds[-1]), 1),
            "status": rul_band(float(preds[-1]), threshold),
        }

    fi_payload = fi.head(15)[["feature", "perm_importance_mean"]].to_dict(orient="records")
    recs_payload = recs.to_dict(orient="records")

    (OUT / "fleet.json").write_text(json.dumps(fleet_payload, indent=2), encoding="utf-8")
    (OUT / "engines.json").write_text(json.dumps(engine_payload, indent=2), encoding="utf-8")
    (OUT / "feature_importance.json").write_text(json.dumps(fi_payload, indent=2), encoding="utf-8")
    (OUT / "recommendations.json").write_text(json.dumps(recs_payload, indent=2), encoding="utf-8")
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Exported dashboard JSON to {OUT}")
    print(f"  fleet: {len(fleet_rows)} engines")
    print(f"  engines: {len(engine_payload['engines'])} trajectories")


if __name__ == "__main__":
    main()
