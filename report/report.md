# AIML320 Assignment 3 — Joshua Pinpin (ID: 300662880)

## Part 1: Job Shop Scheduling

The instance has 3 jobs and 2 machines:

| Job | Arrival | Op 1 (machine, time) | Op 2 (machine, time) |
|---|---|---|---|
| J1 | 0 | O11 (M1, 50) | O12 (M2, 25) |
| J2 | 10 | O21 (M2, 30) | O22 (M1, 35) |
| J3 | 20 | O31 (M1, 40) | O32 (M2, 20) |

Every schedule must satisfy three constraints: an operation Oj1 cannot start before job Jj arrives (arrival), Oj2 cannot start before Oj1 has finished (precedence), and each machine processes at most one operation at a time (resource).

### Q1. Earliest starting times (FCFS sequence)

The given sequence is:

Process(O11, M1, t1) → Process(O21, M2, t2) → Process(O31, M1, t3) → Process(O12, M2, t4) → Process(O22, M1, t5) → Process(O32, M2, t6)

This fixes the order of operations on each machine: M1 processes O11, then O31, then O22, and M2 processes O21, then O12, then O32. Following the hint, the earliest start time of each action is

- **ready time** of the operation = the job's arrival time (for Oj1), or the finish time of Oj1 (for Oj2),
- **idle time** of the machine = the finish time of the previous operation on that machine (0 if none),
- **start** = max(ready time, idle time), and **finish** = start + processing time.

Working through the actions in order, and updating each machine's idle time after each step (both machines start idle at time 0):

| # | Action | Proc time | Op ready time | Machine idle time | Start = max | Finish |
|---|---|---|---|---|---|---|
| 1 | O11 on M1 | 50 | 0 (J1 arrives) | M1: 0 | **t1 = 0** | 50 |
| 2 | O21 on M2 | 30 | 10 (J2 arrives) | M2: 0 | **t2 = 10** | 40 |
| 3 | O31 on M1 | 40 | 20 (J3 arrives) | M1: 50 (after O11) | **t3 = 50** | 90 |
| 4 | O12 on M2 | 25 | 50 (O11 finishes) | M2: 40 (after O21) | **t4 = 50** | 75 |
| 5 | O22 on M1 | 35 | 40 (O21 finishes) | M1: 90 (after O31) | **t5 = 90** | 125 |
| 6 | O32 on M2 | 20 | 90 (O31 finishes) | M2: 75 (after O12) | **t6 = 90** | 110 |

Which constraint determines each start time:

1. **t1 = 0.** J1 arrives at 0 and M1 is idle, so O11 starts immediately.
2. **t2 = 10.** M2 is idle from time 0, but J2 only arrives at 10, so the arrival constraint is binding.
3. **t3 = 50.** O31 is ready at 20 (J3's arrival), but M1 is busy with O11 until 50, so the resource constraint is binding.
4. **t4 = 50.** M2 is free at 40 (after O21), but O12 cannot start until O11 finishes at 50, so the precedence constraint is binding.
5. **t5 = 90.** O22 is ready at 40 (O21 has finished), but M1 is busy with O31 until 90, so the resource constraint is binding.
6. **t6 = 90.** M2 is free at 75 (after O12), but O32 cannot start until O31 finishes at 90, so the precedence constraint is binding.

As a check, the start times satisfy t1 ≤ t2 ≤ … ≤ t6 (0 ≤ 10 ≤ 50 ≤ 50 ≤ 90 ≤ 90), as required by the sorted sequence. The resulting schedule is:

Process(O11, M1, 0) → Process(O21, M2, 10) → Process(O31, M1, 50) → Process(O12, M2, 50) → Process(O22, M1, 90) → Process(O32, M2, 90)

Figure 1 shows this schedule as a Gantt chart. The waits identified above are visible as gaps: M2 is idle at 0–10 until J2 arrives, O31 waits for M1 until 50, and M2 is idle at 40–50 and 75–90 while O12 and O32 wait for their first operations to finish.

![FCFS Gantt chart](../part1/figures/fcfs_gantt.png)

*Figure 1: Gantt chart of the FCFS schedule from Q1 (makespan 125). Bars are coloured by job, hatched areas are machine idle time, and dashed lines mark job arrivals.*

### Q2. Completion times and makespan (FCFS)

The completion time of a job is the finish time of its last (second) operation, taken from the table in Q1:

| Job | Last operation | Start | Proc time | Completion time |
|---|---|---|---|---|
| J1 | O12 | 50 | 25 | **75** |
| J2 | O22 | 90 | 35 | **125** |
| J3 | O32 | 90 | 20 | **110** |

The makespan is the largest completion time over all jobs:

**Makespan = max(75, 125, 110) = 125**

J2 determines the makespan. Although J2 arrives second and its first operation O21 is finished by 40, its second operation O22 has to wait until 90 for M1, because the sequence puts O31 ahead of O22 on M1.

### Q3. SPT schedule

A dispatching rule does not plan the whole schedule in advance. Instead, it simulates time moving forward and makes one decision at a time:

- Each machine has a **queue** of operations that are ready for it. An operation is ready when its job has arrived (for Oj1) or when Oj1 has finished (for Oj2).
- Whenever a machine is **idle** and its queue is **non-empty**, the rule chooses which queued operation to start next. The **Shortest Processing Time (SPT)** rule chooses the operation with the smallest processing time.
- A machine with an empty queue stays idle, even if an operation will become ready soon (non-delay dispatching).

The decision points are the times when a job arrives or an operation finishes, since these are the only times a queue or a machine's status can change. The trace below lists each decision point, with the processing times of queued operations in brackets.

| Time t | Event(s) | M1 queue | M2 queue | Decision |
|---|---|---|---|---|
| 0 | J1 arrives → O11 ready | {O11(50)} | {} | M1 idle: starts O11, finishes at 50 |
| 10 | J2 arrives → O21 ready | M1 busy | {O21(30)} | M2 idle: starts O21, finishes at 40 |
| 20 | J3 arrives → O31 ready | {O31(40)} (M1 busy) | {} | M1 busy until 50: O31 waits |
| 40 | O21 finishes → O22 ready | {O31(40), O22(35)} (M1 busy) | {} | M2 idle but its queue is empty |
| 50 | O11 finishes → O12 ready | {O31(40), O22(35)} | {O12(25)} | **M1: SPT picks O22 (35 < 40)**, finishes at 85. M2: starts O12, finishes at 75 |
| 75 | O12 finishes (J1 complete) | M1 busy | {} | M2 idle, queue empty |
| 85 | O22 finishes (J2 complete) | {O31(40)} | {} | M1 starts O31, finishes at 125 |
| 125 | O31 finishes → O32 ready | {} | {O32(20)} | M2 starts O32, finishes at 145 |
| 145 | O32 finishes (J3 complete) | {} | {} | All jobs done |

The only real choice happens at **t = 50**. M1 becomes free, and two operations are waiting for it: O31 (ready since 20, 40 time units) and O22 (ready since 40, 35 time units). SPT picks O22 because it is shorter. FCFS would pick O31 because it has been waiting longer. Applying the same procedure with FCFS reproduces the Q1 schedule exactly, so this single decision is the only difference between the two solutions.

The final SPT solution, sorted by start time, is:

Process(O11, M1, 0) → Process(O21, M2, 10) → Process(O22, M1, 50) → Process(O12, M2, 50) → Process(O31, M1, 85) → Process(O32, M2, 125)

O22 and O12 both start at 50, so either order is valid. They are listed with M1 first, consistent with the tie at t = 50 in the Q1 sequence.

To double-check the hand calculations, I wrote a small optional script (`part1/gantt.py`). It checks both schedules against the arrival, precedence and resource constraints, and simulates non-delay dispatching with each rule. The simulation produces exactly the Q1 schedule when using FCFS and exactly the schedule above when using SPT. Figure 2 shows the SPT schedule.

![SPT Gantt chart](../part1/figures/spt_gantt.png)

*Figure 2: Gantt chart of the SPT schedule from Q3 (makespan 145), drawn on the same time axis as Figure 1. M2 is idle from 75 to 125 while it waits for O31 to finish on M1.*

### Q4. SPT completion times, makespan and comparison

As in Q2, each job's completion time is the finish time of its second operation:

| Job | Last operation | Start | Proc time | Completion time |
|---|---|---|---|---|
| J1 | O12 | 50 | 25 | **75** |
| J2 | O22 | 50 | 35 | **85** |
| J3 | O32 | 125 | 20 | **145** |

**Makespan = max(75, 85, 145) = 145**

Comparison with the FCFS solution from Q1 and Q2:

| | J1 | J2 | J3 | Makespan |
|---|---|---|---|---|
| FCFS (Q1) | 75 | 125 | 110 | **125** |
| SPT (Q3) | 75 | 85 | 145 | 145 |

**In terms of makespan, the FCFS solution is better: 125 compared with 145, a difference of 20 time units.**

SPT helps J2, which finishes 40 units earlier (85 instead of 125), but it delays J3 by 35 units (145 instead of 110). This happens because SPT runs O22 before O31 on M1, so O31 does not finish until 125. O32 cannot start on M2 until then, and M2 sits idle from 75 to 125. J3 now determines the makespan, and it is 20 units worse than under FCFS.

### Q5. Does a better solution imply a better rule?

**No.** FCFS producing the better solution on this instance does not mean FCFS is a better rule than SPT in general, for three reasons.

**1. "Better" depends on the objective.** Makespan is only one way to measure a schedule. The table below compares both solutions on two other common objectives: mean flowtime (the average time a job spends in the shop, completion time minus arrival time) and total completion time. The values were computed from the completion times in Q2 and Q4.

| Rule | Completion (J1, J2, J3) | Flowtime (J1, J2, J3) | Mean flowtime | Total completion time | Makespan |
|---|---|---|---|---|---|
| FCFS | 75, 125, 110 | 75, 115, 90 | 93.33 | 310 | **125** |
| SPT | 75, 85, 145 | 75, 75, 125 | **91.67** | **305** | 145 |

SPT is worse on makespan but better on both flowtime-based objectives, so even on this one instance neither rule dominates the other.

**2. One small instance is not enough evidence.** This instance has only 3 jobs and 2 machines, and the two solutions differ in a single decision (at t = 50). Dispatching rules are heuristics, and how well they perform varies a lot between instances. Small changes can flip or remove the difference. For example, if J3 arrived after t = 50, O31 would not be in M1's queue at that decision point, and both rules would produce the same schedule. To conclude that one rule is better, both rules should be tested on many instances (e.g. randomly generated instances or a standard benchmark set), and their average performance should be compared, ideally with a statistical significance test.

**3. Each rule suits different goals.** SPT is greedy and myopic. At t = 50 it chose O22 (35) over O31 (40) because O22 is shorter, without considering that J3 still had 60 units of work left (O31 + O32) while J2 had only 35. Delaying J3 left M2 idle from 75 to 125 and increased the makespan. A rule that considers remaining work, such as Most Work Remaining (MWKR), would have chosen O31 here and is generally better suited to makespan. SPT, by finishing short operations first, tends to reduce flowtime-type objectives, which is what happened here. So which rule is "better" depends on what the scheduler is trying to optimise.

### Q6. (AIML420 only)

Q6 is required for AIML420 students only. This report is for AIML320, so Q6 was not attempted.

## Part 2: Neural Networks

### Data

Part 2 uses two binary classification datasets. Each has a separate train and test file, and the target column is `class` (0 or 1).

| Dataset | Train rows | Test rows | Features | Class 1 share (train / test) |
|---|---|---|---|---|
| SeaSyn | 100 | 40 | `attrib1`, `attrib2`, `attrib3` (values between 0 and 10) | 52.0% / 52.5% |
| RingSyn | 453 | 300 | `feature1`, `feature2` (values between about −1.2 and 1.1) | 66.9% / 65.7% |

Both datasets are close enough to balanced for accuracy to be a sensible metric, although RingSyn leans towards class 1. A model that always predicts class 1 already gets **65.7%** on the RingSyn test set, so this majority-class baseline is used as the yardstick in Tasks b and c. A useful model has to beat it clearly.

In RingSyn, class 1 is an inner disc (mean distance from the origin 0.71) and class 0 is a ring around it (mean distance 0.99), so the classes cannot be separated by a straight line. The handout calls the RingSyn features `x1` and `x2`, but the files name them `feature1` and `feature2`, so the code reads the column names from each file's header instead of hard-coding them.

One thing to note about SeaSyn: the 40 test rows are identical to the first 40 rows of the training file. The SeaSyn "test" accuracy in Task a is therefore measured on data the perceptron was trained on, and it shows how well the model fits the training data rather than how well it generalises. The RingSyn train and test files share no rows.

### Perceptron implementation

The perceptron used in Tasks a and b is written from scratch in `part2/perceptron.py`, using only numpy for array maths. The same class is used, unchanged, for both tasks.

| Part | Choice | Reason |
|---|---|---|
| Activation | Step function: ŷ = 1 if w·x + b ≥ 0, otherwise ŷ = 0 | This is the classic Rosenblatt perceptron, and its 0/1 output matches the dataset labels. |
| Bias | A separate bias term b, updated like a weight on a constant input of 1 | Without it, the decision boundary would have to pass through the origin. |
| Initialisation | w = 0 and b = 0 | Deterministic, so results only depend on the shuffle seed. |
| Learning rule | Online (one sample at a time): w ← w + η(y − ŷ)x and b ← b + η(y − ŷ) | The standard perceptron rule. y − ŷ is 0 when the prediction is correct, so the weights only change on mistakes. A false negative (y = 1, ŷ = 0) moves the boundary towards x, and a false positive moves it away. |
| Learning rate | η = 1.0 | Because the weights start at zero, every update is a multiple of η, so η only scales w and b and never changes which side of the boundary a point falls on. Any positive η gives exactly the same predictions, and I confirmed this by training with η = 0.01, 1 and 7. |
| Epoch | One full pass over the training set, in a new random order each epoch | Shuffling stops the result depending on the order of rows in the file. The shuffle uses a fixed seed (42), so every run is reproducible. |
| Feature scaling | Each feature is standardised to mean 0 and standard deviation 1, using the mean and std of the **training** set only, and the same values are applied to the test set | SeaSyn features range from 0 to 10, while the bias input is always 1. Without scaling, the bias would learn much more slowly than the weights. Fitting the scaler only on the training set prevents test data leaking into training. |

During training the model records how many training samples it misclassified (and therefore updated on) in each epoch. If this count reaches 0, the boundary separates the training data perfectly and no further epoch changes the weights. If it never reaches 0, the boundary keeps moving every epoch.

To check the implementation before using it on the assignment data, `python3 part2/perceptron.py --selftest` trains the perceptron for 20 epochs on two 4-point logic gates:

- **AND** (linearly separable): the error count goes 1, 3, 2, 2, 2, 2, 3 and then stays at 0 from epoch 8, ending with 100% accuracy.
- **XOR** (not linearly separable): there is at least one error in every epoch and accuracy ends at 50%, because no single line can separate XOR's classes.

### Task a: Perceptron on linearly separable data (SeaSyn)

For each number of epochs in the handout's list, a fresh perceptron was trained on SeaSynTrain and evaluated on SeaSynTest (`python3 part2/perceptron.py --task a`). Every model uses the same shuffle seed (42), so the model trained for E epochs is exactly the first E epochs of the 200-epoch model, and the table shows snapshots of a single training run. The last column is the number of training samples the perceptron got wrong (and updated on) during its final epoch.

| Model (epoch) | Train accuracy | Test accuracy | Mistakes in last epoch |
|---|---|---|---|
| Perceptron (1) | 0.630 | 0.675 | 31 |
| Perceptron (5) | 0.750 | 0.700 | 26 |
| Perceptron (10) | 0.740 | 0.675 | 25 |
| Perceptron (15) | 0.560 | 0.550 | 24 |
| Perceptron (20) | 0.840 | **0.850** | 23 |
| Perceptron (50) | 0.660 | 0.550 | 30 |
| Perceptron (60) | 0.730 | 0.750 | 25 |
| Perceptron (80) | 0.780 | 0.750 | 19 |
| Perceptron (100) | 0.750 | 0.700 | 18 |
| Perceptron (120) | 0.750 | 0.775 | 25 |
| Perceptron (150) | 0.480 | **0.400** | 20 |
| Perceptron (200) | 0.740 | 0.775 | 29 |

One seed could be misleading, so the sweep was repeated with seeds 0–9. The table below gives the mean ± standard deviation of test accuracy. It also shows a "pocket" version of the same perceptron. Its learning is identical, but at the end of each epoch it measures training accuracy and keeps the best weights seen so far, instead of the weights left by the last epoch. The pocket version only uses the training data to choose its weights.

| Epochs | Perceptron test accuracy | Pocket perceptron test accuracy |
|---|---|---|
| 1 | 0.745 ± 0.073 | 0.745 ± 0.073 |
| 5 | 0.738 ± 0.065 | 0.823 ± 0.024 |
| 10 | 0.773 ± 0.045 | 0.827 ± 0.026 |
| 15 | 0.807 ± 0.059 | 0.847 ± 0.021 |
| 20 | 0.733 ± 0.056 | 0.847 ± 0.024 |
| 50 | 0.742 ± 0.084 | 0.853 ± 0.018 |
| 60 | 0.753 ± 0.062 | 0.853 ± 0.018 |
| 80 | 0.688 ± 0.103 | 0.850 ± 0.016 |
| 100 | 0.722 ± 0.124 | 0.855 ± 0.015 |
| 120 | 0.742 ± 0.089 | 0.855 ± 0.015 |
| 150 | 0.703 ± 0.121 | 0.855 ± 0.015 |
| 200 | 0.747 ± 0.064 | 0.857 ± 0.016 |

![Task a accuracy and mistakes per epoch](../part2/figures/task_a_perceptron.png)

*Figure 3: Left: accuracy against the number of epochs (log scale) on SeaSyn, for seed 42 and as the mean ± std over seeds 0–9 for the plain and pocket perceptrons. Right: training samples misclassified in each epoch of the 200-epoch model (seed 42). The count never reaches 0.*

![Task a decision boundaries](../part2/figures/task_a_boundaries.png)

*Figure 4: The decision boundary of each model in the first table (seed 42), drawn over the SeaSyn training data. SeaSyn has three features, so each panel is a 2D slice through attrib1 and attrib2 with attrib3 fixed at its training mean. The shading is the predicted class within that slice. A point's real prediction also depends on its own attrib3 value, so a few points can be classified differently from the shading behind them.*

**How does increasing the number of epochs affect the model's accuracy?**

For this perceptron on SeaSyn, training for more epochs does **not** make it more accurate. With seed 42, test accuracy jumps between rows with no upward trend. It is 0.850 after 20 epochs but 0.550 after 50 and 0.400 after 150. Averaged over 10 seeds, it stays roughly flat at 0.69–0.81 for every epoch count, and the standard deviation (up to 0.12) is as large as the differences between rows. Accuracy after 200 epochs (0.747) is no better than after 1 epoch (0.745).

The reason is that SeaSyn is **not perfectly linearly separable**, even though the task treats it as linearly separable data. The classes are roughly split by the line attrib1 + attrib2 = 8 (that rule alone gets 88% of the training set right), but about 12% of the points are on the "wrong" side of any line. I checked this separately: a linear-programming feasibility test (scipy) found no line that separates the training set, and a linear SVM (scikit-learn) reached only 85% training accuracy. This is most likely label noise added by the SEA data generator. The Perceptron Convergence Theorem only guarantees that the perceptron stops changing when a separating line exists, so it does not apply here. In contrast, the AND self-test, which is separable, converged after 7 epochs.

Instead, some training samples are misclassified in every epoch (between 15 and 36 per epoch across all seeds, never 0, as Figure 3 shows), so every epoch updates the weights and the decision boundary keeps moving. Each update fixes one point but can move the line past many others. The model returned after E epochs is just wherever the last few updates left the line, not the best line found so far. Stopping at a different epoch is like taking a random snapshot, which is why accuracy depends much more on where training stops than on how long it ran. Figure 4 shows this directly. After 20 and 100 epochs the line runs diagonally between the two classes, roughly along the attrib1 + attrib2 = 8 split. After 10 and 50 epochs it is much too flat and cuts through the class 1 points, and after 150 epochs it lies outside the slice altogether. The 150-epoch model had put most of its weight on attrib3, the feature that has no relationship with the class, and it predicts class 1 for 86% of the training set, which explains its 0.400 test accuracy.

The pocket results confirm this. Keeping the best weights seen during training makes test accuracy rise with the number of epochs, from 0.745 to about 0.85 by 15–20 epochs, and then level off with a small standard deviation. Its training accuracy reaches 0.86–0.87, close to the best any line can do. So the perceptron does find good lines during training, but the plain learning rule cannot settle on one. Other common fixes are a learning rate that decreases over time (unlike a constant learning rate, a schedule does change the result even with zero initial weights) or averaging the weights over all updates.

Two caveats apply to these numbers. The test set has only 40 samples, so each mistake changes test accuracy by 2.5 percentage points. Also, as noted in the Data section, the 40 test rows are copies of the first 40 training rows, so test accuracy closely follows training accuracy and says little about how well the model generalises to new data.

### Task b: Perceptron on non-linearly separable data (RingSyn)

### Task c: MLP on non-linearly separable data (RingSyn)

## References / External resources

**Part 1**

- The Q1–Q5 answers were worked out by hand from the problem definition in the assignment handout. No external code was used.
- The optional checking script `part1/gantt.py` is my own code. It uses Python 3 and the Matplotlib library (J. D. Hunter, "Matplotlib: A 2D Graphics Environment", *Computing in Science & Engineering*, 9(3), 90–95, 2007) to draw Figures 1 and 2.
