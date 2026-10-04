AIML320 Assignment 3 - Joshua Pinpin (300662880)
================================================

Submission contents
-------------------
  report/report.pdf      The report for both parts (all questions answered here).
  readme.txt             This file.
  requirements.txt       Python libraries needed to run the programs.
  part1/gantt.py         Part 1 (optional helper, no code is required for Part 1).
  part1/figures/         Gantt charts produced by part1/gantt.py (Figures 1 and 2 in the report).
  part2/perceptron.py    Part 2 Tasks a and b: perceptron written from scratch (numpy only).
  part2/mlp.py           Part 2 Task c: multilayer perceptron (scikit-learn MLPClassifier).
  part2/figures/         Figures produced with --plot (Figures 3 to 8 in the report).
  part2/data/            The SeaSyn and RingSyn datasets used in Part 2.


Requirements
------------
  Python 3.9 or newer, plus the libraries in requirements.txt.

On the ECS School machines, run these commands from the top-level submission folder
(the folder containing this readme) to set up a virtual environment:

  python3 -m venv .venv
  source .venv/bin/activate          # bash; in tcsh use: source .venv/bin/activate.csh
  pip install -r requirements.txt

If the libraries are already installed system-wide, the venv step can be skipped.


Part 1: Job Shop Scheduling
---------------------------
The handout does not require code for Part 1, and all answers (Q1-Q5) were worked
out by hand in the report. part1/gantt.py is a small optional script that:
  1. checks the hand-calculated FCFS (Q1) and SPT (Q3) schedules against the arrival,
     precedence and machine (resource) constraints,
  2. re-creates both schedules with a non-delay dispatching simulation and checks that
     they match the hand-calculated ones,
  3. prints the completion time of each job, the makespan, the mean flowtime and the
     total completion time (used in Q2, Q4 and Q5),
  4. saves the Gantt charts to part1/figures/fcfs_gantt.png and part1/figures/spt_gantt.png.

Command (from the top-level submission folder):

  python3 part1/gantt.py

Known bugs: none.

Sample terminal output:

=== FCFS ===
Process(O11, M1, 0) -> Process(O21, M2, 10) -> Process(O31, M1, 50) -> Process(O12, M2, 50) -> Process(O22, M1, 90) -> Process(O32, M2, 90)
Job    Arrival  Completion  Flowtime
J1           0          75        75
J2          10         125       115
J3          20         110        90
Makespan:              125
Mean flowtime:         93.33
Total completion time: 310

Saved part1/figures/fcfs_gantt.png
=== SPT ===
Process(O11, M1, 0) -> Process(O21, M2, 10) -> Process(O22, M1, 50) -> Process(O12, M2, 50) -> Process(O31, M1, 85) -> Process(O32, M2, 125)
Job    Arrival  Completion  Flowtime
J1           0          75        75
J2          10          85        75
J3          20         145       125
Makespan:              145
Mean flowtime:         91.67
Total completion time: 305

Saved part1/figures/spt_gantt.png
Both hand schedules are feasible and match the dispatching simulation.


Part 2: Neural Networks
-----------------------
Both programs read the CSV files from part2/data/ relative to their own location, so they
work from any directory. All commands below are run from the top-level submission folder.
Results are reproducible: the perceptron shuffle and the MLP use fixed random seeds.

part2/perceptron.py (Tasks a and b)
  A perceptron written from scratch with numpy (step activation, online perceptron learning
  rule, zero initial weights, data shuffled each epoch). For each dataset it:
    1. trains a fresh perceptron for each number of epochs in
       [1, 5, 10, 15, 20, 50, 60, 80, 100, 120, 150, 200] (seed 42) and prints train and test
       accuracy, the share of test samples predicted as class 1, and the number of training
       mistakes in the last epoch,
    2. prints the majority-class baseline, the test confusion matrix of the 200-epoch model,
       and the minimum and maximum mistakes per epoch,
    3. repeats the sweep for seeds 0-9 and prints mean +/- std test accuracy for the plain
       perceptron and a "pocket" version (keeps the best training weights seen so far),
    4. for Task b only, repeats the sweep with an extra input feature1^2 + feature2^2.

  Commands:
    python3 part2/perceptron.py              # Tasks a and b (about 30 seconds)
    python3 part2/perceptron.py --task a     # Task a (SeaSyn) only
    python3 part2/perceptron.py --task b     # Task b (RingSyn) only
    python3 part2/perceptron.py --plot       # also save Figures 3-6 to part2/figures/
    python3 part2/perceptron.py --selftest   # sanity check: learns AND, cannot learn XOR

  Other options: --seed N (seed for the main table, default 42) and --seeds N (number of
  seeds for the mean +/- std summary, default 10).

part2/mlp.py (Task c)
  scikit-learn MLPClassifier with one hidden layer of 8 tanh neurons (adam, max_iter=2000,
  random_state=42), with the inputs standardised using the training set. It prints the setup,
  train and test accuracy next to the majority-class baseline, the test confusion matrix and
  where the misclassified points are, then the mean +/- std over seeds 0-9. Finally it repeats
  the perceptron's epoch sweep for the MLP (a fresh MLP trained for each number of epochs).
  The ConvergenceWarning that scikit-learn raises when training is stopped early on purpose
  is hidden in that sweep only.

  Commands:
    python3 part2/mlp.py                     # Task c (about 45 seconds)
    python3 part2/mlp.py --plot              # also save Figures 7 and 8 to part2/figures/

  Other options: --seed N and --seeds N, as above.

Known bugs: none.

Tested by copying the submission into a new folder and running every command above with
Python 3.14 (numpy 2.5.3, matplotlib 3.11.2, scikit-learn 1.9.1). The output matched the sample
output below and the figures it produced were identical to the submitted ones.

Sample terminal output of: python3 part2/perceptron.py --selftest

AND: accuracy 1.00, errors per epoch [1, 3, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  -> PASS
XOR: accuracy 0.50, errors per epoch [4, 4, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 4, 3, 4, 3, 3, 3, 1, 4]
  -> PASS

Sample terminal output of: python3 part2/perceptron.py

Task a: SeaSyn (train 100, test 40, seed 42)
| Model (epoch)    | Train acc | Test acc | Predicted 1 | Mistakes in last epoch |
|------------------|-----------|----------|-------------|------------------------|
| Perceptron (1)   |     0.630 |    0.675 |       0.750 |                     31 |
| Perceptron (5)   |     0.750 |    0.700 |       0.275 |                     26 |
| Perceptron (10)  |     0.740 |    0.675 |       0.350 |                     25 |
| Perceptron (15)  |     0.560 |    0.550 |       0.975 |                     24 |
| Perceptron (20)  |     0.840 |    0.850 |       0.425 |                     23 |
| Perceptron (50)  |     0.660 |    0.550 |       0.575 |                     30 |
| Perceptron (60)  |     0.730 |    0.750 |       0.675 |                     25 |
| Perceptron (80)  |     0.780 |    0.750 |       0.425 |                     19 |
| Perceptron (100) |     0.750 |    0.700 |       0.275 |                     18 |
| Perceptron (120) |     0.750 |    0.775 |       0.600 |                     25 |
| Perceptron (150) |     0.480 |    0.400 |       0.775 |                     20 |
| Perceptron (200) |     0.740 |    0.775 |       0.450 |                     29 |

Majority-class baseline (always predict 1): test acc 0.525
Test confusion matrix, Perceptron (200):
|         | Pred 0 | Pred 1 |
|---------|--------|--------|
| True 0  |     16 |      3 |
| True 1  |      6 |     15 |
Mistakes per epoch over all 200 epochs: min 16, max 34 (never 0, so it never converged)

Test accuracy over 10 seeds (0-9), mean +/- std
| Epochs | Perceptron      | Pocket perceptron |
|--------|-----------------|-------------------|
|      1 | 0.745 +/- 0.073 | 0.745 +/- 0.073   |
|      5 | 0.738 +/- 0.065 | 0.823 +/- 0.024   |
|     10 | 0.773 +/- 0.045 | 0.827 +/- 0.026   |
|     15 | 0.807 +/- 0.059 | 0.847 +/- 0.021   |
|     20 | 0.733 +/- 0.056 | 0.847 +/- 0.024   |
|     50 | 0.742 +/- 0.084 | 0.853 +/- 0.018   |
|     60 | 0.753 +/- 0.062 | 0.853 +/- 0.018   |
|     80 | 0.688 +/- 0.103 | 0.850 +/- 0.016   |
|    100 | 0.722 +/- 0.124 | 0.855 +/- 0.015   |
|    120 | 0.742 +/- 0.089 | 0.855 +/- 0.015   |
|    150 | 0.703 +/- 0.121 | 0.855 +/- 0.015   |
|    200 | 0.747 +/- 0.064 | 0.857 +/- 0.016   |

Task b: RingSyn (train 453, test 300, seed 42)
| Model (epoch)    | Train acc | Test acc | Predicted 1 | Mistakes in last epoch |
|------------------|-----------|----------|-------------|------------------------|
| Perceptron (1)   |     0.700 |    0.743 |       0.593 |                    133 |
| Perceptron (5)   |     0.673 |    0.697 |       0.440 |                    127 |
| Perceptron (10)  |     0.764 |    0.757 |       0.693 |                    141 |
| Perceptron (15)  |     0.698 |    0.727 |       0.557 |                    140 |
| Perceptron (20)  |     0.660 |    0.640 |       0.537 |                    144 |
| Perceptron (50)  |     0.689 |    0.747 |       0.510 |                    147 |
| Perceptron (60)  |     0.733 |    0.790 |       0.720 |                    134 |
| Perceptron (80)  |     0.689 |    0.730 |       0.580 |                    138 |
| Perceptron (100) |     0.669 |    0.657 |       1.000 |                    143 |
| Perceptron (120) |     0.728 |    0.773 |       0.677 |                    129 |
| Perceptron (150) |     0.722 |    0.727 |       0.570 |                    126 |
| Perceptron (200) |     0.711 |    0.747 |       0.583 |                    139 |

Majority-class baseline (always predict 1): test acc 0.657
Test confusion matrix, Perceptron (200):
|         | Pred 0 | Pred 1 |
|---------|--------|--------|
| True 0  |     76 |     27 |
| True 1  |     49 |    148 |
Mistakes per epoch over all 200 epochs: min 119, max 162 (never 0, so it never converged)

Test accuracy over 10 seeds (0-9), mean +/- std
| Epochs | Perceptron      | Pocket perceptron |
|--------|-----------------|-------------------|
|      1 | 0.723 +/- 0.041 | 0.723 +/- 0.041   |
|      5 | 0.679 +/- 0.065 | 0.758 +/- 0.045   |
|     10 | 0.686 +/- 0.058 | 0.777 +/- 0.036   |
|     15 | 0.699 +/- 0.062 | 0.775 +/- 0.038   |
|     20 | 0.688 +/- 0.043 | 0.780 +/- 0.029   |
|     50 | 0.719 +/- 0.040 | 0.781 +/- 0.010   |
|     60 | 0.689 +/- 0.065 | 0.783 +/- 0.010   |
|     80 | 0.730 +/- 0.048 | 0.783 +/- 0.010   |
|    100 | 0.727 +/- 0.068 | 0.783 +/- 0.010   |
|    120 | 0.713 +/- 0.053 | 0.782 +/- 0.009   |
|    150 | 0.698 +/- 0.062 | 0.781 +/- 0.009   |
|    200 | 0.716 +/- 0.058 | 0.784 +/- 0.009   |

Extra check: same perceptron with inputs feature1, feature2, feature1^2 + feature2^2 (seed 42)
| Epochs |     1 |     5 |    10 |    15 |    20 |    50 |    60 |    80 |   100 |   120 |   150 |   200 |
|--------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Train  | 0.872 | 0.927 | 0.898 | 0.903 | 0.907 | 0.775 | 0.874 | 0.872 | 0.865 | 0.916 | 0.898 | 0.921 |
| Test   | 0.900 | 0.947 | 0.913 | 0.930 | 0.923 | 0.790 | 0.920 | 0.900 | 0.870 | 0.943 | 0.920 | 0.953 |

Sample terminal output of: python3 part2/mlp.py

Task c: MLP on RingSyn (train 453, test 300)
Setup: 1 hidden layer of 8 neurons, activation=tanh, solver=adam, max_iter=2000, random_state=42, inputs standardised
Training stopped after 1113 epochs (final training loss 0.1996)

| Model                      | Train acc | Test acc |
|----------------------------|-----------|----------|
| Majority class (always 1)  |     0.669 |    0.657 |
| MLP (8 hidden, tanh)       |     0.927 |    0.937 |

Test confusion matrix:
|         | Pred 0 | Pred 1 |
|---------|--------|--------|
| True 0  |     93 |     10 |
| True 1  |      9 |    188 |
Misclassified test points: 19, distance from origin min 0.78, median 0.84, max 0.90 (all test points: 0.41 to 1.21)

Same setup over 10 seeds (0-9):
  train acc mean 0.926 +/- 0.003
  test acc  mean 0.936 +/- 0.003 (min 0.930, max 0.943)

MLP epoch sweep on RingSyn: a fresh MLP trained for each number of epochs (seed 42)
| Model (epoch)     | Train acc | Test acc | Predicted 1 | Test acc, 10 seeds |
|-------------------|-----------|----------|-------------|--------------------|
| MLP (1)           |     0.667 |    0.673 |       0.330 | 0.579 +/- 0.133    |
| MLP (5)           |     0.675 |    0.677 |       0.333 | 0.598 +/- 0.127    |
| MLP (10)          |     0.689 |    0.700 |       0.357 | 0.624 +/- 0.112    |
| MLP (15)          |     0.693 |    0.730 |       0.400 | 0.653 +/- 0.094    |
| MLP (20)          |     0.700 |    0.737 |       0.440 | 0.671 +/- 0.089    |
| MLP (50)          |     0.709 |    0.767 |       0.537 | 0.739 +/- 0.068    |
| MLP (60)          |     0.724 |    0.760 |       0.570 | 0.758 +/- 0.056    |
| MLP (80)          |     0.748 |    0.780 |       0.630 | 0.763 +/- 0.057    |
| MLP (100)         |     0.748 |    0.787 |       0.670 | 0.775 +/- 0.043    |
| MLP (120)         |     0.744 |    0.807 |       0.703 | 0.781 +/- 0.043    |
| MLP (150)         |     0.781 |    0.813 |       0.723 | 0.807 +/- 0.017    |
| MLP (200)         |     0.808 |    0.833 |       0.730 | 0.835 +/- 0.017    |
| MLP (1113, final) |     0.927 |    0.937 |       0.660 | see above          |

