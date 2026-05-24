"""Generate Assignment 2 Jupyter notebooks from src modules."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "notebooks"


def make_notebook(name: str, title: str, cells: list[dict]) -> None:
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "cells": cells,
    }
    path = NB_DIR / name
    path.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print(f"Wrote {path}")


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": source.splitlines(True),
    }


def main() -> None:
    NB_DIR.mkdir(exist_ok=True)

    make_notebook(
        "01_feature_engineering.ipynb",
        "Feature Engineering",
        [
            md("# Assignment 2 — Feature Engineering\n\nSmart Factory Predictive Maintenance (NASA FD001)"),
            code(
                """import sys
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.features import engineer_features, get_deployable_feature_columns, select_features
from src.leakage_guard import assert_no_leakage

df = pd.read_csv(ROOT / 'data/processed/SmartFactory_cleaned.csv')
assert df.shape == (20631, 42), df.shape
print('A1 cleaned data OK:', df.shape)

fe, catalog = engineer_features(df)
catalog.to_csv(ROOT / 'outputs/feature_catalog.csv', index=False)
fe.to_csv(ROOT / 'data/processed/SmartFactory_modeling.csv', index=False)
print(f'Engineered {len(catalog)} documented features')
print(catalog.head(10))

cols = get_deployable_feature_columns(fe)
selected = select_features(fe, cols, corr_threshold=0.95)
assert_no_leakage(selected)
pd.DataFrame({'feature': selected}).to_csv(ROOT / 'outputs/selected_features.csv', index=False)
print(f'Selected {len(selected)} deployable features after correlation pruning')
print('NOTEBOOK_OK')
"""
            ),
        ],
    )

    make_notebook(
        "02_model_training.ipynb",
        "Model Training",
        [
            md("# Assignment 2 — Model Training\n\nRidge baseline + tuned Random Forest / Gradient Boosting with engine-grouped CV."),
            code(
                """# Run full training pipeline (shared with scripts/run_assignment2_pipeline.py)
import subprocess, sys
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
result = subprocess.run([sys.executable, str(ROOT / 'scripts/run_assignment2_pipeline.py')], check=True)
print('NOTEBOOK_OK')
"""
            ),
        ],
    )

    make_notebook(
        "03_model_evaluation.ipynb",
        "Model Evaluation",
        [
            md("# Assignment 2 — Model Evaluation\n\nLoads pipeline outputs and verifies G7 rubric minima."),
            code(
                """from pathlib import Path
import pandas as pd
import joblib

ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()

catalog = pd.read_csv(ROOT / 'outputs/feature_catalog.csv')
cv = pd.read_csv(ROOT / 'outputs/cv_results.csv')
test = pd.read_csv(ROOT / 'outputs/test_metrics.csv')
fi = pd.read_csv(ROOT / 'outputs/feature_importance.csv')
model = joblib.load(ROOT / 'models/final_model.pkl')

assert len(catalog) >= 10, f'G7 fail: only {len(catalog)} features'
assert cv['fold'].nunique() >= 5, 'G7 fail: need 5-fold CV'
assert len(test) >= 3, 'G7 fail: test metrics missing'
assert 'perm_importance_mean' in fi.columns, 'G7 fail: permutation importance missing'
assert model is not None, 'G7 fail: final model missing'

print('G7 assertions PASSED')
print(test.to_string(index=False))
print('NOTEBOOK_OK')
"""
            ),
        ],
    )


if __name__ == "__main__":
    main()
