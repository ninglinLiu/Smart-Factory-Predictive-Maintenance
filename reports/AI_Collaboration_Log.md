# AI Collaboration Report
## IOT106TC Big Data Analytics — Assignment 1

**Report type:** Mandatory AI Use Disclosure  
**Module:** IOT106TC Big Data Analytics  
**Assignment:** Assignment 1 — Exploratory Data Analysis Report  
**Student scenario:** Smart Factory Predictive Maintenance  

---

## Overview

This document describes how AI assistance was used during the preparation of Assignment 1. AI tools were used to support specific technical tasks — primarily code scaffolding, debugging guidance, visualisation suggestions, and wording refinement for selected sections. All analytical decisions, figure selections, business interpretations, and final report content were reviewed and controlled by the student.

The purpose of this log is to provide an honest, academically responsible account of AI involvement, in compliance with the module's AI use policy.

---

## 1. Data Exploration Phase

**What AI assisted with:**  
AI helped identify the structure of the NASA C-MAPSS FD001 dataset and suggested appropriate column names based on published documentation. Specifically, AI recommended using whitespace-separated loading (`pd.read_csv` with `sep='\s+'`) and assigning the 26 columns as: `unit_number`, `time_in_cycles`, `operational_setting_1/2/3`, and `sensor_1` through `sensor_21`.

AI also suggested the initial set of exploratory checks to perform: dataset shape, number of unique engines, descriptive statistics, data type inspection, missing value counts, and duplicate row detection.

**What the student did:**  
The student verified all suggestions by executing the code and inspecting outputs. Key checks included:
- Confirming the dataset loaded with the expected number of rows and 26 columns.
- Verifying that `unit_number` values ranged from 1 to the expected number of engines.
- Checking that `time_in_cycles` began at 1 for every engine.
- Confirming the absence (or presence) of missing values and duplicates.

The student checked the NASA PCoE / C-MAPSS dataset description used in the coursework materials for context on the operational settings and anonymised sensor channels, rather than relying solely on AI-provided information.

**Student reflection:**  
The AI suggestion for data loading was useful as an initial scaffold. However, the student ran the loading code, checked the output shape, and confirmed column assignments before proceeding. The data loading step required no correction from the AI-suggested approach.

---

## 2. Data Cleaning Phase

**What AI assisted with:**  
AI suggested a standard cleaning checklist appropriate for sensor time-series data:
- Missing value checks per column.
- Exact duplicate row detection and removal.
- Numeric type validation.
- Outlier screening using IQR and z-score methods.
- Identification of near-constant features using standard deviation.

**What the student decided independently:**  
The student rejected automatic outlier removal after considering the domain context. The FD001 dataset is a run-to-failure dataset in which extreme sensor values in the late lifecycle phase may represent genuine degradation signals — not data collection errors. Removing these observations would bias the dataset toward healthy engine states and would be incorrect for a predictive maintenance application.

The student also decided not to delete near-constant sensor channels at this stage. While these channels carry low diagnostic information, removing them before formal feature selection would pre-empt a decision that should be made with explicit statistical feature selection in Assignment 2.

**Student reflection:**  
The AI-suggested cleaning checklist was a useful starting point, but required domain-aware modification. The decision to preserve outliers and near-constant sensors represents an independent analytical judgement that differs from a generic data cleaning approach.

---

## 3. EDA Phase

**What AI assisted with:**  
AI suggested a set of visualisation types appropriate for a predictive maintenance EDA:
- Engine lifetime distribution (histogram, KDE)
- RUL distribution and life-stage breakdown
- Sensor trend plots over normalised lifecycle
- Life-stage boxplots for sensor distribution comparison
- Correlation heatmap
- Short-life vs. long-life engine comparison
- PCA visualisation coloured by life stage and RUL

AI also suggested specific figure layout approaches (e.g., subplot grids, colour-by-stage scatter plots) and the use of 20-cycle rolling means to smooth sensor noise.

**What the student did:**  
The student evaluated each suggested figure type against the assignment requirements and the analytical questions being addressed. Several refinements were made:
- The student selected which sensors to include in the lifecycle trend and boxplot figures based on the sensor-RUL correlation ranking, rather than showing all 21 sensors.
- The student chose to show 8 representative engines in Figure 4 by selecting across lifetime quartiles, rather than selecting arbitrarily or by sequential engine ID.
- The student decided to include PCA as an advanced analytical step only after confirming that it added interpretive value (life-stage separation along PC1) rather than complexity for its own sake.

**Student reflection:**  
AI's visualisation suggestions provided a useful menu of options. Not all suggestions were equally appropriate — some would have produced cluttered or redundant figures. The student applied judgement to select and refine the figure set, prioritising clarity and direct relevance to the business problem.

---

## 4. Business Insights Phase

**What AI assisted with:**  
AI helped translate technical EDA findings into clearer, stakeholder-oriented language. For example, AI suggested framing the near-constant sensor finding in terms of data transmission cost reduction (operationally relevant to an IoT team), and framing the sensor-RUL correlation finding in terms of maintenance alert prioritisation (relevant to the Maintenance Director and Safety Team).

AI also suggested the structured recommendation format used in Section 5 of the report, including fields for action, supporting evidence, expected impact, implementation ease, and priority.

**What the student decided independently:**  
The student reviewed every recommendation against the actual computed findings and removed or revised suggestions that were not supported by the data. In particular:
- Financial quantification of expected savings was avoided because the dataset does not contain cost or downtime data. Generic financial claims were replaced with operational impact descriptions.
- The student re-framed AI-suggested language that was overly generic (e.g., "the company should improve maintenance") into specific, evidence-tied recommendations.
- The student added the "near-failure risk band" recommendation based on the specific near-failure proportion statistic computed in the notebook, which was not in the AI's initial suggestion set.

**Student reflection:**  
AI's business language suggestions were helpful for improving clarity. However, several initial suggestions were either unsupported by the data or were too generic to be academically defensible. Each recommendation in the final report was verified against a specific figure or output table.

---

## 5. Critical Reflection

Working with AI assistance on a technical data analysis project has been a genuinely instructive experience, but one that required more active critical engagement than I initially expected.

AI performed well in areas where the task had a clear, established structure: loading data, computing summary statistics, generating boilerplate visualisation code, and suggesting report sections. For these tasks, AI provided useful starting points that saved time. The code suggestions were syntactically correct in most cases and covered the expected logical steps.

However, AI struggled — or at least required significant student oversight — in areas requiring domain judgement. The most important example was outlier handling. AI's initial suggestion followed a generic data cleaning protocol: identify and remove IQR-flagged outliers. This approach is appropriate for many datasets, but not for a run-to-failure predictive maintenance dataset where late-life extremes carry the most critical information. I had to override this suggestion based on understanding of the domain. This is the kind of judgement that cannot be delegated to AI.

AI also produced visualisation suggestions that were inconsistent in quality. Some suggestions (life-stage boxplots, PCA coloured by RUL) added genuine analytical value. Others were redundant or did not directly serve the business question. I had to evaluate each suggestion against the specific question it was meant to answer and discard those that did not meet this standard.

For some wording suggestions, AI tended to overstate confidence or use vague, generic language. Phrases like "the results clearly show" or "this proves that" had to be replaced with appropriately qualified language ("the results are consistent with," "this supports the interpretation that"). Academic writing requires epistemic precision that such suggestions frequently lacked.

The validation step was essential throughout. I used AI outputs as provisional suggestions only. For code, I ran the relevant cells and inspected the outputs. For text, I checked each numerical claim against the corresponding CSV, figure, or notebook result before deciding whether to include it. Where suggestions were inconsistent with the data, I corrected or discarded them.

The most important lesson from this project is that AI is a capable tool for accelerating technical work, but it is not a substitute for domain knowledge, critical thinking, or careful validation. The responsibility for analytical correctness and academic integrity remains entirely with the student. I used AI as I would use a reference textbook or a code documentation search — as a resource to consult, not a source to copy from uncritically.

---

## 6. Selected AI Interaction Summaries

The following summaries describe the key AI-assisted stages of the project. Exact conversation transcripts are not reproduced, as the interactions involved iterative prompting across multiple sessions. These summaries represent the substance and outcome of each interaction.

---

**Conversation 1: Dataset Structure and Loading**

*Student prompt summary:*  
"I asked AI how to load the NASA FD001 text file, which has no header, and how to assign the correct column names."

*AI assistance summary:*  
"AI suggested using `pd.read_csv` with `sep=r'\s+'` and `header=None`, and naming the columns as `unit_number`, `time_in_cycles`, `operational_setting_1/2/3`, and `sensor_1` through `sensor_21`. It also suggested an initial set of exploratory checks to confirm the load was successful."

*Student validation and reflection:*  
"I executed the loading code and verified the result by checking the dataframe shape, column names, and the distribution of `time_in_cycles` per engine to confirm cycles started at 1. The AI suggestion was correct and did not require modification. The dataset loaded with the expected structure."

---

**Conversation 2: RUL Calculation**

*Student prompt summary:*  
"I asked how to calculate Remaining Useful Life for each engine in a run-to-failure dataset where the last cycle is the failure cycle."

*AI assistance summary:*  
"AI suggested grouping by `unit_number`, extracting the maximum cycle for each engine, and computing RUL as `max_cycle − time_in_cycles`. It also suggested validating that RUL equals zero at each engine's final cycle."

*Student validation and reflection:*  
"I implemented the RUL calculation and ran the sanity check: all 100 engines reached RUL = 0 at their last recorded cycle, confirming the formula was correct. I also manually verified three engines by inspecting their cycle sequences and confirming that the final row had RUL = 0."

---

**Conversation 3: Cleaning and Outlier Handling**

*Student prompt summary:*  
"I asked what cleaning strategy is appropriate for a sensor degradation dataset used in predictive maintenance."

*AI assistance summary:*  
"AI suggested a standard checklist: missing value checks, duplicate removal, data type validation, IQR-based outlier detection, and identification of near-constant features. It initially suggested flagging and removing outliers beyond 2×IQR."

*Student validation and reflection:*  
"I rejected automatic outlier removal. In a run-to-failure dataset, extreme late-life sensor values are the most diagnostically important observations. Removing them would bias the dataset against the very pattern I am trying to detect. I modified the approach to flag outliers for documentation but preserve all rows. The fence was also widened to 3×IQR to reduce false positives. This decision required domain reasoning that AI did not apply on its own."

---

**Conversation 4: EDA Visualisation Design**

*Student prompt summary:*  
"I asked which visualisations would best support a predictive maintenance EDA report covering engine lifecycle, sensor degradation, and RUL analysis."

*AI assistance summary:*  
"AI suggested RUL distributions, engine lifetime histograms, sensor trend plots over normalised lifecycle, life-stage boxplots, short vs. long life engine comparisons, correlation heatmaps, and PCA visualisation. It also suggested the 20-cycle rolling mean as an overlay on sensor trend plots."

*Student validation and reflection:*  
"I evaluated each suggestion against the assignment requirements and the analytical question it was intended to address. I selected 10 figures for inclusion, excluded 2 proposed figures that were redundant or would be cluttered with all 21 sensors, and decided to show the top 6 informative sensors (not all active sensors) in the trend and boxplot figures. The PCA was included only after confirming that it produced meaningful life-stage separation rather than random scatter."

---

**Conversation 5: Business Recommendations**

*Student prompt summary:*  
"I asked AI to help translate the technical EDA results into recommendations that would be meaningful to non-technical stakeholders such as the Plant Manager, Maintenance Director, and Finance Director."

*AI assistance summary:*  
"AI suggested structuring recommendations around maintenance prioritisation, sensor monitoring infrastructure, data volume reduction (deprioritising constant channels), and future RUL prediction model development. It provided a structured format for each recommendation including action, evidence, expected impact, and priority."

*Student validation and reflection:*  
"I revised each recommendation to tie it to a specific figure or computed statistic rather than a generic claim. I removed a suggested recommendation that included a specific percentage reduction in maintenance cost, as the dataset provides no cost data to support such a claim. Every recommendation in the final report is traceable to at least one named figure or output CSV."

---

*End of AI Collaboration Report*
