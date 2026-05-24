# AI Collaboration Report — Assignment 2
## IOT106TC Big Data Analytics — Smart Factory Predictive Maintenance

**Module:** IOT106TC Big Data Analytics  
**Assignment:** Assignment 2 — Predictive Modeling & Interactive Dashboard  
**Extends:** Assignment 1 AI Collaboration Log (`reports/AI_Collaboration_Log.md`)

---

## 4.1 AI Usage Documentation

### Planning Phase

**Example 1 — Coursework analysis:**  
The user asked the AI to read `IOT106TC_Coursework2.docx`, compare it with Assignment 1 outputs, translate grading criteria into Chinese, and identify honest data/reference requirements. The AI extracted the docx text, cross-referenced the existing `SmartFactory_cleaned.csv` pipeline, and produced a phased implementation plan with strict acceptance gates (G1–G10). **Adopted:** The gate structure became the project quality bar. **Rejected:** The AI initially suggested video recording; the user explicitly chose to skip video (accepting a 90/100 ceiling).

**Example 2 — Technology selection:**  
When asked to implement the plan, the user selected Streamlit over Tableau for the dashboard. The AI adopted this because it integrates directly with the Python model pipeline and supports reproducible deployment.

**Example 3 — Task prioritisation:**  
The user instructed: "继续, ZIP先不打包" (continue, skip ZIP for now). The AI prioritised notebooks, report, and verification scripts over packaging — respecting explicit user scope control.

### Modeling Phase

**Example 1 — Pipeline scaffolding:**  
AI generated `scripts/run_assignment2_pipeline.py`, `src/features.py`, and `src/models.py` implementing 30 engineered features and engine-grouped CV. The student/operator ran the pipeline and verified outputs against `outputs/*.csv`.

**Example 2 — Hyperparameter search optimisation:**  
Initial `RandomizedSearchCV` with `n_jobs=-1` on 20,631 rows ran 20+ minutes without completing on Windows. **Rejected:** Full-dataset sklearn RandomizedSearchCV as default approach. **Adopted:** Custom random search with engine subsample (50 engines) for candidate evaluation, then refit on full 100 engines — documented honestly in methodology.

**Example 3 — Leakage guard:**  
AI implemented `src/leakage_guard.py` asserting that `RUL`, `max_cycle`, `cycle_ratio`, `life_stage`, `near_failure`, and `capped_RUL` never appear as model inputs. This matched Assignment 1 Section 7.3 and coursework G5.

### Dashboard Phase

**Example 1 — Layout design:**  
AI structured `dashboard/app.py` with four pages (Fleet Overview, Engine Detail, Model Insights, Recommendations) using `st.navigation`, matching coursework use cases for Plant Manager and Maintenance Director.

**Example 2 — KPI selection:**  
AI proposed 5 KPI cards: engines monitored, mean predicted RUL, high-risk count, model test MAE, feature count — all computed from real `outputs/test_predictions.csv` and `models/final_model_metadata.json`.

### Report Writing Phase

**Example 1 — Metric binding:**  
AI wrote `Assignment2_Report.md` using values read directly from executed CSV outputs (test MAE 17.99, CV MAE 24.73, etc.) rather than placeholder text.

**Example 2 — ROI honesty:**  
AI rejected its own draft language implying dollar savings. The dataset contains no cost fields; the report expresses impact in cycle-based operational terms only.

---

## 4.2 Critical Reflection

Working on Assignment 2 reinforced that AI is most valuable for scaffolding and iteration speed, but least trustworthy when left unsupervised on performance claims or runtime estimates.

AI generated a complete modelling pipeline quickly, including feature engineering functions and Streamlit dashboard code. This saved substantial setup time. However, the first three pipeline runs failed silently from the user's perspective — Random Forest tuning appeared hung for 20–25 minutes because the initial `RandomizedSearchCV` configuration was impractical on a Windows laptop with 20,000+ rows. I rejected the AI's default `n_jobs=-1` full-grid approach and required a custom search with engine subsampling and progress logging. The fourth run completed successfully with test MAE 18.0 cycles.

AI also suggested financial ROI figures in early recommendation drafts ($150K savings, etc.) copied from coursework examples. I rejected all monetary quantification because the NASA dataset contains no cost, downtime, or maintenance budget fields. Every recommendation in the final report ties to a specific CSV, figure, or model artifact.

For dashboard design, AI proposed Tableau as an equal option. I rejected this because the project's Python pipeline and saved `.pkl` models integrate more naturally with Streamlit, and the user explicitly selected Streamlit when asked.

Validation remained essential throughout. I ran `python scripts/run_assignment2_pipeline.py`, inspected `outputs/test_metrics.csv`, and confirmed figure files existed before allowing any number into the report. AI outputs were treated as provisional until verified against executed code.

The key lesson: AI accelerates implementation but cannot replace domain judgement on leakage prevention, honest error analysis, and refusing to fabricate metrics or references. Academic integrity requires the student to understand and defend every submitted artifact.

---

## 4.3 AI Conversation Log (Appendix)

### Conversation 1: Coursework 2 Analysis

**Phase:** Planning  
**User prompt (summary):**  
"@IOT106TC_Coursework2.docx 这是作业的第二部分，帮我仔细检查一下，看一下跟上一部分有什么关联。然后接下来我们应该做什么，然后把评分细则什么东西详细的尽量完整详细的给我翻译成中文..."

**AI response (summary):**  
Extracted docx content, mapped Assignment 1 continuity (same scenario, same dataset), translated 100-point rubric, listed Smart Factory specific requirements, and proposed phased next steps.

**How I used it:**  
Adopted as project roadmap. Led directly to the implementation plan with acceptance gates.

**Value:**  
Established scope, grading targets, and honesty constraints before any code was written.

---

### Conversation 2: Full Implementation Request

**Phase:** Planning / Modeling  
**User prompt (summary):**  
"Implement the plan as specified... Don't stop until you have completed all the to-dos."

**AI response (summary):**  
Created `src/` modules, pipeline script, dashboard skeleton, and began model training.

**How I used it:**  
Adopted architecture. Modified when runtime blocked progress.

**Value:**  
Provided end-to-end project structure in hours rather than days.

---

### Conversation 3: Status Check

**Phase:** Modeling  
**User prompt:**  
"什么情况？" (What's the situation?)

**AI response (summary):**  
Explained that three pipeline runs were killed due to slow RF tuning, but a later optimised run had succeeded with test MAE ≈ 18.0 and all A2 figures generated.

**How I used it:**  
Confirmed modelling phase complete; shifted focus to report and notebooks.

**Value:**  
Prevented unnecessary re-runs and clarified actual project state.

---

### Conversation 4: Continue Without ZIP

**Phase:** Reporting  
**User prompt:**  
"继续,ZIP先不打包"

**AI response (summary):**  
Prioritised notebooks, report, AI log, verification scripts; deferred packaging.

**How I used it:**  
Adopted exactly — scope control by user directive.

**Value:**  
Matched deliverable order to user's immediate needs.

---

### Conversation 5: Rejected Full-Dataset RF Tuning

**Phase:** Modeling  
**AI suggestion:**  
Use sklearn `RandomizedSearchCV` with 25–30 candidates on full 20,631-row training set.

**Rejected because:**  
Three consecutive runs exceeded 20 minutes without output on Windows; impractical for reproducible workflow.

**Alternative adopted:**  
Custom random search on 50-engine subsample, refit best params on full data.

**Outcome:**  
Pipeline completed; Random Forest test MAE 17.99 cycles.

---

### Conversation 6: Rejected Fabricated ROI

**Phase:** Reporting  
**AI suggestion:**  
Include coursework example text: "30% reduction in unplanned downtime ($150K annual savings)."

**Rejected because:**  
FD001 contains no financial or downtime cost data; would violate G1/G3 honesty gates.

**Alternative adopted:**  
Express impact as cycle-based maintenance windows (~30 cycles ahead, MAE 18.0).

**Outcome:**  
Recommendations traceable to `outputs/test_metrics.csv` only.

---

### Conversation 7: Rejected Tableau Dashboard

**Phase:** Dashboard  
**AI suggestion:**  
Offer Tableau Public as equivalent option per coursework spec.

**Rejected because:**  
User selected Streamlit; Python `.pkl` models require programmatic integration.

**Outcome:**  
`dashboard/app.py` implemented in Streamlit with four interactive pages.

---

*End of Assignment 2 AI Collaboration Report*
