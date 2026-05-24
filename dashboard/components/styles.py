"""Colorblind-friendly risk styling (Okabe-Ito inspired + text labels)."""

RISK_GREEN = "#0072B2"   # blue — healthy
RISK_YELLOW = "#E69F00"  # orange — watch
RISK_RED = "#D55E00"     # vermillion — critical

RISK_LABELS = {
    "green": ("Healthy", RISK_GREEN, "RUL ≥ 60 cycles"),
    "yellow": ("Watch", RISK_YELLOW, "30 ≤ RUL < 60 cycles"),
    "red": ("Critical", RISK_RED, "RUL < 30 cycles"),
}


def rul_band(rul: float, threshold: int = 30) -> str:
    if rul < threshold:
        return "red"
    if rul < 60:
        return "yellow"
    return "green"


def band_label(band: str) -> str:
    return RISK_LABELS[band][0]


def band_color(band: str) -> str:
    return RISK_LABELS[band][1]
