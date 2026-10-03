# AIML320 Assignment 3 — <Your Name> (<Student ID>)

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

![FCFS Gantt chart](../part1/figures/fcfs_gantt.png)

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

### Q4. SPT completion times, makespan and comparison

### Q5. Does a better solution imply a better rule?

## Part 2: Neural Networks

### Task a: Perceptron on linearly separable data (SeaSyn)

### Task b: Perceptron on non-linearly separable data (RingSyn)

### Task c: MLP on non-linearly separable data (RingSyn)

## References / External resources
