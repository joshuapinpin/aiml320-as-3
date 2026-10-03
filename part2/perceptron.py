"""Part 2, Tasks a and b: a perceptron written from scratch (numpy only).

Run from the repo root:
    .venv/Scripts/python part2/perceptron.py
"""
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent / "data"  # works from any working directory


def load_dataset(name):
    """Load <name>.csv -> (X, y, feature_names).

    The target column is 'class' and every other column is a feature. Column names are
    read from the header, not hard-coded, because RingSyn uses feature1/feature2 rather
    than the x1/x2 named in the handout.
    """
    path = DATA_DIR / f"{name}.csv"
    with open(path) as f:
        header = f.readline().strip().split(",")
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    target_idx = header.index("class")
    feature_idx = [i for i in range(len(header)) if i != target_idx]
    X = data[:, feature_idx]
    y = data[:, target_idx].astype(int)
    return X, y, [header[i] for i in feature_idx]
