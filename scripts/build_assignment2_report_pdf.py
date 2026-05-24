"""
Render Assignment 2 Markdown report to A4 PDF.

Usage (from repo root):
    python scripts/build_assignment2_report_pdf.py

Uses Playwright if Chromium is installed; otherwise falls back to xhtml2pdf.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "reports" / "Assignment2_Report.md"
HTML_TMP = ROOT / "reports" / "_Assignment2_Report_render.html"
PDF_OUT = ROOT / "reports" / "Assignment2_Report.pdf"

CSS = """
@page { size: A4; margin: 14mm 13mm 16mm 13mm; }
html { font-size: 10.5pt; }
body {
  font-family: Georgia, "Times New Roman", Times, serif;
  line-height: 1.38;
  color: #1a1a1a;
  max-width: 176mm;
  margin: 0 auto;
}
h1 { font-size: 1.55rem; page-break-after: avoid; margin-top: 0; }
h2 {
  font-size: 1.18rem;
  margin-top: 1.4rem;
  border-bottom: 1px solid #bbb;
  padding-bottom: 0.15rem;
  page-break-after: avoid;
}
h3 { font-size: 1.0rem; page-break-after: avoid; margin-top: 0.9rem; }
p { margin: 0.35rem 0; text-align: justify; }
ul, ol { margin: 0.25rem 0 0.25rem 1.1rem; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.6rem 0;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th, td { border: 1px solid #888; padding: 4px 7px; vertical-align: top; }
th { background: #f2f2f2; font-weight: 600; }
code { font-family: Consolas, monospace; font-size: 0.9em; background: #f5f5f5; padding: 0 3px; }
img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 5mm auto;
  page-break-inside: avoid;
}
"""


def _resolve_image_paths(html: str) -> str:
    """Convert relative figure paths to absolute file URIs for PDF renderers."""

    def repl(match: re.Match) -> str:
        src = match.group(1)
        if src.startswith(("http://", "https://", "file://")):
            return match.group(0)
        abs_path = (MD_PATH.parent / src).resolve()
        if abs_path.exists():
            return f'src="{abs_path.as_uri()}"'
        return match.group(0)

    return re.sub(r'src="([^"]+)"', repl, html)


def _build_html(text: str) -> str:
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    body = _resolve_image_paths(body)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Assignment 2 — Smart Factory Predictive Maintenance</title>
  <style>{CSS}</style>
</head>
<body>{body}</body>
</html>"""


def _pdf_via_chromium_cli(html_path: Path) -> bool:
    """Use installed Chrome/Edge headless print-to-pdf (no Playwright browser download)."""
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    browser = next((p for p in candidates if p.exists()), None)
    if browser is None:
        return False
    uri = html_path.resolve().as_uri()
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        f"--print-to-pdf={PDF_OUT.resolve()}",
        uri,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        return PDF_OUT.exists() and PDF_OUT.stat().st_size > 1000
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"Browser CLI PDF failed ({exc}); trying next method...")
        return False


def _pdf_via_playwright(html_path: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(html_path.as_uri(), wait_until="domcontentloaded")
            page.pdf(path=str(PDF_OUT), format="A4", print_background=True)
            browser.close()
        return True
    except Exception as exc:
        print(f"Playwright unavailable ({exc}); trying xhtml2pdf fallback...")
        return False


def _pdf_via_xhtml2pdf(html: str) -> None:
    from xhtml2pdf import pisa

    with PDF_OUT.open("wb") as out:
        status = pisa.CreatePDF(html, dest=out, encoding="utf-8")
    if status.err:
        raise RuntimeError(f"xhtml2pdf failed with {status.err} error(s)")


def main() -> None:
    if not MD_PATH.exists():
        raise FileNotFoundError(f"Report not found: {MD_PATH}")

    text = MD_PATH.read_text(encoding="utf-8")
    if re.search(r"\[UPDATE[^\]]*\]|\{\{[^}]+\}\}", text):
        raise RuntimeError("G3 FAIL: unresolved placeholders remain in Assignment2_Report.md")

    rc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_report_constraints.py")],
        capture_output=True,
        text=True,
    )
    if rc.returncode != 0:
        raise RuntimeError(f"G8 FAIL:\n{rc.stdout}\n{rc.stderr}")

    html = _build_html(text)
    HTML_TMP.write_text(html, encoding="utf-8")

    if not _pdf_via_playwright(HTML_TMP):
        if not _pdf_via_chromium_cli(HTML_TMP):
            _pdf_via_xhtml2pdf(html)
            print("Note: PDF generated via xhtml2pdf. For better quality run: python -m playwright install chromium")

    try:
        HTML_TMP.unlink()
    except OSError:
        pass
    print(f"Wrote PDF: {PDF_OUT}")


if __name__ == "__main__":
    main()
