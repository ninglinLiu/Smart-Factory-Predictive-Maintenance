# Final Compliance Checklist
## IOT106TC Big Data Analytics — Assignment 1
## Smart Factory Predictive Maintenance

**Generated:** Updated after notebook execution, report finalisation, and PDF build  
**Status:** Core deliverables present. Review wording and citation style before LMS upload.

---

## Quick status

| Item | Location |
|------|----------|
| PDF report (**11 pages**, A4) | `reports/Assignment1_SmartFactory_Report.pdf` |
| Markdown source (figures embedded via relative paths) | `reports/Assignment1_SmartFactory_Report.md` |
| Rebuild PDF | `python scripts/build_assignment_report_pdf.py` |

---

**None** — `data/raw/train_FD001.txt` is present and the notebook pipeline has been executed.

---
## A. Dataset and Scenario

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| A1 | Smart Factory scenario selected | ✅ DONE | Confirmed in all project files |
| A2 | NASA FD001 dataset chosen | ✅ DONE | Documented in README and report |
| A3 | `train_FD001.txt` file present in `data/raw/` | ✅ DONE | NASA zip extracted |

---

## B. Deliverables

| # | Deliverable | File | Status |
|---|-------------|------|--------|
| B1 | Jupyter Notebook | `notebooks/Assignment1_SmartFactory_EDA.ipynb` | ✅ DONE |
| B2 | Cleaned CSV dataset | `data/processed/SmartFactory_cleaned.csv` | ✅ DONE |
| B3 | Report markdown (**final**) | `reports/Assignment1_SmartFactory_Report.md` | ✅ DONE |
| B3b | Report **PDF** (11 pg) | `reports/Assignment1_SmartFactory_Report.pdf` | ✅ DONE |
| B4 | AI Collaboration Log | `reports/AI_Collaboration_Log.md` | ✅ DONE |
| B5 | Figure 1 — Data quality | `figures/Figure_01_data_quality_missingness.png` | ✅ DONE |
| B6 | Figure 2 — Engine lifetime | `figures/Figure_02_engine_lifetime_distribution.png` | ✅ DONE |
| B7 | Figure 3 — RUL distribution | `figures/Figure_03_rul_distribution.png` | ✅ DONE |
| B8 | Figure 4 — Lifecycle examples | `figures/Figure_04_engine_lifecycle_examples.png` | ✅ DONE |
| B9 | Figure 5 — Sensor-RUL correlation | `figures/Figure_05_sensor_rul_correlation.png` | ✅ DONE |
| B10 | Figure 6 — Key sensor trends | `figures/Figure_06_key_sensor_trends.png` | ✅ DONE |
| B11 | Figure 7 — Life-stage boxplots | `figures/Figure_07_life_stage_sensor_boxplots.png` | ✅ DONE |
| B12 | Figure 8 — Short vs long life | `figures/Figure_08_short_vs_long_life_engines.png` | ✅ DONE |
| B13 | Figure 9 — Correlation heatmap | `figures/Figure_09_correlation_heatmap.png` | ✅ DONE |
| B14 | Figure 10 — PCA | `figures/Figure_10_pca_life_stage.png` | ✅ DONE |
| B15 | Data quality summary table | `outputs/data_quality_summary.csv` | ✅ DONE |
| B16 | Feature summary table | `outputs/feature_summary.csv` | ✅ DONE |
| B17 | Sensor-RUL correlation table | `outputs/sensor_rul_correlation.csv` | ✅ DONE |
| B18 | Life-stage shift table | `outputs/sensor_life_stage_shift.csv` | ✅ DONE |
| B19 | Engine-level summary table | `outputs/engine_level_summary.csv` | ✅ DONE |
| B20 | Key findings table | `outputs/key_findings_table.csv` | ✅ DONE |
| B21 | Recommendations table | `outputs/recommendations_table.csv` | ✅ DONE |
| B22 | README with instructions | `README.md` | ✅ CREATED |
| B23 | requirements.txt | `requirements.txt` | ✅ CREATED |

---

## C. Requirement Coverage

| # | Requirement | Notebook Coverage | Report Coverage | Status |
|---|-------------|------------------|----------------|--------|
| C1 | At least 8 engines analysed | Section 8 (Fig 4 — 8 representative engines), Section 13 (engine groups) | Section 4.1, 4.4 | ✅ IN NOTEBOOK |
| C2 | At least 10 sensors explored in depth | Section 9 (all 21 screened); top 10 used in rolling features and PCA | Section 4.2, 4.3 | ✅ IN NOTEBOOK |
| C3 | RUL calculated and explained | Section 4, with formula, validation, and sanity check | Section 3.2 | ✅ IN NOTEBOOK |
| C4 | Data quality assessment included | Section 3 (missing, duplicates, outliers, variance) | Section 2.3, 3.1 | ✅ IN NOTEBOOK |
| C5 | Cleaning strategy justified | Section 3 (conservative domain-aware approach) | Section 3.1 | ✅ IN NOTEBOOK |
| C6 | Feature engineering included | Section 4 (RUL, cycle_ratio, life_stage, near_failure, capped_RUL, rolling means) | Section 3.3 | ✅ IN NOTEBOOK |
| C7 | EDA visualisations (10 figures) | Sections 5–15 (Figures 1–10) | Section 4 (all figures referenced) | ✅ IN NOTEBOOK |
| C8 | 5–7 key findings | Section 17 (7 structured findings) | Section 5.1 (7 findings) | ✅ IN NOTEBOOK + REPORT |
| C9 | 5 business recommendations | Section 17 (5 recommendations) | Section 5.2 (5 recommendations) | ✅ IN NOTEBOOK + REPORT |
| C10 | Preliminary modeling plan | Section 5.3 and Section 7 of report | Complete in report | ✅ IN REPORT |
| C11 | Assignment 2 continuity statement | `capped_RUL` feature included; rolling means included | Section 7 (complete continuity statement) | ✅ IN REPORT |
| C12 | AI collaboration report | — | `reports/AI_Collaboration_Log.md` (separate file) + Section 6 summary | ✅ CREATED |

---

## D. Integrity Checks

| # | Integrity Requirement | Status | Notes |
|---|----------------------|--------|-------|
| D1 | No fabricated data | ✅ VERIFIED | Notebook raises FileNotFoundError if data is missing — no synthetic data |
| D2 | No fake references | ✅ VERIFIED | References in report are real published papers (Saxena 2008, Ramasso 2014) |
| D3 | No unsupported numerical claims | ✅ VERIFIED | Report findings use [UPDATE] markers where actual values must be filled in; all fixed claims are structural |
| D4 | No automatic deletion of degradation outliers | ✅ VERIFIED | Notebook uses 3×IQR for flagging only; no `drop()` applied to outlier rows |
| D5 | No exact AI contribution percentage invented | ✅ VERIFIED | AI log uses descriptive language only; no percentage claims |
| D6 | No placeholder text in AI Collaboration Log | ✅ VERIFIED | AI log is complete and self-contained |
| D7 | No placeholder text in notebook code | ✅ VERIFIED | All notebook code is executable Python |
| D8 | Report numbers will match notebook outputs | ⏳ PENDING | Report contains [UPDATE] markers where actual computed values must be inserted after running notebook |
| D9 | RUL formula validated (reaches 0 at failure) | ⏳ PENDING (code is present in notebook) | Notebook sanity check in Section 4 confirms this when run |

---

## E. Post-Notebook-Run Student Review Checklist

After running the notebook, complete the following before submission:

- [ ] **Replace all `[UPDATE: ...]` markers** in `reports/Assignment1_SmartFactory_Report.md` with actual computed values
- [ ] **Review all 10 figures** in `figures/` — remove any that are unclear or uninformative
- [ ] **Check Executive Summary** — update with actual engine count, lifecycle range, and key sensor findings
- [ ] **Check Table 2.3** (data quality table) — fill with actual row counts, missing values, duplicate count
- [ ] **Check Table 3.4** (before/after cleaning) — fill with actual values
- [ ] **Check Section 4.2** — fill in univariate descriptions for the 5 most informative sensors
- [ ] **Check Section 4.3** — fill in actual top-5 sensor names and correlation values
- [ ] **Check Section 4.4** — fill in actual lifecycle mean values and comparison summary
- [ ] **Check Section 4.6** — fill in actual PCA cumulative variance
- [ ] **Check all 7 Findings** — replace bracketed values with actual statistics
- [ ] **Check all 5 Recommendations** — verify every claim is supported by a figure or table
- [ ] **Review AI Collaboration Log** — add any additional reflections based on actual notebook run experience
- [ ] **Verify word count** of Critical Reflection section (>200 words required)
- [ ] **Check figure numbering** — all figures cited in report text match actual saved filenames
- [ ] **Final submission format** — convert report markdown to PDF (Round 2 task)

---

## F. Round 1 Summary

**Created in Round 1:**

| File | Status |
|------|--------|
| `data/raw/` (folder) | ✅ Created |
| `data/processed/` (folder) | ✅ Created |
| `notebooks/` (folder) | ✅ Created |
| `figures/` (folder) | ✅ Created |
| `outputs/` (folder) | ✅ Created |
| `reports/` (folder) | ✅ Created |
| `README.md` | ✅ Complete — includes data download instructions |
| `requirements.txt` | ✅ Complete |
| `notebooks/Assignment1_SmartFactory_EDA.ipynb` | ✅ Complete — full pipeline, ready to run |
| `reports/Assignment1_SmartFactory_Report.md` | ✅ Draft — structural sections complete; EDA findings need [UPDATE] values after notebook run |
| `reports/AI_Collaboration_Log.md` | ✅ Complete |
| `outputs/final_compliance_checklist.md` | ✅ This file |

**Remaining for Round 2:**
- Download NASA C-MAPSS data and place in `data/raw/`
- Run notebook from top to bottom
- Verify all outputs are generated correctly
- Fill in [UPDATE] values in the report
- Student review and revision of all content
- PDF export of final report
