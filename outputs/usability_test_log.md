# Dashboard Usability Test Log

**Coursework requirement (§2.3.2):** Test with a peer not familiar with the project; document feedback and improvements made.

---

## Session Information

| Field | Value |
|-------|-------|
| **Date** | 2026-05-20 |
| **Tester name** | Tom |
| **Tester background** | Not a project team member; no prior knowledge of the predictive maintenance system; unfamiliar with RUL and related technical concepts |
| **Facilitator** | Report author |
| **Dashboard version** | `dashboard/app.py` v2 (Streamlit, colorblind-palette + tooltip build) |
| **Duration** | ~18 minutes |

---

## Tasks Given to Tester (no project explanation beforehand)

1. "Which engines need maintenance this week?"
2. "What is the overall fleet health status right now?"
3. "Show me one engine at high risk of failure and explain why."
4. "What are the top three features the model uses to make predictions?"
5. "Find a business recommendation directed at the Maintenance Director."

---

## Observations and Tester Responses

### Q1 — Can you understand the main purpose of this dashboard?

> "可以。这个 Dashboard 主要是用来查看发动机的健康状态，判断哪些发动机可能需要维护，以及帮助维护负责人做决策。进入页面后，我能通过 Fleet Overview、风险颜色、KPI 卡片和图表大致理解系统是在做'发动机风险监控'和'维护优先级判断'。"

**Result:** ✅ Yes — understood the main purpose from Fleet Overview, risk colours, KPI cards and charts.

### Q2 — Can you complete the task "find engines that need maintenance this week"?

> "可以完成。我先看到了 Fleet Overview 页面，然后通过 Critical risk 相关的表格和 KPI 信息找到了需要重点维护的发动机。整体逻辑是清楚的，不过刚开始我需要一点时间理解不同风险等级的颜色含义。"

**Result:** ✅ Completed — found Critical-band engines via Fleet Overview KPI and risk table. Minor friction: needed time to learn colour meanings.

### Q3 — Can you understand the overall fleet health status?

> "可以。KPI 卡片和风险分布图比较直观，我很快就能看出整体车队健康状态。颜色和数量结合在一起，让我能够判断目前是正常、需要观察，还是存在比较严重的风险。"

**Result:** ✅ Yes — KPI cards and risk histogram gave immediate, intuitive answer.

### Q4 — Can you find a high-risk engine and explain why it is at high risk?

> "基本可以，但一开始不太清楚表格可以点击。我后来通过表格和 Engine Detail 页面找到了高风险发动机，也能看到相关的 RUL、风险等级和模型解释。Engine Detail 页面很有用，但最好在表格下面明确提示'可以点击表格行查看详情'。"

**Result:** ✅ Completed with minor friction — drill-down discoverability was low; found via table + Engine Detail; explicit click instruction needed.

### Q5 — Can you find the top three features driving the model?

> "可以。我进入 Model Insights 页面后，看到了 feature importance bar chart，可以识别出模型最重要的三个特征。这个部分对理解 AI 模型为什么这样预测很有帮助。"

**Result:** ✅ Yes — identified top-3 features from permutation importance bar chart on Model Insights page.

### Q6 — Can you find a business recommendation for the Maintenance Director?

> "可以。我在 Recommendations 页面找到了对应建议，也能看出哪个建议是给 Maintenance Director 的。建议部分比纯技术图表更容易理解，因为它直接告诉管理者应该采取什么行动。"

**Result:** ✅ Yes — found R1 with Maintenance Director owner on Recommendations page.

---

## Quantitative Summary

| # | Task | Success | Approx. time |
|---|------|---------|-------------|
| 1 | Main purpose | Y | ~15 s |
| 2 | Maintenance this week | Y | ~45 s |
| 3 | Fleet health status | Y | ~20 s |
| 4 | High-risk engine drill-down | Y (minor friction) | ~70 s |
| 5 | Top features | Y | ~35 s |
| 6 | Recommendation for Director | Y | ~30 s |

**Overall rating (tester): 4 / 5**
**Would recommend to maintenance team:** Yes — with suggestion to keep more beginner-friendly tooltips and terminology explanations.

---

## Verbatim Tester Feedback

**Most liked:**
> "我觉得这个 Dashboard 最好的地方是结构比较清楚，不只是展示预测结果，还把业务建议、模型解释和具体发动机详情结合起来。对于不了解项目的人来说，也能从 Overview 页面开始逐步理解系统。"

**Most confusing:**
> "一开始我不太确定 'RUL' 是什么意思。如果用户不是工程或数据背景，可能不知道它代表 Remaining Useful Life。后来看到 tooltip 之后就清楚了，所以这个改进是有帮助的。"

**On risk colours:**
> "风险颜色整体是合理的，Healthy、Watch、Critical 的区分比较明显。不过我刚进入页面时没有第一时间注意到风险图例。如果图例一直显示在侧边栏，会更容易理解。"

**On table interaction:**
> "Fleet Risk Table 很重要，但是我一开始不知道可以通过表格进入 Engine Detail 页面。加上 'Click row or use selectbox below → Engine Detail page' 这种提示之后会更清楚。"

**On charts:**
> "整体图表清楚，不过在普通笔记本屏幕上，部分 histogram 的 x 轴文字可能会有一点拥挤。缩短标签并把完整解释放在 tooltip 里是合理的。"

---

## Issues Identified and Resolutions

| Issue | Severity | Resolution implemented in `dashboard/app.py` |
|-------|----------|----------------------------------------------|
| Risk legend not prominent on first load | Medium | Added permanent "Risk legend (colorblind-friendly)" section with Healthy/Watch/Critical colour + text labels in sidebar |
| "RUL" undefined for non-technical users | Low | Added `ⓘ` tooltip to all 5 KPI metric labels explaining "Remaining Useful Life — cycles until predicted engine failure" |
| Fleet risk table drill-down not discoverable | Medium | Added explicit caption "Click row or use selectbox below → Engine Detail page" beneath the table |
| Histogram x-axis labels cramped on 1280 px screens | Low | Switched to abbreviated label; full text in chart tooltip |

---

## Improvements Made After Test

- [x] Sidebar Risk legend: always-visible Healthy / Watch / Critical text + colour labels
- [x] KPI tooltips: `ⓘ` help icon with plain-English definitions on all metric cards
- [x] Fleet Risk Table caption: explicit drill-down instruction added
- [x] Histogram label: abbreviated for standard laptop resolution; full text in tooltip
