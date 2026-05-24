# Dashboard Screenshots — Submission Guide

Coursework 2 requires **5–8 screenshots** of the interactive dashboard (different views/filters).

## Where to save files

Save all PNG files **here**:

```
dashboard/screenshots/
```

Recommended filenames (capture after `streamlit run dashboard/app.py`):

| File | What to capture |
|------|-----------------|
| `S01_fleet_overview_kpis.png` | Fleet Overview — full page with 5 KPI cards |
| `S02_fleet_risk_histogram.png` | Fleet Overview — risk histogram + color bands |
| `S03_fleet_scatter_actual_pred.png` | Fleet Overview — actual vs predicted scatter |
| `S04_fleet_risk_table_drilldown.png` | Fleet risk table with R/Y/G badges |
| `S05_engine_detail_sensor_rul.png` | Engine Detail — sensor trend + RUL trajectory |
| `S06_engine_detail_maintenance_alert.png` | Engine Detail — red/critical maintenance alert |
| `S07_model_insights_importance.png` | Model Insights — feature importance chart |
| `S08_recommendations_page.png` | Recommendations — expanded priority panel |

## Where screenshots are used (besides PDF)

| Location | Purpose |
|----------|---------|
| **`reports/Assignment2_Report.md` §5** | Embedded in PDF report with captions (annotations) |
| **`Assignment2_Code_[StudentID].zip`** | Inside `dashboard/screenshots/` — code/dashboard deliverable |
| **Presentation video (MP4)** | Screen recording; screenshots optional as slides |
| **LMS / marker review** | Visible in PDF report + code ZIP |

You do **not** need a separate folder under `figures/` if report embeds from `../dashboard/screenshots/`.

## Tips

- Use 1920×1080 window; Windows `Win+Shift+S` or browser full-page capture.
- Show **filters changed** between at least 2 screenshots (proves interactivity).
- Add **1 sentence annotation** in the report caption for each figure (what the marker should notice).
