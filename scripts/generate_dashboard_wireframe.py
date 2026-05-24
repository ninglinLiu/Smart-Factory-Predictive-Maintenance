"""Generate dashboard wireframe figure for the report (300 DPI)."""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures" / "Figure_A2_08_dashboard_wireframe.png"


def main() -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Dashboard Wireframe — Smart Factory Predictive Maintenance", fontsize=14, fontweight="bold")

    def box(x, y, w, h, text, fc="#f5f5f5", ec="#333"):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fc, ec=ec, lw=1.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, wrap=True)

    # Sidebar
    box(0.2, 0.4, 2.2, 6.2, "SIDEBAR FILTERS\n\n• Risk band\n• Engine multiselect\n• RUL threshold\n• Primary sensor\n• Life-stage band", fc="#e8eef7")

    # KPI row
    for i, kpi in enumerate(["Engines", "Mean RUL", "High Risk", "Test MAE", "Features"]):
        box(2.6 + i * 1.85, 5.6, 1.7, 0.9, kpi, fc="#d4edda")

    # Main panels
    box(2.6, 2.9, 4.3, 2.5, "PRIMARY CHART\nRisk histogram / Sensor trends\n(Plotly — zoom & pan)", fc="#fff3cd")
    box(7.0, 2.9, 4.3, 2.5, "SECONDARY CHART\nActual vs Predicted\nRUL trajectory", fc="#fff3cd")

    # Fleet table drill-down
    box(2.6, 0.5, 8.7, 2.2, "FLEET RISK TABLE (R/Y/G status badges)\nClick row → drill-down to Engine Detail page", fc="#f8d7da")

    # Nav
    box(2.6, 6.6, 8.7, 0.7, "NAV: Fleet Overview | Engine Detail | Model Insights | Recommendations", fc="#cce5ff")

    legend = [
        mpatches.Patch(color="#0072B2", label="Healthy (≥60)"),
        mpatches.Patch(color="#E69F00", label="Watch (30–59)"),
        mpatches.Patch(color="#D55E00", label="Critical (<30)"),
    ]
    ax.legend(handles=legend, loc="lower right", fontsize=8, title="Colorblind-friendly risk bands")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
