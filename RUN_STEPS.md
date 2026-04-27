# How to Run Each Member's Demo

Mini Docker — Container Orchestration System (ML2011, VIT Pune 2025-26)

Quick, copy-paste steps each team member runs during viva. Every command is run from the repo root (`/home/yash/mini-docker`).

---

## 🌐 Web Dashboard (Recommended for Viva)

The project includes a beautiful web dashboard that streams live terminal output and shows real-time visualizations for all 5 roles — disk scheduling race animations, Banker's algorithm matrix, namespace rings, OverlayFS layers, and CPU Gantt charts.

```bash
# One-time install (requires Python 3.8+)
pip install -r web/requirements.txt

# Start the web server
uvicorn web.server:app --host 0.0.0.0 --port 8080

# Open in browser on Ubuntu:
#   http://localhost:8080
# From Windows (same WiFi):
#   http://<ubuntu-ip>:8080
```

> **Role 4** (Banker's Algorithm) runs without sudo and is the safest demo to start with if you are setting up the machine.

> The web server needs to be running as a **privileged user** (or with sudo) since it internally calls `sudo ./bin/roleX_demo` for roles 1/2/3/5:
> ```bash
> sudo uvicorn web.server:app --host 0.0.0.0 --port 8080
> ```

---

## Terminal-only demo (fallback)

## Before anyone presents — one-time setup

Run these **once** on the demo machine:

```bash
# 1. Clean previous binaries and repopulate src/ + include/
make clean
make setup

# 2. Cache sudo credentials so the presentation flows without re-typing
sudo -v
```

`make setup` creates the `include/` and `bin/` directories and copies `container.h` into `include/`. The `src/*.c` files are already in place as the canonical source — no copying needed.

Build status verified: all five roles compile cleanly on Ubuntu with cgroups v2 (a few harmless `-Wunused` warnings in role2/role4 are expected).


---

## Role 1 — Architecture Lead

**Subsystem:** Container lifecycle, Linux namespaces, `clone()` system call.

```bash
sudo make role1
sudo ./bin/role1_demo
```

**What the demo prints (summary):**
- `[container_create] id=c1 state=CREATING` — enters CREATING state
- `[container:c1] PID inside namespace = 1` — child sees itself as PID 1 inside the new PID namespace (proof of isolation)
- `[container_create] id=c1 pid=<host_pid> state=RUNNING`
- A "Container created" summary block (ID, host PID, state, CPU/RAM config)
- `[container_stop] ... exited gracefully` → `[container_destroy] state=TERMINATED`

**Talking points during viva:**
- The namespace flags used: `CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWUTS | CLONE_NEWIPC`.
- State machine: `PENDING → CREATING → RUNNING → STOPPING → STOPPED → TERMINATED` (defined in `container.h:8-15`).
- Zombie reaping is done in a `SIGCHLD` handler (`role1_architecture.c` near line 326).

**Live proof (optional):** while the container sleeps, open another terminal and run `sudo nsenter -t <pid> -p ps aux` — only the container's own processes show up.

---

## Role 2 — Memory & Storage

**Subsystem:** cgroups v2 memory limits, OverlayFS (copy-on-write rootfs), virtual `/proc` + `/tmp` + `/dev` mounts.

```bash
sudo make role2
sudo ./bin/role2_demo
```

**What the demo prints (summary):**
- `--- Memory cgroup ---`
  - `[memory_cgroup] Creating cgroup: /sys/fs/cgroup/containers/demo-c1`
  - `[memory_cgroup] memory.max = 128 MB (134217728 bytes)`
  - `[memory_cgroup] Verified memory.max = 134217728 bytes` (round-trip readback)
- `--- Overlay filesystem ---`
  - `[overlay_fs] Overlay mounted at: /tmp/containers/demo-c1/merged`
  - `[overlay_fs] Container sees merged view (CoW layer active)`
- `--- Virtual fs mounts ---`
  - `/proc`, `/tmp` (tmpfs, 64 MB), `/dev` (devtmpfs) mounted into the rootfs
- `=== Teardown ===` — unmounts and removes the cgroup.

**Talking points during viva:**
- cgroups v2 files touched: `memory.max`, `memory.high`, `cgroup.subtree_control`.
- OverlayFS layers: `lower` (read-only base) + `upper` (container writes) + `work` (kernel scratch) → `merged` (what the container sees).
- Why copy-on-write: two containers can share the same base image; only their diffs take disk space.

**Live proof:** `cat /sys/fs/cgroup/containers/demo-c1/memory.max` during the demo — should print `134217728`.

---

## Role 3 — CPU Scheduler

**Subsystem:** cgroups v2 CPU quota + `cpu.weight`, weighted round-robin scheduler with ±5% fairness target.

```bash
sudo make role3
sudo ./bin/role3_demo
```

**What the demo prints (summary):**
- `--- Setting up CPU cgroups ---` — creates 3 cgroups with different weights (e.g. 2048, 1024, 512).
  - `[cpu_cgroup] cpu.weight = 2048 (CPU priority relative to siblings)`
  - `[cpu_cgroup] cpu.max = 50000/100000 µs = 50.0% of 1 core`
- `--- Building run queue ---` — scheduler adds containers.
- `--- Weighted Round-Robin scheduling decisions ---`
  - `Tick 1 → Schedule: container-A` … several ticks, container-A is picked more often (higher share).
- `--- Fairness report ---` — table showing `Shares | Expected% | Actual% | Status` with a deviation check (`PASS` if within ±5%).

**Talking points during viva:**
- `cpu.weight` range is 1–10000 (default 100), proportional CPU allocation.
- `cpu.max <quota> <period>` = hard ceiling (e.g., 50000 100000 = max 50% of one core).
- Weighted RR picks the container with the highest `shares / usage_so_far` ratio.

**Live proof:** `cat /sys/fs/cgroup/containers/container-A/cpu.weight` during the run.

---

## Role 4 — Security & Synchronization ⭐ (no sudo needed)

**Subsystem:** Banker's algorithm (deadlock avoidance), POSIX named semaphore (mutual exclusion), safe-state check.

```bash
make role4
./bin/role4_demo
```

**Verified output on this machine:**
- `--- Banker's Algorithm ---`
  - Prints the `Available / Max Need / Allocated / Still Needs` table.
  - Step-by-step: safety check → container request → grant/wait decision → release → re-check.
  - Refuses requests that would lead to an unsafe state, proving deadlock **avoidance** (not just detection).
- `--- Semaphore (Mutual Exclusion) Demo ---`
  - `[semaphore] Created /container_shared_resource with initial value 1`
  - `container-A waiting → acquired → released → container-B waiting → acquired → released`

**Talking points during viva:**
- Three arrays: `Max[]`, `Allocation[]`, `Need[] = Max - Allocation`. Before granting `Request[i]`, run the safety algorithm on the hypothetical post-grant state.
- Why POSIX named semaphores (`sem_open`): they work across unrelated processes (containers) via a filesystem-visible name.
- Functions: `bankers_request`, `bankers_release`, `is_safe_state` (`role4_security_sync.c`).

**This is the safest demo to run live** — no root, no cgroups, no kernel dependencies. Start the presentation with this if the demo machine is flaky.

---

## Role 5 — Monitoring, I/O & Testing

**Subsystem:** Live metrics dashboard (CPU% + memory from `/proc` and cgroups), integration test suite, **disk scheduling simulation (FCFS, SSTF, SCAN, C-SCAN)**.

```bash
sudo make role5
sudo ./bin/role5_demo
```

Note: `make role5` compiles `role5_monitoring.c` **and** `role1_architecture.c` together, because the test suite actually creates real containers via role1's `container_create()`.

**What the demo prints (summary):**
- `--- Live Metrics Dashboard ---` — a redrawn table with columns `Container | CPU% | Memory | Status`, with bar-chart cells.
- `[TEST 1] Container startup latency (target: <500ms)` — creates 5 containers, measures elapsed ms, `PASS`/`FAIL` each.
- `[TEST 2] PID namespace isolation` — prints manual commands to verify inside the container.
- `[TEST 3] Memory limit enforcement` — documents the `stress-ng --vm 1 --vm-bytes 200M` test against a 128 MB limit.
- `[TEST 4] CPU scheduler fairness` — documents the `stress-ng --cpu 1` test across two containers with 2:1 share ratio.
- `[TEST 5] Deadlock prevention` — runs 100 simulated resource-request ops and counts deadlocks (expect 0).
- `[TEST 6] Disk Scheduling Simulation` — runs all 4 disk scheduling algorithms (FCFS, SSTF, SCAN, C-SCAN) on 18 I/O requests from 5 containers and prints a comparison table.
- `═══ All tests complete ═══` — performance summary.

**What TEST 6 prints (disk scheduling detail):**
```
[TEST 6] Disk Scheduling Simulation (Unit VI — I/O Management)
  Disk: 200 cylinders (0–199), head starts at cylinder 53

  Pending I/O queue (18 requests from 5 containers):
    container-A: cylinders [98, 183, 37, 122]
    container-B: cylinders [14, 124, 65, 67]
    container-C: cylinders [43, 0, 190, 75]
    container-D: cylinders [134, 9, 46]
    container-E: cylinders [5, 88, 102]

  --- Algorithm 1: FCFS (First Come, First Served) ---
  Seek sequence: 53 → 98 → 183 → 37 → ...
  Total seek distance: XXXX cylinders

  --- Algorithm 2: SSTF (Shortest Seek Time First) ---
  Seek sequence: 53 → 65 → 67 → 75 → ...
  Total seek distance: XXXX cylinders

  --- Algorithm 3: SCAN (Elevator, moving HIGH first) ---
  Seek sequence: 53 → 65 → 67 → 75 → ...
  Total seek distance: XXXX cylinders

  --- Algorithm 4: C-SCAN (Circular SCAN) ---
  Seek sequence: 53 → 65 → 67 → ... → 190 → 0 → 5 → ...
  Total seek distance: XXXX cylinders

  ╔═══════════════════════════════════════════════════╗
  ║           Disk Scheduling Comparison             ║
  ╠════════════════╦═══════════════╦═════════════════╣
  ║ Algorithm      ║ Seek Distance ║ Notes           ║
  ...
```

**Talking points during viva:**

- **Unit VI — Disk Scheduling (FCFS, SSTF, SCAN, C-SCAN): Test 6**
  - **FCFS:** Services arrival order. O(n), no starvation, worst seek performance. Analogy: serving customers in the queue regardless of where they sit.
  - **SSTF:** Greedy nearest-cylinder pick. Best average seek distance but can **starve** requests at far cylinders if inner requests keep arriving.
  - **SCAN (Elevator):** Head sweeps toward higher cylinders, services everything, then reverses. No starvation. This is what real HDDs do — ask "why is it called the elevator algorithm?"
  - **C-SCAN:** Like SCAN but the head jumps back to 0 after reaching the end without servicing on return. Produces **more uniform wait time** — preferred where fairness across all cylinders matters (e.g., multi-container shared storage).
  - The simulation loads 18 I/O requests from 5 containers — mirrors real multi-container disk contention.

- **Unit VI — I/O Management + I/O Buffering:**
  - `/proc/<pid>/stat` and `/sys/fs/cgroup/<id>/{cpu.stat, memory.current}` are pseudo-device I/O streams.
  - CPU % is computed from **buffered** delta samples (previous reading vs current) — textbook double-buffer I/O. Without buffering the first sample would always be 0%.

- **Unit II — Readers-Writers problem:** the monitor is a **reader** sampling the kernel while containers (writers) update their stats. Classic Readers-Writers synchronization pattern.

- **Unit III — Scheduling criteria verification:** Test 4 measures CPU % for two containers with a 2:1 share ratio and asserts ±5% fairness.

- **Unit IV — Deadlock Detection + Recovery:** Test 5 runs 100 simulated resource requests, detects circular-wait, rolls back offending request (recovery = abort one process).

- **Unit I — OS monitoring / Time-sharing loop:** dashboard repeatedly samples multiple containers — textbook time-shared monitoring. ANSI escape codes (`\033[<N>A`) redraw in place.

**Live proof:** run `systemd-cgtop` in another terminal — should show the same numbers the dashboard is displaying.

---

## Quick cheat sheet for the podium

| Presenter | Build | Run | Sudo? |
|-----------|---------------|--------------------------|------|
| Role 1    | `sudo make role1` | `sudo ./bin/role1_demo` | yes  |
| Role 2    | `sudo make role2` | `sudo ./bin/role2_demo` | yes  |
| Role 3    | `sudo make role3` | `sudo ./bin/role3_demo` | yes  |
| Role 4    | `make role4`      | `./bin/role4_demo`      | **no** |
| Role 5    | `sudo make role5` | `sudo ./bin/role5_demo` | yes  |

Everyone: keep a second terminal open for the "live proof" commands listed under each role — mam loves seeing the kernel-side evidence (`/sys/fs/cgroup/...`, `nsenter`, `systemd-cgtop`).

Good luck!
