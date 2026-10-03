"""Part 2, Tasks a and b: a perceptron written from scratch (numpy only).

Contents:
    load_dataset    reads a CSV from part2/data into (X, y, feature_names)
    StandardScaler  standardises features using the training set's mean and std
    Perceptron      single-layer perceptron with a step activation and the online
                    perceptron learning rule
    accuracy        fraction of samples classified correctly
    run_epoch_sweep trains a fresh perceptron for each epoch count in EPOCHS

The model itself uses only numpy. No machine learning library is used in this file
(matplotlib is only used for the optional --plot figures).

Run from the repo root:
    .venv/Scripts/python part2/perceptron.py              # all tasks
    .venv/Scripts/python part2/perceptron.py --task a     # Task a (SeaSyn) only
    .venv/Scripts/python part2/perceptron.py --task b     # Task b (RingSyn) only
    .venv/Scripts/python part2/perceptron.py --plot       # also save figures to part2/figures/
    .venv/Scripts/python part2/perceptron.py --selftest   # AND / XOR sanity checks
"""
import argparse
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent / "data"  # works from any working directory
FIG_DIR = Path(__file__).resolve().parent / "figures"

EPOCHS = [1, 5, 10, 15, 20, 50, 60, 80, 100, 120, 150, 200]  # from the handout

# task -> (title, train file, test file)
TASKS = {
    "a": ("Task a: SeaSyn", "SeaSynTrain", "SeaSynTest"),
    "b": ("Task b: RingSyn", "RingSynTrain", "RingSynTest"),  # same perceptron, no changes
}


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

    def fit(self, X, y, pocket=False):
        """Train with the online perceptron rule for n_epochs epochs.

        After training, errors_[e] holds the number of misclassified (and therefore
        updated) training samples during epoch e. It reaches 0 once the perceptron
        has found a line/plane that separates the training data.

        pocket=True ("pocket algorithm") changes nothing about learning. It only
        remembers the w, b with the highest training accuracy at the end of any epoch,
        and keeps those as the final model instead of the weights from the last epoch.
        It only looks at training data.

        history_[e] holds the (w, b) this model would end with if training stopped after
        epoch e + 1 (for pocket=True, the best weights so far). This lets the multi-seed
        summary read off every epoch count from one run instead of retraining.
        """
        rng = np.random.default_rng(self.seed)
        self.w_ = np.zeros(X.shape[1])
        self.b_ = 0.0
        self.errors_ = []
        self.history_ = []
        best_acc, best_w, best_b = -1.0, self.w_.copy(), self.b_

        for _ in range(self.n_epochs):
            order = rng.permutation(len(X))  # new random order each epoch
            errors = 0
            for i in order:
                x_i, y_i = X[i], y[i]
                y_hat = 1 if x_i @ self.w_ + self.b_ >= 0 else 0
                # Perceptron rule. update is +lr (predicted 0, should be 1), -lr
                # (predicted 1, should be 0) or 0 (correct, nothing changes).
                update = self.learning_rate * (y_i - y_hat)
                if update != 0:  # skipping a zero update is only a speed-up
                    self.w_ += update * x_i  # move the boundary towards/away from x_i
                    self.b_ += update        # bias acts as a weight on a constant input of 1
                    errors += 1
            self.errors_.append(errors)

            if pocket:
                train_acc = accuracy(y, self.predict(X))
                if train_acc > best_acc:
                    best_acc, best_w, best_b = train_acc, self.w_.copy(), self.b_
                self.history_.append((best_w, best_b))
            else:
                self.history_.append((self.w_.copy(), self.b_))

        if pocket:
            self.w_, self.b_ = best_w, best_b
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


def add_radius_feature(X, names):
    """Append r^2 = x1^2 + x2^2 (squared distance from the origin) as an extra feature."""
    return np.c_[X, (X[:, :2] ** 2).sum(axis=1)], [*names, f"{names[0]}^2 + {names[1]}^2"]


def load_scaled(train_name, test_name, radius_feature=False):
    """Load a train/test pair and standardise both with the scaler fitted on train only.

    Returns (X_train, y_train, X_test, y_test, scaler, feature_names). The scaler is
    returned so the plots can show the original, unscaled feature values.
    radius_feature=True adds r^2 as a third input (only used for the extra Task b check).
    """
    X_train, y_train, names = load_dataset(train_name)
    X_test, y_test, _ = load_dataset(test_name)
    if radius_feature:
        X_test, _ = add_radius_feature(X_test, names)
        X_train, names = add_radius_feature(X_train, names)
    scaler = StandardScaler().fit(X_train)
    return scaler.transform(X_train), y_train, scaler.transform(X_test), y_test, scaler, names


def run_epoch_sweep(X_train, y_train, X_test, y_test, seed, pocket=False):
    """Train a fresh perceptron for each epoch count in EPOCHS.

    Every model uses the same seed, so it sees the same shuffle order. The model for E
    epochs is therefore exactly the first E epochs of the 200-epoch model, and each row
    is a snapshot of one training run.
    Returns a list of (epochs, train acc, test acc, mistakes in last epoch, model).
    """
    rows = []
    for n_epochs in EPOCHS:
        model = Perceptron(n_epochs=n_epochs, seed=seed).fit(X_train, y_train, pocket=pocket)
        rows.append((n_epochs,
                     accuracy(y_train, model.predict(X_train)),
                     accuracy(y_test, model.predict(X_test)),
                     model.errors_[-1],
                     model))
    return rows


def multi_seed_test_acc(X_train, y_train, X_test, y_test, n_seeds, pocket=False):
    """Test accuracy for seeds 0 .. n_seeds-1 -> array of shape (n_seeds, len(EPOCHS)).

    Gives the same numbers as run_epoch_sweep, but trains one max(EPOCHS)-epoch model per
    seed and reads each epoch count from its history_, which is much faster.
    """
    acc = np.zeros((n_seeds, len(EPOCHS)))
    for s in range(n_seeds):
        model = Perceptron(n_epochs=max(EPOCHS), seed=s).fit(X_train, y_train, pocket=pocket)
        for j, n_epochs in enumerate(EPOCHS):
            w, b = model.history_[n_epochs - 1]
            acc[s, j] = accuracy(y_test, (X_test @ w + b >= 0).astype(int))
    return acc


def print_sweep_table(title, rows, n_train, X_test, seed):
    """Print the results table. 'Predicted 1' is the share of test samples predicted as class 1."""
    print(f"{title} (train {n_train}, test {len(X_test)}, seed {seed})")
    print("| Model (epoch)    | Train acc | Test acc | Predicted 1 | Mistakes in last epoch |")
    print("|------------------|-----------|----------|-------------|------------------------|")
    for n_epochs, train_acc, test_acc, mistakes, model in rows:
        pred_1 = model.predict(X_test).mean()
        print(f"| {f'Perceptron ({n_epochs})':<16} | {train_acc:9.3f} | {test_acc:8.3f} | {pred_1:11.3f} | {mistakes:22d} |")
    print()


def confusion_matrix(y_true, y_pred):
    """2x2 matrix: rows = true class 0/1, columns = predicted class 0/1."""
    return np.array([[np.sum((y_true == t) & (y_pred == p)) for p in (0, 1)] for t in (0, 1)])


def majority_baseline(y_train, y_test):
    """Test accuracy of always predicting the most common class in the training set."""
    majority = np.bincount(y_train).argmax()
    return majority, accuracy(y_test, majority)


def print_diagnostics(rows, y_train, X_test, y_test):
    """Majority-class baseline, confusion matrix of the last model, and whether training ever converged."""
    majority, baseline = majority_baseline(y_train, y_test)
    print(f"Majority-class baseline (always predict {majority}): test acc {baseline:.3f}")

    n_epochs, _, _, _, model = rows[-1]
    cm = confusion_matrix(y_test, model.predict(X_test))
    print(f"Test confusion matrix, Perceptron ({n_epochs}):")
    print("|         | Pred 0 | Pred 1 |")
    print("|---------|--------|--------|")
    for t in (0, 1):
        print(f"| True {t}  | {cm[t, 0]:6d} | {cm[t, 1]:6d} |")
    errors = model.errors_
    print(f"Mistakes per epoch over all {len(errors)} epochs: min {min(errors)}, max {max(errors)}"
          f" ({'converged' if min(errors) == 0 else 'never 0, so it never converged'})")
    print()


def print_multi_seed_table(plain, pocket):
    n_seeds = plain.shape[0]
    print(f"Test accuracy over {n_seeds} seeds (0-{n_seeds - 1}), mean +/- std")
    print("| Epochs | Perceptron      | Pocket perceptron |")
    print("|--------|-----------------|-------------------|")
    for j, n_epochs in enumerate(EPOCHS):
        print(f"| {n_epochs:6d} | {plain[:, j].mean():.3f} +/- {plain[:, j].std():.3f} "
              f"| {pocket[:, j].mean():.3f} +/- {pocket[:, j].std():.3f}   |")
    print()


def _pyplot():
    """Import matplotlib only when plotting, so the rest of the file needs only numpy."""
    import matplotlib
    matplotlib.use("Agg")  # write files only, no window
    import matplotlib.pyplot as plt
    return plt


def _save(fig, filename):
    FIG_DIR.mkdir(exist_ok=True)
    out_path = FIG_DIR / filename
    fig.savefig(out_path, dpi=200)
    _pyplot().close(fig)
    print(f"Saved {out_path.relative_to(Path(__file__).resolve().parent.parent).as_posix()}")


def plot_sweep(task, title, rows, plain, pocket, seed, baseline):
    """Save accuracy vs epochs and mistakes per epoch to part2/figures/."""
    plt = _pyplot()
    fig, (ax_acc, ax_err) = plt.subplots(1, 2, figsize=(11, 4))
    epochs = np.array(EPOCHS)

    ax_acc.plot(epochs, [r[2] for r in rows], "o-", color="tab:blue", label=f"Test acc (seed {seed})")
    ax_acc.plot(epochs, [r[1] for r in rows], "s--", color="tab:blue", alpha=0.5, label=f"Train acc (seed {seed})")
    for acc, colour, name in [(plain, "tab:orange", "Perceptron"), (pocket, "tab:green", "Pocket perceptron")]:
        mean, std = acc.mean(axis=0), acc.std(axis=0)
        ax_acc.plot(epochs, mean, color=colour, label=f"{name} test acc, mean ± std of {acc.shape[0]} seeds")
        ax_acc.fill_between(epochs, mean - std, mean + std, color=colour, alpha=0.2)
    ax_acc.axhline(baseline, color="grey", linestyle=":", label=f"Majority-class baseline ({baseline:.3f})")
    ax_acc.set_xscale("log")
    ax_acc.set_xticks(epochs)
    ax_acc.minorticks_off()
    ax_acc.set_xticklabels(EPOCHS, fontsize=7, rotation=45)
    ax_acc.set_ylim(0, 1)
    ax_acc.set_xlabel("Number of epochs (log scale)")
    ax_acc.set_ylabel("Accuracy")
    ax_acc.set_title("Accuracy vs number of epochs")
    ax_acc.legend(fontsize=7, loc="lower right")

    errors = rows[-1][4].errors_  # the 200-epoch model
    ax_err.plot(range(1, len(errors) + 1), errors, color="tab:red")
    ax_err.set_ylim(bottom=0)
    ax_err.set_xlabel("Epoch")
    ax_err.set_ylabel("Misclassified training samples")
    ax_err.set_title(f"Mistakes per epoch ({len(errors)}-epoch model, seed {seed})")

    fig.suptitle(title)
    fig.tight_layout()
    _save(fig, f"task_{task}_perceptron.png")


def plot_boundary_grid(task, title, rows, X_train, y_train, scaler, names, seed):
    """Save a 3x4 grid with the learned decision boundary after each epoch count.

    Each panel shows the training data and the model's predicted regions over the first
    two features, in their original units. With more than two features (SeaSyn), the
    picture is a 2D slice: the other features are fixed at their training mean.
    """
    plt = _pyplot()
    from matplotlib.colors import ListedColormap

    X_orig = scaler.mean_ + X_train * scaler.std_  # undo the scaling for the axes
    pad = 0.05 * (X_orig[:, :2].max(axis=0) - X_orig[:, :2].min(axis=0))
    lo, hi = X_orig[:, :2].min(axis=0) - pad, X_orig[:, :2].max(axis=0) + pad
    xx, yy = np.meshgrid(np.linspace(lo[0], hi[0], 300), np.linspace(lo[1], hi[1], 300))
    grid = np.tile(scaler.mean_, (xx.size, 1))  # other features at their training mean
    grid[:, 0], grid[:, 1] = xx.ravel(), yy.ravel()
    grid = scaler.transform(grid)

    fig, axes = plt.subplots(3, 4, figsize=(14, 10.5), sharex=True, sharey=True)
    for ax, (n_epochs, _, test_acc, mistakes, model) in zip(axes.flat, rows):
        net = model._net_input(grid).reshape(xx.shape)
        ax.contourf(xx, yy, (net >= 0).astype(int), levels=[-0.5, 0.5, 1.5],
                    cmap=ListedColormap(["#c6dbef", "#fdd0a2"]))
        ax.contour(xx, yy, net, levels=[0], colors="black", linewidths=1)
        ax.scatter(*X_orig[y_train == 0, :2].T, s=10, color="tab:blue", label="class 0")
        ax.scatter(*X_orig[y_train == 1, :2].T, s=12, color="tab:orange", marker="x", label="class 1")
        ax.set_xlim(lo[0], hi[0])
        ax.set_ylim(lo[1], hi[1])
        ax.set_title(f"{n_epochs} epoch{'' if n_epochs == 1 else 's'}: test acc {test_acc:.3f}, {mistakes} mistakes", fontsize=9)
    for ax in axes[-1]:
        ax.set_xlabel(names[0])
    for ax in axes[:, 0]:
        ax.set_ylabel(names[1])
    axes[0, 0].legend(fontsize=7, loc="upper right")

    note = f" ({', '.join(names[2:])} fixed at training mean)" if len(names) > 2 else ""
    fig.suptitle(f"{title}: decision boundary after each number of epochs, seed {seed}{note}\n"
                 "shading = predicted class (blue 0, orange 1), points = training data")
    fig.tight_layout()
    _save(fig, f"task_{task}_boundaries.png")


def run_task(task, seed, n_seeds, plot):
    title, train_name, test_name = TASKS[task]
    X_train, y_train, X_test, y_test, scaler, names = load_scaled(train_name, test_name)

    rows = run_epoch_sweep(X_train, y_train, X_test, y_test, seed)
    print_sweep_table(title, rows, len(X_train), X_test, seed)
    print_diagnostics(rows, y_train, X_test, y_test)

    plain = multi_seed_test_acc(X_train, y_train, X_test, y_test, n_seeds)
    pocket = multi_seed_test_acc(X_train, y_train, X_test, y_test, n_seeds, pocket=True)
    print_multi_seed_table(plain, pocket)

    if plot:
        plot_sweep(task, title, rows, plain, pocket, seed, majority_baseline(y_train, y_test)[1])
        plot_boundary_grid(task, title, rows, X_train, y_train, scaler, names, seed)
        print()

    if task == "b":
        print_radius_feature_check(train_name, test_name, seed)


def print_radius_feature_check(train_name, test_name, seed):
    """Extra check for Task b: the same perceptron, given r^2 = x1^2 + x2^2 as a third input.

    The model is unchanged. Only the input changes, which shows that the problem in Task b
    is the features, not the training.
    """
    X_train, y_train, X_test, y_test, _, names = load_scaled(train_name, test_name, radius_feature=True)
    rows = run_epoch_sweep(X_train, y_train, X_test, y_test, seed)
    print(f"Extra check: same perceptron with inputs {', '.join(names)} (seed {seed})")
    print("| Epochs | " + " | ".join(f"{e:5d}" for e in EPOCHS) + " |")
    print("|--------|" + "|".join("-------" for _ in EPOCHS) + "|")
    print("| Train  | " + " | ".join(f"{r[1]:.3f}" for r in rows) + " |")
    print("| Test   | " + " | ".join(f"{r[2]:.3f}" for r in rows) + " |")
    print()


def main():
    parser = argparse.ArgumentParser(description="Perceptron for AIML320 Assignment 3, Part 2 Tasks a and b.")
    parser.add_argument("--task", choices=[*TASKS, "all"], default="all", help="which task to run (default: all)")
    parser.add_argument("--seed", type=int, default=42, help="shuffle seed for the main results table (default: 42)")
    parser.add_argument("--seeds", type=int, default=10, help="number of seeds for the mean +/- std summary (default: 10)")
    parser.add_argument("--plot", action="store_true", help="save figures to part2/figures/")
    parser.add_argument("--selftest", action="store_true", help="run the AND / XOR sanity checks and exit")
    args = parser.parse_args()

    if args.selftest:
        raise SystemExit(0 if selftest() else 1)
    for task in (TASKS if args.task == "all" else [args.task]):
        run_task(task, args.seed, args.seeds, args.plot)


if __name__ == "__main__":
    main()
