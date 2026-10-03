"""Part 1 helper: validate the hand-calculated FCFS and SPT schedules and draw Gantt charts.

The handout does not require code for Part 1. This script only double-checks the
answers in the report and produces the figures for it.

Run from the repo root:
    .venv/Scripts/python part1/gantt.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write files only, no window
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ---- Problem data ----
ARRIVAL = {"J1": 0, "J2": 10, "J3": 20}
# op -> (job, index_in_job, machine, proc_time)
OPS = {
    "O11": ("J1", 1, "M1", 50), "O12": ("J1", 2, "M2", 25),
    "O21": ("J2", 1, "M2", 30), "O22": ("J2", 2, "M1", 35),
    "O31": ("J3", 1, "M1", 40), "O32": ("J3", 2, "M2", 20),
}
MACHINES = ["M1", "M2"]
JOB_COLOURS = {"J1": "tab:blue", "J2": "tab:orange", "J3": "tab:green"}

# ---- Schedules from the hand calculations (Q1 and Q3): list of (op, machine, start) ----
FCFS = [
    ("O11", "M1", 0), ("O21", "M2", 10), ("O31", "M1", 50),
    ("O12", "M2", 50), ("O22", "M1", 90), ("O32", "M2", 90),
]
SPT = [
    ("O11", "M1", 0), ("O21", "M2", 10), ("O22", "M1", 50),
    ("O12", "M2", 50), ("O31", "M1", 85), ("O32", "M2", 125),
]


def first_op(job):
    return f"O{job[1]}1"


def validate(schedule) -> dict:
    """Check every constraint and return the finish time of each op.

    Raises ValueError listing all violations if the schedule is infeasible.
    """
    errors = []
    start = {op: t for op, _, t in schedule}
    finish = {op: t + OPS[op][3] for op, _, t in schedule}

    # 1. each op appears exactly once, on its correct machine
    ops_in_schedule = [op for op, _, _ in schedule]
    if sorted(ops_in_schedule) != sorted(OPS):
        errors.append(f"schedule must contain each op exactly once, got {ops_in_schedule}")
    for op, machine, _ in schedule:
        if OPS[op][2] != machine:
            errors.append(f"{op} must run on {OPS[op][2]}, not {machine}")

    for op, (job, idx, _, _) in OPS.items():
        if op not in start:
            continue
        # 2. arrival: start(Oj1) >= arrival time of Jj
        if idx == 1 and start[op] < ARRIVAL[job]:
            errors.append(f"{op} starts at {start[op]} before {job} arrives at {ARRIVAL[job]}")
        # 3. precedence: start(Oj2) >= finish(Oj1)
        if idx == 2:
            prev = first_op(job)
            if prev in finish and start[op] < finish[prev]:
                errors.append(f"{op} starts at {start[op]} before {prev} finishes at {finish[prev]}")

    # 4. resource: no two ops overlap on the same machine
    for m in MACHINES:
        on_m = sorted((t, op) for op, machine, t in schedule if machine == m)
        for (_, a), (t_b, b) in zip(on_m, on_m[1:]):
            if t_b < finish[a]:
                errors.append(f"{b} starts at {t_b} on {m} while {a} runs until {finish[a]}")

    # 5. sorted: start times are non-decreasing in list order
    starts = [t for _, _, t in schedule]
    if starts != sorted(starts):
        errors.append(f"actions are not sorted by start time: {starts}")

    if errors:
        raise ValueError("Infeasible schedule:\n  " + "\n  ".join(errors))
    return finish


def summarise(name, schedule, finish):
    """Print the schedule, job completion times, makespan, mean flowtime and total completion time."""
    completion = {job: finish[f"O{job[1]}2"] for job in ARRIVAL}
    flowtime = {job: completion[job] - ARRIVAL[job] for job in ARRIVAL}
    makespan = max(completion.values())

    print(f"=== {name} ===")
    print(" -> ".join(f"Process({op}, {m}, {t})" for op, m, t in schedule))
    print(f"{'Job':<5}{'Arrival':>9}{'Completion':>12}{'Flowtime':>10}")
    for job in ARRIVAL:
        print(f"{job:<5}{ARRIVAL[job]:>9}{completion[job]:>12}{flowtime[job]:>10}")
    print(f"Makespan:              {makespan}")
    print(f"Mean flowtime:         {sum(flowtime.values()) / len(flowtime):.2f}")
    print(f"Total completion time: {sum(completion.values())}")
    print()
    return makespan


def idle_gaps(schedule, finish, machine, until):
    """Return (start, length) of each period where `machine` is idle between 0 and `until`."""
    gaps, t = [], 0
    for start, op in sorted((s, op) for op, m, s in schedule if m == machine):
        if start > t:
            gaps.append((t, start - t))
        t = max(t, finish[op])
    if until > t:
        gaps.append((t, until - t))
    return gaps


def plot_gantt(schedule, finish, title, out_path, x_max=150):
    """Draw one row per machine (M1 on top), one bar per op coloured by job, and save to `out_path`."""
    makespan = max(finish.values())
    y_pos = {m: len(MACHINES) - 1 - i for i, m in enumerate(MACHINES)}  # M1 on top
    height = 0.6

    fig, ax = plt.subplots(figsize=(9, 3))
    for m in MACHINES:
        y = y_pos[m] - height / 2
        # light grey hatched bars for idle time, up to the makespan
        ax.broken_barh(idle_gaps(schedule, finish, m, makespan), (y, height),
                       facecolor="none", edgecolor="lightgrey", hatch="///", linewidth=0)
    for op, m, start in schedule:
        job, _, _, proc = OPS[op]
        ax.broken_barh([(start, proc)], (y_pos[m] - height / 2, height),
                       facecolor=JOB_COLOURS[job], edgecolor="black")
        ax.text(start + proc / 2, y_pos[m], f"{op}\n{start}-{start + proc}",
                ha="center", va="center", fontsize=8, color="white", fontweight="bold")

    # dashed arrival lines behind the bars, labelled in the gap between the machine rows
    for job, t in ARRIVAL.items():
        ax.axvline(t, color=JOB_COLOURS[job], linestyle="--", linewidth=1, zorder=0)
        ax.text(t + 0.8, 0.5, f"{job} arr.", va="center", ha="left",
                fontsize=7, color=JOB_COLOURS[job])
    ax.axvline(makespan, color="red", linewidth=1.5)
    ax.text(makespan - 1, -0.45, f"makespan = {makespan}", color="red", fontsize=8, va="bottom", ha="right")

    ax.set_xlim(0, x_max)
    ax.set_ylim(-0.5, len(MACHINES) - 0.5)
    ax.set_yticks(list(y_pos.values()), list(y_pos.keys()))
    ax.set_xticks(range(0, x_max + 1, 10))
    ax.set_xlabel("Time")
    ax.set_title(f"{title} (makespan = {makespan})")
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    ax.set_axisbelow(True)
    handles = [Patch(facecolor=c, edgecolor="black", label=j) for j, c in JOB_COLOURS.items()]
    handles.append(Patch(facecolor="none", edgecolor="lightgrey", hatch="///", label="idle"))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def dispatch(rule):
    """Non-delay dispatching simulation.

    Whenever a machine is idle and has ready ops in its queue, start the op with the
    smallest rule(op, ready_time) (ties broken by op name). Returns a schedule list.
    """
    ready = {op: ARRIVAL[job] for op, (job, idx, _, _) in OPS.items() if idx == 1}
    free = {m: 0 for m in MACHINES}
    schedule, t = [], 0
    while ready:
        for m in MACHINES:
            if free[m] > t:
                continue
            queue = [op for op, r in ready.items() if OPS[op][2] == m and r <= t]
            if not queue:
                continue
            op = min(queue, key=lambda o: (rule(o, ready[o]), o))
            job, idx, _, proc = OPS[op]
            schedule.append((op, m, t))
            free[m] = t + proc
            del ready[op]
            if idx == 1:
                ready[f"O{job[1]}2"] = t + proc
        # jump to the next event: a machine becoming free or an op becoming ready
        t = min([f for f in free.values() if f > t] + [r for r in ready.values() if r > t], default=t)
    return schedule


if __name__ == "__main__":
    rules = {
        "FCFS": lambda op, ready_time: ready_time,  # longest-waiting op first
        "SPT": lambda op, ready_time: OPS[op][3],   # shortest processing time first
    }
    out = Path(__file__).parent / "figures"
    out.mkdir(exist_ok=True)
    for name, sched in [("FCFS", FCFS), ("SPT", SPT)]:
        finish = validate(sched)
        assert dispatch(rules[name]) == sched, f"{name} dispatch simulation disagrees with hand schedule"
        summarise(name, sched, finish)
        path = out / f"{name.lower()}_gantt.png"
        plot_gantt(sched, finish, f"{name} schedule", path)
        print(f"Saved {path.relative_to(Path.cwd()) if path.is_relative_to(Path.cwd()) else path}")
    print("Both hand schedules are feasible and match the dispatching simulation.")
