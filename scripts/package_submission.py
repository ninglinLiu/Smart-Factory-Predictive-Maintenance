"""
Package Assignment 2 submission ZIP (run only when ready to submit).

Usage:
    python scripts/package_submission.py --student-id 2012345
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_MB = 100


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-id", required=True, help="Your student ID")
    args = parser.parse_args()
    sid = args.student_id

    rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_submission.py")])
    if rc.returncode != 0:
        print("ABORT: verify_submission.py failed — ZIP not created (G10).")
        return 1

    out_dir = ROOT / "submission_staging"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

    report_pdf = ROOT / "reports" / "Assignment2_Report.pdf"
    a1_pdf = ROOT / "reports" / "Assignment1_SmartFactory_Report.pdf"
    if not report_pdf.exists():
        print(f"Missing {report_pdf} — run build_assignment2_report_pdf.py first")
        return 1

    shutil.copy(report_pdf, out_dir / f"Assignment2_Report_{sid}.pdf")
    if a1_pdf.exists():
        shutil.copy(a1_pdf, out_dir / f"Assignment1_Reference_{sid}.pdf")

    # Code zip
    code_zip = out_dir / f"Assignment2_Code_{sid}.zip"
    exclude = {".git", "__pycache__", ".ipynb_checkpoints", "submission_staging", ".cursor"}
    with zipfile.ZipFile(code_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in ROOT.rglob("*"):
            if any(p in path.parts for p in exclude):
                continue
            if path.is_file() and path.suffix not in {".pyc"}:
                zf.write(path, path.relative_to(ROOT))

    # Presentation placeholder if video missing
    pres = out_dir / f"Assignment2_Presentation_{sid}.MISSING.txt"
    pres.write_text(
        "Presentation video not included. See deliverables/video/VIDEO_SCRIPT.md to self-record.\n",
        encoding="utf-8",
    )

    final_zip = ROOT / f"Assignment2_{sid}_SmartFactory.zip"
    with zipfile.ZipFile(final_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in out_dir.iterdir():
            zf.write(f, f.name)

    size_mb = final_zip.stat().st_size / (1024 * 1024)
    if size_mb > MAX_MB:
        print(f"FAIL: ZIP size {size_mb:.1f} MB exceeds {MAX_MB} MB limit")
        return 1

    print(f"Created {final_zip} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
