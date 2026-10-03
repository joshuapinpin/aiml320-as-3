"""Part 2, Tasks a and b: a perceptron written from scratch (numpy only).

Contents:
    load_dataset    reads a CSV from part2/data into (X, y, feature_names)
    StandardScaler  standardises features using the training set's mean and std
    Perceptron      single-layer perceptron with a step activation and the online
                    perceptron learning rule
    accuracy        fraction of samples classified correctly

The model itself uses only numpy. No machine learning library is used in this file.

Run from the repo root:
    .venv/Scripts/python part2/perceptron.py --selftest   # AND / XOR sanity checks
"""
import argparse
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


class StandardScaler:
    """Rescale each feature to mean 0 and standard deviation 1.

    fit() must be called on the training set only. The same mean and std are then
    applied to the test set, so no information from the test set leaks into training.
    """

    def fit(self, X):
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0)
        self.std_[self.std_ == 0] = 1.0  # a constant feature would otherwise divide by zero
        return self

    def transform(self, X):
        return (X - self.mean_) / self.std_

    def fit_transform(self, X):
        return self.fit(X).transform(X)


class Perceptron:
    """Rosenblatt perceptron for 0/1 labels.

    Prediction:  y_hat = 1 if w . x + b >= 0, else 0   (step activation)
    Learning:    for each training sample, in a shuffled order every epoch,
                     w <- w + lr * (y - y_hat) * x
                     b <- b + lr * (y - y_hat)
                 (y - y_hat) is 0 when the prediction is correct, so the weights only
                 change on mistakes.

    w and b start at zero. With zero initialisation every update is a multiple of lr, so
    lr only rescales w and b and never changes which side of the boundary a point is on.
    Any positive learning rate therefore gives the same predictions.
    """

    def __init__(self, learning_rate=1.0, n_epochs=10, seed=42):
        self.learning_rate = learning_rate
        self.n_epochs = n_epochs  # one epoch = one full pass over the training set
        self.seed = seed          # seeds the per-epoch shuffle, so runs are reproducible

    def _net_input(self, X):
        """Return w . x + b for each row of X."""
        return X @ self.w_ + self.b_

    def predict(self, X):
        """Apply the step function to the net input -> array of 0/1."""
        return (self._net_input(X) >= 0).astype(int)

    def fit(self, X, y):
        """Train with the online perceptron rule for n_epochs epochs.

        After training, errors_[e] holds the number of misclassified (and therefore
        updated) training samples during epoch e. It reaches 0 once the perceptron
        has found a line/plane that separates the training data.
        """
        rng = np.random.default_rng(self.seed)
        self.w_ = np.zeros(X.shape[1])
        self.b_ = 0.0
        self.errors_ = []

        for _ in range(self.n_epochs):
            order = rng.permutation(len(X))  # new random order each epoch
            errors = 0
            for i in order:
                x_i, y_i = X[i], y[i]
                y_hat = 1 if x_i @ self.w_ + self.b_ >= 0 else 0
                # Perceptron rule. update is +lr (predicted 0, should be 1), -lr
                # (predicted 1, should be 0) or 0 (correct, nothing changes).
                update = self.learning_rate * (y_i - y_hat)
                self.w_ += update * x_i  # move the boundary towards/away from x_i
                self.b_ += update        # bias acts as a weight on a constant input of 1
                errors += int(update != 0)
            self.errors_.append(errors)
        return self


def accuracy(y_true, y_pred):
    """Fraction of predictions that match the true labels."""
    return np.mean(y_true == y_pred)


def selftest():
    """Sanity checks: the perceptron must learn AND (linearly separable) and fail on XOR."""
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    cases = {"AND": np.array([0, 0, 0, 1]), "XOR": np.array([0, 1, 1, 0])}
    passed = True
    for name, y in cases.items():
        model = Perceptron(n_epochs=20).fit(X, y)
        acc = accuracy(y, model.predict(X))
        print(f"{name}: accuracy {acc:.2f}, errors per epoch {model.errors_}")
        if name == "AND":
            ok = acc == 1.0 and model.errors_[-1] == 0
        else:  # XOR is not linearly separable, so some sample is always misclassified
            ok = acc < 1.0 and 0 not in model.errors_
        print(f"  -> {'PASS' if ok else 'FAIL'}")
        passed &= ok
    return passed


def main():
    parser = argparse.ArgumentParser(description="Perceptron for AIML320 Assignment 3, Part 2 Tasks a and b.")
    parser.add_argument("--selftest", action="store_true", help="run the AND / XOR sanity checks and exit")
    args = parser.parse_args()

    if args.selftest:
        raise SystemExit(0 if selftest() else 1)
    parser.print_help()  # the Task a / b experiments are added in later stages


if __name__ == "__main__":
    main()
