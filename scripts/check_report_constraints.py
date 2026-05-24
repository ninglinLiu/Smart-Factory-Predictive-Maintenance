"""G8: enforce report word-count and recommendation field constraints."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "Assignment2_Report.md"
AI_LOG = ROOT / "reports" / "AI_Collaboration_Log_A2.md"

REQUIRED_REC_FIELDS = [
    "problem",
    "solution",
    "expected_impact",
    "implementation",
    "timeline",
    "owner",
    "priority",
    "evidence",
]


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def extract_section(text: str, heading: str) -> str:
    pattern = rf"##\s*{re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def check_executive_summary(text: str) -> list[str]:
    errors = []
    section = extract_section(text, "Executive Summary")
    if not section:
        return ["Executive Summary section missing"]
    wc = word_count(section)
    if wc < 150 or wc > 200:
        errors.append(f"Executive Summary word count {wc} (required 150-200)")
    return errors


def check_critical_reflection(text: str) -> list[str]:
    errors = []
    section = extract_section(text, "Critical Reflection")
    if not section:
        # also try within AI log
        return []
    wc = word_count(section)
    if wc < 200:
        errors.append(f"Critical Reflection word count {wc} (required >=200)")
    return errors


def check_placeholders(text: str) -> list[str]:
    if "[UPDATE" in text or "{{" in text:
        found = re.findall(r"\[UPDATE[^\]]*\]|\{\{[^}]+\}\}", text)
        return [f"Unresolved placeholder: {p}" for p in found[:5]]
    return []


def check_recommendations_csv() -> list[str]:
    import pandas as pd

    path = ROOT / "outputs" / "recommendations_table_a2.csv"
    if not path.exists():
        return ["recommendations_table_a2.csv missing"]
    df = pd.read_csv(path)
    errors = []
    if len(df) < 5:
        errors.append(f"Only {len(df)} recommendations (need 5)")
    for col in REQUIRED_REC_FIELDS:
        if col not in df.columns:
            errors.append(f"Recommendation missing column: {col}")
        elif df[col].isna().any() or (df[col].astype(str).str.strip() == "").any():
            errors.append(f"Empty values in recommendation column: {col}")
    return errors


def main() -> int:
    errors: list[str] = []
    if REPORT.exists():
        text = REPORT.read_text(encoding="utf-8")
        errors.extend(check_executive_summary(text))
        errors.extend(check_placeholders(text))
    else:
        errors.append("Assignment2_Report.md missing")

    if AI_LOG.exists():
        text = AI_LOG.read_text(encoding="utf-8")
        errors.extend(check_critical_reflection(text))

    errors.extend(check_recommendations_csv())

    if errors:
        print("G8 CHECK FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("G8 CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
