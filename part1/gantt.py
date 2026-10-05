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
JOB_COLOURS = {"J1": "#ff5757", "J2": "#38b6ff", "J3": "#7ed957"}

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


def plot_gantt(schedule, finish, title, out_path, x_max=150):
    """Draw one row per machine (M1 on top) and one flat bar per op, coloured by job and
    labelled "op: start-finish", inside a black frame with grey gridlines every 10 time units.
    Dashed lines mark job arrivals, a black line marks the makespan, and a job colour key
    sits on the right."""
    makespan = max(finish.values())
    y_pos = {m: len(MACHINES) - 1 - i for i, m in enumerate(MACHINES)}  # M1 on top
    height = 0.6

    fig, ax = plt.subplots(figsize=(10, 3.8))
    for op, m, start in schedule:
        job, _, _, proc = OPS[op]
        ax.barh(y_pos[m], proc, left=start, height=height, color=JOB_COLOURS[job],
                linewidth=0, zorder=3)
        ax.text(start + proc / 2, y_pos[m], f"{op}: {start}-{start + proc}",
                ha="center", va="center", fontsize=10, color="white", fontweight="bold", zorder=4)

    # dashed arrival lines behind the bars but above the frame (so J1's line at t=0 shows),
    # labelled just above the frame
    for job, t in ARRIVAL.items():
        ax.axvline(t, color=JOB_COLOURS[job], linestyle="--", linewidth=2.5, zorder=2.7)
        ax.annotate(f"{job} arr.", (t, 1), xycoords=("data", "axes fraction"), xytext=(0, 4),
                    textcoords="offset points", ha="center", va="bottom",
                    fontsize=8, fontweight="bold", color=JOB_COLOURS[job])
    ax.axvline(makespan, color="black", linewidth=2.5, zorder=5)
    ax.text(makespan - 1.5, -0.55, f"makespan = {makespan}", ha="right", va="center",
            fontsize=10, fontweight="bold")

    ax.set_xlim(0, x_max)
    ax.set_ylim(-0.75, len(MACHINES) - 0.25)
    ax.set_xticks(range(0, x_max + 1, 10))
    ax.set_yticks(list(y_pos.values()), list(y_pos.keys()), fontsize=11, fontweight="bold")
    ax.tick_params(axis="y", length=0, pad=8)
    ax.set_xlabel("Time")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=18)
    ax.grid(axis="x", color="#d9d9d9", linewidth=2)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_linewidth(2)
    handles = [Patch(color=c, label=j) for j, c in JOB_COLOURS.items()]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=10)
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
