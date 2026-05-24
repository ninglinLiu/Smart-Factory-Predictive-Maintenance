"""
Render Markdown report (+ embedded PNG figures) to A4 PDF.

Usage (from repo root):
    python scripts/build_assignment_report_pdf.py
"""
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "reports" / "Assignment1_SmartFactory_Report.md"
HTML_TMP = ROOT / "reports" / "_Assignment1_Report_render.html"
PDF_OUT = ROOT / "reports" / "Assignment1_SmartFactory_Report.pdf"

CSS = """
@page { size: A4; margin: 14mm 13mm 16mm 13mm; }
html { font-size: 10.5pt; }
body {
  font-family: "Georgia", "Times New Roman", Times, serif;
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
blockquote { margin: 0.3rem 0 0.3rem 1rem; color: #333; border-left: 3px solid #ccc; padding-left: 0.5rem; }
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
code { font-family: ui-monospace, Consolas, monospace; font-size: 0.9em; background: #f5f5f5; padding: 0 3px; }
pre { background: #f5f5f5; padding: 8px; overflow-x: auto; page-break-inside: avoid; }
img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 5mm auto;
  page-break-inside: avoid;
}
"""


def main() -> None:
    md = MD_PATH.read_text(encoding="utf-8")
    body = markdown.markdown(md, extensions=["tables", "fenced_code"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Assignment 1 — Smart Factory EDA</title>
  <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>"""

    HTML_TMP.write_text(html, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(HTML_TMP.as_uri(), wait_until="domcontentloaded")
        page.emulate_media(media="screen")
        page.pdf(
            path=str(PDF_OUT),
            format="A4",
            print_background=True,
            margin={
                "top": "14mm",
                "right": "11mm",
                "bottom": "14mm",
                "left": "11mm",
            },
        )
        browser.close()

    try:
        HTML_TMP.unlink()
    except OSError:
        pass

    print(f"Wrote PDF: {PDF_OUT}")


if __name__ == "__main__":
    main()
