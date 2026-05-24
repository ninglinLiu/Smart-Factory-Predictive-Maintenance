# IOT106TC Big Data Analytics — Assignment 2
## Smart Factory Predictive Maintenance: Predictive Modeling & Interactive Dashboard

**Module:** IOT106TC Big Data Analytics  
**Assignment:** Assignment 2 — Predictive Modeling & Interactive Dashboard  
**Scenario:** Scenario 1 — Smart Factory Predictive Maintenance  
**Dataset:** NASA C-MAPSS FD001  
**Continuity:** Builds directly on Assignment 1 EDA ([Assignment1_SmartFactory_Report.pdf](Assignment1_SmartFactory_Report.pdf))

---

## Quick Start

```bash
pip install -r requirements.txt
python scripts/run_assignment2_pipeline.py
python scripts/generate_notebooks.py
streamlit run dashboard/app.py
python scripts/build_assignment2_report_pdf.py
python scripts/verify_submission.py
python scripts/package_submission.py --student-id YOUR_ID
```

---

## Project Structure

```
IOT106TC/
├── data/
│   ├── raw/                    # NASA FD001 raw files (train, test, RUL)
│   └── processed/
│       ├── SmartFactory_cleaned.csv      # From Assignment 1
│       ├── SmartFactory_modeling.csv     # A2 feature-engineered train set
│       └── SmartFactory_test_features.csv
├── notebooks/
│   ├── 01_feature_engineering.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_model_evaluation.ipynb
├── src/                        # Reusable Python modules
├── models/                     # Saved final_model.pkl + metadata
├── dashboard/app.py            # Streamlit interactive dashboard
├── outputs/                    # Metrics tables, feature catalog
├── figures/                    # A2 evaluation figures (300 DPI)
├── reports/                    # Assignment 2 report + AI log
└── scripts/                    # Pipeline, verification, packaging
```

---

## Assignment 1 Continuity

- Same scenario and dataset (NASA FD001)
- A1 EDA identified top sensors (sensor_11, sensor_4, sensor_12, etc.)
- A2 uses deployable features only — no RUL leakage
- Engine-grouped cross-validation prevents temporal data leakage

---

## Dashboard

Run: `streamlit run dashboard/app.py`

Pages: Fleet Overview | Engine Detail | Model Insights | Recommendations

Requirements met: 5 KPIs, 3+ filters, interactive Plotly charts, maintenance recommendations.

---

## Submission

See `scripts/package_submission.py` for ZIP packaging per coursework specification.

**Note:** Presentation video (Part 4, 10 points) is not included — see `deliverables/video/VIDEO_SCRIPT.md` for a ready-to-record storyboard.
