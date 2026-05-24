"""Enforce G5: no retrospective / target-leaking columns as model inputs."""

from __future__ import annotations

FORBIDDEN_INPUT_COLUMNS = frozenset(
    {
        "RUL",
        "capped_RUL",
        "near_failure",
        "cycle_ratio",
        "life_stage",
        "max_cycle",
    }
)


def assert_no_leakage(feature_columns: list[str] | set[str], *, context: str = "") -> None:
    """Raise ValueError if any forbidden column appears in model inputs."""
    cols = set(feature_columns)
    leaked = FORBIDDEN_INPUT_COLUMNS & cols
    if leaked:
        prefix = f"{context}: " if context else ""
        raise ValueError(
            f"{prefix}Data leakage detected — forbidden input columns: {sorted(leaked)}"
        )


def filter_deployable_columns(columns: list[str]) -> list[str]:
    """Return columns safe for prediction-time deployment."""
    return [c for c in columns if c not in FORBIDDEN_INPUT_COLUMNS]
