"""Master submission verifier — gates G1 through G9."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_RAW = [
    ROOT / "data/raw/train_FD001.txt",
    ROOT / "data/raw/test_FD001.txt",
    ROOT / "data/raw/RUL_FD001.txt",
]

FORBIDDEN_INPUTS = {"RUL", "capped_RUL", "near_failure", "cycle_ratio", "life_stage", "max_cycle"}


def gate(name: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    msg = f"[{status}] {name}" + (f" — {detail}" if detail else "")
    print(msg)
    return ok


def main() -> int:
    all_ok = True

    # G1 raw data
    for p in REQUIRED_RAW:
        ok = p.exists() and p.stat().st_size > 0
        all_ok = all_ok and gate("G1", ok, str(p))

    # G3 no placeholders in report
    report = ROOT / "reports/Assignment2_Report.md"
    if report.exists():
        text = report.read_text(encoding="utf-8")
        placeholders = re.findall(r"\[UPDATE[^\]]*\]|\{\{[^}]+\}\}", text)
        all_ok = all_ok and gate("G3", len(placeholders) == 0, f"{len(placeholders)} placeholders")
    else:
        all_ok = all_ok and gate("G3", False, "report missing")

    # G5 leakage — selected features
    sel = ROOT / "outputs/selected_features.csv"
    if sel.exists():
        feats = set(pd.read_csv(sel)["feature"])
        leaked = FORBIDDEN_INPUTS & feats
        all_ok = all_ok and gate("G5", len(leaked) == 0, str(leaked) if leaked else "clean")
    else:
        all_ok = all_ok and gate("G5", False, "selected_features.csv missing")

    # G7 rubric minima
    checks = []
    cat = ROOT / "outputs/feature_catalog.csv"
    if cat.exists():
        n = len(pd.read_csv(cat))
        checks.append(n >= 10)
        gate("G7-features", n >= 10, f"{n} features")
    else:
        checks.append(False)
        gate("G7-features", False, "missing catalog")

    cv = ROOT / "outputs/cv_results.csv"
    if cv.exists():
        df = pd.read_csv(cv)
        checks.append(df["fold"].nunique() >= 5)
        checks.append(df["model"].nunique() >= 2)
        gate("G7-cv", all(checks[-2:]), f"folds={df['fold'].nunique()}, models={df['model'].nunique()}")
    else:
        checks.append(False)
        gate("G7-cv", False, "missing cv_results")

    test = ROOT / "outputs/test_metrics.csv"
    if test.exists():
        checks.append(len(pd.read_csv(test)) >= 1)
        gate("G7-test", True)
    else:
        checks.append(False)
        gate("G7-test", False)

    fi = ROOT / "outputs/feature_importance.csv"
    if fi.exists():
        fdf = pd.read_csv(fi)
        checks.append("perm_importance_mean" in fdf.columns)
        gate("G7-fi", "perm_importance_mean" in fdf.columns)
    else:
        checks.append(False)
        gate("G7-fi", False)

    all_ok = all_ok and all(checks)

    # G6 model exists
    model = ROOT / "models/final_model.pkl"
    all_ok = all_ok and gate("G6", model.exists(), "final_model.pkl")

    # G8 report constraints
    rc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_report_constraints.py")],
        capture_output=True,
        text=True,
    )
    all_ok = all_ok and gate("G8", rc.returncode == 0, rc.stdout.strip() or rc.stderr.strip())

    # G9 AI log
    ai_log = ROOT / "reports/AI_Collaboration_Log_A2.md"
    if ai_log.exists():
        ai_text = ai_log.read_text(encoding="utf-8")
        conv_count = len(re.findall(r"### Conversation \d+", ai_text))
        reject_count = len(re.findall(r"Rejected|rejected", ai_text))
        ok9 = conv_count >= 5 and reject_count >= 3
        all_ok = all_ok and gate("G9", ok9, f"conversations={conv_count}, rejections={reject_count}")
    else:
        all_ok = all_ok and gate("G9", False, "AI log missing")

    # Dashboard
    all_ok = all_ok and gate("Dashboard", (ROOT / "dashboard/app.py").exists())

    # Notebooks
    for nb in ["01_feature_engineering.ipynb", "02_model_training.ipynb", "03_model_evaluation.ipynb"]:
        all_ok = all_ok and gate(f"Notebook-{nb}", (ROOT / "notebooks" / nb).exists())

    # Wireframe figure
    wireframe = ROOT / "figures" / "Figure_A2_08_dashboard_wireframe.png"
    all_ok = all_ok and gate("Wireframe", wireframe.exists(), str(wireframe))

    # Usability test log (template must exist; user fills after peer test)
    usability = ROOT / "outputs" / "usability_test_log.md"
    all_ok = all_ok and gate("Usability-log", usability.exists())

    # Dashboard screenshots folder
    ss_readme = ROOT / "dashboard" / "screenshots" / "README.md"
    ss_files = list((ROOT / "dashboard" / "screenshots").glob("S*.png")) if (ROOT / "dashboard" / "screenshots").exists() else []
    # 4 pages → 4 screenshots minimum (one per dashboard page)
    gate("Dashboard-screenshots", len(ss_files) >= 4, f"{len(ss_files)}/4+ PNG files in dashboard/screenshots/")
    if len(ss_files) < 4:
        all_ok = False

    print("\n" + ("ALL GATES PASSED" if all_ok else "GATE FAILURES — see above (screenshots require manual capture)"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
