"""Part 2, Task c: a multilayer perceptron (scikit-learn) on RingSyn.

The MLP is scikit-learn's MLPClassifier with one hidden layer of 8 tanh neurons, trained
on RingSynTrain and evaluated with accuracy on RingSynTest. The inputs are standardised
with a scaler fitted on the training set only (inside a Pipeline).

It also repeats the perceptron's epoch sweep for the MLP: a fresh MLP is trained for each
epoch count in EPOCHS (by setting max_iter), to compare how both models learn over time.

Run from the repo root:
    .venv/Scripts/python part2/mlp.py            # results for seed 42, 10-seed check, epoch sweep
    .venv/Scripts/python part2/mlp.py --plot     # also save the figures to part2/figures/
"""
import argparse
import warnings
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DATA_DIR = Path(__file__).resolve().parent / "data"  # works from any working directory
FIG_DIR = Path(__file__).resolve().parent / "figures"

# The one setup used for Task c (the handout asks for a single reasonable configuration).
HIDDEN_LAYER_SIZES = (8,)  # one hidden layer with 8 neurons (handout: 4 to 10)
ACTIVATION = "tanh"        # smooth non-linearity, suits a curved boundary
SOLVER = "adam"            # scikit-learn's default optimiser
MAX_ITER = 2000            # enough for adam to converge on this small dataset (no ConvergenceWarning)

EPOCHS = [1, 5, 10, 15, 20, 50, 60, 80, 100, 120, 150, 200]  # same list as the perceptron tasks


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


def build_model(seed, max_iter=MAX_ITER):
    """Standardise the inputs, then the MLP. The scaler is fitted on the training data only.

    For adam, max_iter is the maximum number of epochs (full passes over the training set).
    """
    return make_pipeline(
        StandardScaler(),
        MLPClassifier(hidden_layer_sizes=HIDDEN_LAYER_SIZES, activation=ACTIVATION,
                      solver=SOLVER, max_iter=max_iter, random_state=seed),
    )


def train_for_epochs(seed, n_epochs, X_train, y_train):
    """Train a fresh MLP for exactly n_epochs epochs.

    With the same seed, the weight initialisation and shuffle order are identical, so this
    model is a snapshot of the main model after n_epochs epochs. Stopping before the loss has
    converged is the point of the experiment, so scikit-learn's ConvergenceWarning is hidden.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        return build_model(seed, max_iter=n_epochs).fit(X_train, y_train)


def run_epoch_sweep(X_train, y_train, X_test, y_test, seed, n_seeds):
    """Train a fresh MLP for each epoch count, for the main seed and for seeds 0 .. n_seeds-1.

    Returns (rows, multi) where rows = list of (epochs, train acc, test acc, predicted 1 share,
    model) for the main seed, and multi = test accuracy array of shape (n_seeds, len(EPOCHS)).
    """
    rows = []
    for n_epochs in EPOCHS:
        model = train_for_epochs(seed, n_epochs, X_train, y_train)
        rows.append((n_epochs,
                     accuracy_score(y_train, model.predict(X_train)),
                     accuracy_score(y_test, model.predict(X_test)),
                     model.predict(X_test).mean(),
                     model))
    multi = np.array([[accuracy_score(y_test, train_for_epochs(s, n_epochs, X_train, y_train).predict(X_test))
                       for n_epochs in EPOCHS] for s in range(n_seeds)])
    return rows, multi


def print_epoch_sweep(rows, multi, final_model, X_train, y_train, X_test, y_test, seed):
    """Print the sweep in the same format as the perceptron tables, plus the fully trained model."""
    n_seeds = multi.shape[0]
    seeds_header = f"Test acc, {n_seeds} seeds"
    print(f"MLP epoch sweep on RingSyn: a fresh MLP trained for each number of epochs (seed {seed})")
    print(f"| Model (epoch)     | Train acc | Test acc | Predicted 1 | {seeds_header:<15} |")
    print(f"|-------------------|-----------|----------|-------------|-{'-' * max(15, len(seeds_header))}-|")
    for j, (n_epochs, train_acc, test_acc, pred_1, _) in enumerate(rows):
        mean_std = f"{multi[:, j].mean():.3f} +/- {multi[:, j].std():.3f}"
        print(f"| {f'MLP ({n_epochs})':<17} | {train_acc:9.3f} | {test_acc:8.3f} | {pred_1:11.3f} "
              f"| {mean_std:<{max(15, len(seeds_header))}} |")
    final = f"MLP ({final_model[-1].n_iter_}, final)"
    print(f"| {final:<17} | {accuracy_score(y_train, final_model.predict(X_train)):9.3f} "
          f"| {accuracy_score(y_test, final_model.predict(X_test)):8.3f} "
          f"| {final_model.predict(X_test).mean():11.3f} | {'see above':<{max(15, len(seeds_header))}} |")
    print()


def print_results(model, X_train, y_train, X_test, y_test, seed):
    mlp = model[-1]
    print(f"Task c: MLP on RingSyn (train {len(X_train)}, test {len(X_test)})")
    print(f"Setup: 1 hidden layer of {HIDDEN_LAYER_SIZES[0]} neurons, activation={ACTIVATION}, "
          f"solver={SOLVER}, max_iter={MAX_ITER}, random_state={seed}, inputs standardised")
    print(f"Training stopped after {mlp.n_iter_} epochs (final training loss {mlp.loss_:.4f})")  # n_iter_ counts epochs for adam
    print()

    majority = np.bincount(y_train).argmax()  # most common class in the training set
    rows = [(f"Majority class (always {majority})",
             accuracy_score(y_train, np.full_like(y_train, majority)),
             accuracy_score(y_test, np.full_like(y_test, majority))),
            (f"MLP ({HIDDEN_LAYER_SIZES[0]} hidden, {ACTIVATION})",
             accuracy_score(y_train, model.predict(X_train)),
             accuracy_score(y_test, model.predict(X_test)))]
    print("| Model                      | Train acc | Test acc |")
    print("|----------------------------|-----------|----------|")
    for name, train_acc, test_acc in rows:
        print(f"| {name:<26} | {train_acc:9.3f} | {test_acc:8.3f} |")
    print()

    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    print("Test confusion matrix:")
    print("|         | Pred 0 | Pred 1 |")
    print("|---------|--------|--------|")
    for t in (0, 1):
        print(f"| True {t}  | {cm[t, 0]:6d} | {cm[t, 1]:6d} |")

    # Where are the remaining errors? Class 1 is the inner ring and class 0 the outer half-ring,
    # so the distance from the origin shows whether the errors are near the border between them.
    wrong = y_pred != y_test
    radius = np.linalg.norm(X_test[:, :2], axis=1)
    print(f"Misclassified test points: {wrong.sum()}, distance from origin "
          f"min {radius[wrong].min():.2f}, median {np.median(radius[wrong]):.2f}, max {radius[wrong].max():.2f}"
          f" (all test points: {radius.min():.2f} to {radius.max():.2f})")
    print()


def print_multi_seed(X_train, y_train, X_test, y_test, n_seeds):
    """Train the same setup with random_state 0 .. n_seeds-1 to show the result is not a lucky seed."""
    train_acc, test_acc = [], []
    for s in range(n_seeds):
        model = build_model(s).fit(X_train, y_train)
        train_acc.append(accuracy_score(y_train, model.predict(X_train)))
        test_acc.append(accuracy_score(y_test, model.predict(X_test)))
    print(f"Same setup over {n_seeds} seeds (0-{n_seeds - 1}):")
    print(f"  train acc mean {np.mean(train_acc):.3f} +/- {np.std(train_acc):.3f}")
    print(f"  test acc  mean {np.mean(test_acc):.3f} +/- {np.std(test_acc):.3f}"
          f" (min {np.min(test_acc):.3f}, max {np.max(test_acc):.3f})")
    print()


def _pyplot():
    """Import matplotlib only when plotting."""
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


def _plot_grid(X, pad=0.1, n=400):
    """A grid of points covering X (2 features), for drawing predicted regions."""
    lo, hi = X.min(axis=0) - pad, X.max(axis=0) + pad
    xx, yy = np.meshgrid(np.linspace(lo[0], hi[0], n), np.linspace(lo[1], hi[1], n))
    return xx, yy, np.c_[xx.ravel(), yy.ravel()]


def _draw_regions(ax, model, xx, yy, grid, X, y, names, equal=True):
    """Shade the predicted class, draw the boundary and scatter the data points."""
    from matplotlib.colors import ListedColormap

    prob = model.predict_proba(grid)[:, 1].reshape(xx.shape)
    ax.contourf(xx, yy, (prob >= 0.5).astype(int), levels=[-0.5, 0.5, 1.5],
                cmap=ListedColormap(["#c6dbef", "#fdd0a2"]))
    if prob.min() < 0.5 < prob.max():  # only draw the boundary if it is inside the picture
        ax.contour(xx, yy, prob, levels=[0.5], colors="black", linewidths=1.2)
    ax.scatter(*X[y == 0].T, s=10, color="tab:blue", label="class 0")
    ax.scatter(*X[y == 1].T, s=12, color="tab:orange", marker="x", label="class 1")
    ax.set_xlim(xx.min(), xx.max())
    ax.set_ylim(yy.min(), yy.max())
    if equal:
        ax.set_aspect("equal")
    ax.set_xlabel(names[0])
    ax.set_ylabel(names[1])


def plot_model(model, X_test, y_test, names, seed):
    """Left: the MLP's predicted regions over the test data. Right: each hidden neuron's own line."""
    plt = _pyplot()
    scaler, mlp = model[0], model[-1]
    xx, yy, grid = _plot_grid(X_test)

    fig, (ax_regions, ax_hidden) = plt.subplots(1, 2, figsize=(12, 5.5))
    for ax in (ax_regions, ax_hidden):
        _draw_regions(ax, model, xx, yy, grid, X_test, y_test, names)

    wrong = model.predict(X_test) != y_test
    ax_regions.scatter(*X_test[wrong].T, s=60, facecolors="none", edgecolors="red", label="misclassified")
    ax_regions.set_title(f"MLP decision boundary on the test data\n"
                         f"test acc {accuracy_score(y_test, model.predict(X_test)):.3f}, seed {seed}")
    ax_regions.legend(fontsize=7, loc="upper right")

    # Hidden neuron j is tanh(v_j . z + c_j), where z is the standardised input. Its line
    # v_j . z + c_j = 0 is converted back to original units: z = (x - mean) / std.
    weights, biases = mlp.coefs_[0], mlp.intercepts_[0]
    for j in range(weights.shape[1]):
        v = weights[:, j] / scaler.scale_
        c = biases[j] - np.sum(weights[:, j] * scaler.mean_ / scaler.scale_)
        ax_hidden.contour(xx, yy, (grid @ v + c).reshape(xx.shape), levels=[0], colors="dimgrey",
                          linewidths=0.8, linestyles="--")
    ax_hidden.set_title(f"Lines of the {weights.shape[1]} hidden neurons (dashed)\n"
                        "combined into the curved output boundary (solid)")

    fig.tight_layout()
    _save(fig, "task_c_mlp.png")


def plot_epoch_grid(rows, X_train, y_train, names, seed):
    """3x4 grid with the MLP's decision boundary after each epoch count (same layout as the perceptron's)."""
    plt = _pyplot()
    xx, yy, grid = _plot_grid(X_train, n=250)
    fig, axes = plt.subplots(3, 4, figsize=(14, 10.5), sharex=True, sharey=True)
    for ax, (n_epochs, _, test_acc, _, model) in zip(axes.flat, rows):
        _draw_regions(ax, model, xx, yy, grid, X_train, y_train, names, equal=False)
        ax.set_title(f"{n_epochs} epoch{'' if n_epochs == 1 else 's'}: test acc {test_acc:.3f}", fontsize=9)
        ax.label_outer()
    axes[0, 0].legend(fontsize=7, loc="upper right")
    fig.suptitle(f"Task c: RingSyn: MLP decision boundary after each number of epochs, seed {seed}\n"
                 "shading = predicted class (blue 0, orange 1), points = training data")
    fig.tight_layout()
    _save(fig, "task_c_epochs.png")


def main():
    parser = argparse.ArgumentParser(description="MLP for AIML320 Assignment 3, Part 2 Task c.")
    parser.add_argument("--seed", type=int, default=42, help="random_state for the main result (default: 42)")
    parser.add_argument("--seeds", type=int, default=10, help="number of seeds for the mean +/- std check (default: 10)")
    parser.add_argument("--plot", action="store_true", help="save the figures to part2/figures/")
    args = parser.parse_args()

    X_train, y_train, names = load_dataset("RingSynTrain")
    X_test, y_test, _ = load_dataset("RingSynTest")

    model = build_model(args.seed).fit(X_train, y_train)
    print_results(model, X_train, y_train, X_test, y_test, args.seed)
    print_multi_seed(X_train, y_train, X_test, y_test, args.seeds)
    rows, multi = run_epoch_sweep(X_train, y_train, X_test, y_test, args.seed, args.seeds)
    print_epoch_sweep(rows, multi, model, X_train, y_train, X_test, y_test, args.seed)
    if args.plot:
        plot_model(model, X_test, y_test, names, args.seed)
        plot_epoch_grid(rows, X_train, y_train, names, args.seed)


if __name__ == "__main__":
    main()
