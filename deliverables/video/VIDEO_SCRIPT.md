⚠️ **NOT a submission file.** Record your own 5–7 minute MP4 per coursework Part 4. Do not upload this markdown to LMS.
## Smart Factory Predictive Maintenance — Self-Recording Storyboard

**Target length:** 5–7 minutes  
**Format:** Screen recording of Streamlit dashboard + voiceover  
**Note:** Video not recorded by AI — use this script to recover Part 4 (10 points).

---

## Segment 1: Project Background (0:00 – 1:00)

**[Slide 1 — Title]**

> "Hello. This is my IOT106TC Assignment 2 project: Predictive Modeling and Interactive Dashboard for Smart Factory Predictive Maintenance, using the NASA C-MAPSS FD001 dataset."

**[Slide 2 — Problem]**

> "In Assignment 1, I analysed 100 turbofan engines and found that sensor channels like sensor_11 correlate strongly with Remaining Useful Life. Calendar-based maintenance is inefficient because engine lifetimes vary from 128 to 362 cycles."

**[Slide 3 — Continuity]**

> "Assignment 2 builds directly on that EDA. I used the same cleaned dataset, engineered 30 new features, trained predictive models, and built an interactive Streamlit dashboard for maintenance stakeholders."

---

## Segment 2: Model Development & Results (1:00 – 3:00)

**[Screen: `outputs/test_metrics.csv` or report table]**

> "I trained three model families: Ridge regression as a baseline, Random Forest, and Gradient Boosting. All validation used engine-grouped 5-fold cross-validation — entire engines held out, never individual rows — to prevent data leakage."

> "Random Forest performed best with cross-validation MAE of 24.7 cycles and held-out test MAE of 18.0 cycles, with R-squared 0.68 on the official NASA test set."

**[Screen: Figure_A2_01 actual vs predicted]**

> "This scatter plot shows predicted versus true RUL on 100 unseen test engines. Most points cluster near the diagonal, though some outlier engines show larger errors — documented in my error analysis."

**[Screen: Figure_A2_03 feature importance]**

> "The top features are time in cycles and PCA-derived degradation scores, consistent with Assignment 1 findings. I also deployed a near-failure classifier with ROC-AUC 0.997 for dual-threshold alerting."

---

## Segment 3: Dashboard Demonstration (3:00 – 6:00)

**[Screen: Run `streamlit run dashboard/app.py`]**

> "Now I'll demonstrate the interactive dashboard."

**[Fleet Overview page]**

> "The Fleet Overview shows five KPIs: engines monitored, mean predicted RUL, high-risk count below 30 cycles, model test MAE, and feature count. The histogram shows the risk distribution across the test fleet."

**[Engine Detail page — select engines, adjust threshold]**

> "On Engine Detail, I can filter specific engines, adjust the RUL risk threshold, and view sensor trends with 20-cycle rolling means alongside predicted RUL trajectories. When predicted RUL drops below the threshold, the dashboard displays a maintenance recommendation."

**[Model Insights page]**

> "Model Insights shows feature importance and the worst prediction errors for transparency."

**[Recommendations page]**

> "The Recommendations page lists five prioritised business actions with evidence links to my analysis outputs."

---

## Segment 4: Business Impact & Next Steps (6:00 – 7:00)

**[Slide — Recommendations summary]**

> "My top recommendations are: implement predictive scheduling when RUL falls below 30 cycles, prioritise monitoring of top sensor channels, mandate engine-grouped retraining, deploy dual near-failure alerts, and investigate high-error engines."

> "Expected operational impact: maintenance teams can act approximately 30 cycles before estimated failure, reducing unplanned downtime without over-maintaining healthy equipment."

> "Thank you."

---

## Recording Checklist

- [ ] Clear audio, minimal background noise
- [ ] Screen resolution 1920×1080 or higher
- [ ] Show dashboard interactivity (filters, page navigation)
- [ ] Total duration 5–7 minutes
- [ ] Save as `Assignment2_Presentation_[StudentID].mp4`
