AIML320 Assignment 3 - Joshua Pinpin (300662880)
================================================

Submission contents
-------------------
  report/report.pdf      The report for both parts (all questions answered here).
  readme.txt             This file.
  requirements.txt       Python libraries needed to run the programs.
  part1/gantt.py         Part 1 (optional helper, no code is required for Part 1).
  part1/figures/         Gantt charts produced by part1/gantt.py (Figures 1 and 2 in the report).
  part2/data/            The SeaSyn and RingSyn datasets used in Part 2.


Requirements
------------
  Python 3.9 or newer, plus the libraries in requirements.txt.

On the ECS School machines, run these commands from the top-level submission folder
(the folder containing this readme) to set up a virtual environment:

  python3 -m venv .venv
  source .venv/bin/activate
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
(To be added: perceptron and mlp programs, commands and sample output.)
