⚠️ **NOT a submission file.** Convert manually to `.pptx` or use as speaker notes when recording video. Do not upload this `.md` to LMS.

---
marp: true
theme: default
paginate: true
title: IOT106TC Assignment 2 — Smart Factory Predictive Maintenance
---

# Smart Factory Predictive Maintenance
## IOT106TC Assignment 2 — NASA C-MAPSS FD001

**Scenario 1:** Predictive Maintenance  
**Student presentation deck** (companion to VIDEO_SCRIPT.md)

---

## Problem Statement

- Turbofan engines monitored by 21 IoT sensor channels
- Calendar maintenance is inefficient (lifetimes: 128–362 cycles)
- Assignment 1 EDA: sensor_11 |r| = 0.696 with RUL

---

## Assignment 1 → 2 Continuity

| A1 Output | A2 Usage |
|-----------|----------|
| SmartFactory_cleaned.csv | Modelling input |
| Top sensor ranking | Feature selection |
| Engine-grouped EDA | CV strategy |
| near_failure band (RUL≤30) | Classification target |

---

## Feature Engineering

**30 documented features:**
- Rolling slopes, std, min/max
- Lag features (1, 5, 10 cycles)
- Sensor interactions (sensor_4 × sensor_11)
- PCA scores, EWMA, anomaly counters

**47 deployable features** after correlation pruning

---

## Models Evaluated

| Model | CV MAE | Test MAE | Test R² |
|-------|--------|----------|---------|
| Ridge (baseline) | 30.6 | 26.2 | 0.46 |
| **Random Forest** | **24.7** | **18.0** | **0.68** |
| Gradient Boosting | 25.2 | 18.8 | 0.64 |

Engine-grouped 5-fold CV · 25 hyperparameter candidates each

---

## Final Model: Random Forest

- **Test MAE:** 18.0 cycles
- **Top features:** time_in_cycles, pca_score_1, sensor_4_min20
- **Near-failure classifier:** ROC-AUC 0.997

---

## Dashboard (Streamlit)

1. **Fleet Overview** — KPIs + risk distribution
2. **Engine Detail** — sensor trends + RUL trajectory
3. **Model Insights** — feature importance + errors
4. **Recommendations** — 5 prioritised actions

`streamlit run dashboard/app.py`

---

## Top Recommendations

1. Predictive scheduling (RUL < 30 cycles)
2. Prioritise top sensor monitoring
3. Engine-grouped retraining protocol
4. Dual near-failure alert layer
5. Investigate high-error engines

---

## Expected Operational Impact

- Proactive maintenance ~**30 cycles** before failure
- Reduced calendar over-maintenance
- Data-driven prioritisation for maintenance teams

*No financial figures — dataset contains no cost data*

---

## Thank You

**Deliverables:** Report PDF · Code · Dashboard · Notebooks  
**Assignment 1 reference:** Included as appendix
