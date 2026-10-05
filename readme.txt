AIML320 Assignment 3 - Joshua Pinpin (300662880)
================================================

Submission contents
-------------------
  report.pdf          The report for both parts (all questions answered here).
  readme.txt          This file.
  requirements.txt    Python libraries needed to run the notebooks.
  perceptron.ipynb    Part 2 Tasks a and b: perceptron written from scratch (numpy only).
  mlp.ipynb           Part 2 Task c: multilayer perceptron (scikit-learn MLPClassifier).

The notebooks are submitted already run, so every table and figure is saved inside them
and can be read without running anything (open them in Jupyter, VS Code, or on GitHub).


Part 1: Job Shop Scheduling
---------------------------
The handout does not require code for Part 1, so no program is submitted for it. All
answers (Q1-Q5) are worked out in the report.


Part 2: Neural Networks
-----------------------

Requirements
  Python 3.9 or newer, plus the libraries in requirements.txt.

Setup
  The datasets are not included in this submission. The notebooks expect the four CSV files
  provided with the assignment handout in a folder called data/, and save their figures to a
  folder called figures/. Both folders must sit next to the notebooks. From the folder that
  contains the notebooks, run:

    mkdir data figures
    cp /path/to/SeaSynTrain.csv /path/to/SeaSynTest.csv data/
    cp /path/to/RingSynTrain.csv /path/to/RingSynTest.csv data/

  The folder should then look like this:

    perceptron.ipynb
    mlp.ipynb
    requirements.txt
    data/SeaSynTrain.csv
    data/SeaSynTest.csv
    data/RingSynTrain.csv
    data/RingSynTest.csv
    figures/                (empty; the notebooks write their PNGs here)

  On the ECS School machines, set up a virtual environment in the same folder:

    python3 -m venv .venv
    source .venv/bin/activate          # bash; in tcsh use: source .venv/bin/activate.csh
    pip install -r requirements.txt

  If the libraries are already installed system-wide, the venv step can be skipped.

Commands
  From the folder that contains the notebooks, with the venv activated. Each command runs
  every cell of the notebook and saves the outputs back into it:

    jupyter nbconvert --to notebook --execute --inplace perceptron.ipynb   # about 1 minute
    jupyter nbconvert --to notebook --execute --inplace mlp.ipynb          # about 45 seconds

  To run the notebooks interactively instead, open them in VS Code (with the Python and Jupyter
  extensions) or install Jupyter with "pip install notebook", run "jupyter notebook", and use
  Run > Run All Cells.

  Results are reproducible: the perceptron shuffle and the MLP use fixed random seeds (42).

perceptron.ipynb (Tasks a and b)
  A perceptron written from scratch with numpy: a Perceptron class with fit, activation (step
  function) and predict, plus small helpers to load a CSV and standardise the features with the
  training set's mean and std. For SeaSyn (Task a) and then RingSyn (Task b) it:
    1. trains a fresh perceptron for each number of epochs in
       [1, 5, 10, 15, 20, 50, 60, 80, 100, 120, 150, 200] and prints the test accuracy table,
    2. draws the decision boundary of each of those 12 models in a 3x4 grid and saves it to
       figures/perceptron_SeaSyn.png and figures/perceptron_RingSyn.png
       (Figures 3 and 4 in the report).
  A final cell runs the data checks quoted in the report: whether the SeaSyn training set is
  linearly separable (a linear-programming feasibility check with scipy), whether the SeaSyn
  test rows are copies of training rows, and the majority-class baseline for each test set.

mlp.ipynb (Task c)
  scikit-learn MLPClassifier with one hidden layer of 8 tanh neurons (adam, random_state=42),
  with the inputs standardised using the training set. It uses the same helpers as the
  perceptron notebook (copied in, so each notebook runs on its own). It:
    1. trains a fresh MLP for each number of epochs in the same list (max_iter = epochs),
       prints the test accuracy table and saves the 3x4 boundary grid to
       figures/mlp_RingSyn.png (Figure 5). Stopping early is the point of this sweep, so
       scikit-learn's ConvergenceWarning is hidden,
    2. trains the final MLP until its loss stops improving (max_iter=2000), prints its train and
       test accuracy, and saves its decision boundary to figures/mlp_RingSyn_final.png
       (Figure 6).

Known bugs: none. If data/ or figures/ is missing, the notebooks stop with a
FileNotFoundError, so follow the Setup steps above first.

Tested by running both commands above with Python 3.14 (numpy 2.5.3, matplotlib 3.11.2,
scikit-learn 1.9.1, nbconvert 7.17.1, ipykernel 7.4.0). The saved outputs matched the sample
output below.

Sample output of perceptron.ipynb (the figures are omitted here):

## Task a: SeaSyn (linearly separable)
| Model (epoch)    | Accuracy |
|------------------|----------|
| Perceptron (1)   |    0.675 |
| Perceptron (5)   |    0.700 |
| Perceptron (10)  |    0.675 |
| Perceptron (15)  |    0.550 |
| Perceptron (20)  |    0.850 |
| Perceptron (50)  |    0.550 |
| Perceptron (60)  |    0.750 |
| Perceptron (80)  |    0.750 |
| Perceptron (100) |    0.700 |
| Perceptron (120) |    0.775 |
| Perceptron (150) |    0.400 |
| Perceptron (200) |    0.775 |

## Task b: RingSyn (not linearly separable)
| Model (epoch)    | Accuracy |
|------------------|----------|
| Perceptron (1)   |    0.743 |
| Perceptron (5)   |    0.697 |
| Perceptron (10)  |    0.757 |
| Perceptron (15)  |    0.727 |
| Perceptron (20)  |    0.640 |
| Perceptron (50)  |    0.747 |
| Perceptron (60)  |    0.790 |
| Perceptron (80)  |    0.730 |
| Perceptron (100) |    0.657 |
| Perceptron (120) |    0.773 |
| Perceptron (150) |    0.727 |
| Perceptron (200) |    0.747 |

## Data checks used in the report
SeaSyn train linearly separable: False
SeaSyn test set is the first 40 train rows: True
SeaSyn majority-class baseline (always predict 1): 0.525
RingSyn majority-class baseline (always predict 1): 0.657

Sample output of mlp.ipynb (the figures are omitted here):

## Epoch sweep: RingSyn
| Model (epoch) | Accuracy |
|---------------|----------|
| MLP (1)       |    0.673 |
| MLP (5)       |    0.677 |
| MLP (10)      |    0.700 |
| MLP (15)      |    0.730 |
| MLP (20)      |    0.737 |
| MLP (50)      |    0.767 |
| MLP (60)      |    0.760 |
| MLP (80)      |    0.780 |
| MLP (100)     |    0.787 |
| MLP (120)     |    0.807 |
| MLP (150)     |    0.813 |
| MLP (200)     |    0.833 |

## Final model: trained until the loss converges (max 2000 epochs)
Trained for 1113 epochs
Train accuracy: 0.927
Test accuracy:  0.937
