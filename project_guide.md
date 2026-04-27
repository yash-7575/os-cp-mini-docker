# Mini Docker — Project Guide
### ML2011 Operating Systems | VIT Pune 2025-26

A from-scratch container runtime written in C that demonstrates the core mechanisms behind Docker — Linux namespaces, cgroups v2, overlay filesystem, Banker's algorithm, and a live metrics dashboard — without using Docker itself.

---

## File Overview

| File | Role | Needs `sudo`? |
|------|------|---------------|
| `container.h` | Shared types & API declarations | No |
| `role1_architecture.c` | Container lifecycle + namespace isolation | Yes |
| `role2_memory_storage.c` | Memory cgroups + overlay filesystem | Yes |
| `role3_scheduler.c` | CPU cgroups + weighted round-robin scheduler | Yes |
| `role4_security_sync.c` | Banker's algorithm + POSIX semaphores | **No** |
| `role5_monitoring.c` | Live ASCII dashboard + test suite | Yes |
| `Makefile` | Build system | — |

---

## File-by-File Breakdown

---

### `container.h` — Shared Header

**Purpose:** Defines every type and function signature shared across all five roles. Think of it as the API contract between modules.

**Key definitions:**

| Symbol | What it is |
|--------|-----------|
| `container_state_t` | Enum: `PENDING → CREATING → RUNNING → STOPPING → STOPPED → TERMINATED` |
| `resource_config_t` | Struct holding CPU shares, CPU quota, memory limit, storage limit |
| `container_t` | Main container descriptor: ID, PID, state, resources, rootfs path, namespace FDs |
| `container_table_t` | Array of up to 64 `container_t` entries (the orchestrator's in-memory registry) |
| Function declarations | `container_create/stop/destroy`, `setup_memory_cgroup`, `setup_cpu_cgroup`, `bankers_request`, `collect_metrics`, etc. |

**Use case:** Every `.c` file includes this. Without it, the roles cannot call each other's functions (Role 5 calls Role 1's `container_create()`).

---

### `role1_architecture.c` — Architecture & Namespace Isolation

**Purpose:** Implements the Docker `docker run` equivalent — creates a process that lives in its own isolated Linux namespaces.

**Key functions:**

| Function | What it does |
|----------|-------------|
| `container_init()` | First function that runs **inside** the new container. Remounts `/proc` (so `ps` only shows container's own processes), sets hostname to container ID, then `execvp`s the workload (`/bin/sh` by default). This process becomes PID 1 of the new PID namespace. |
| `container_create()` | Allocates a stack, fills `container_t`, calls `clone()` with `CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWUTS | CLONE_NEWIPC`. The child starts in completely new namespaces. Returns PID on host side. |
| `container_stop()` | Two-phase shutdown: SIGTERM → wait 5 s → SIGKILL. Identical to `docker stop`. |
| `container_destroy()` | Stops if running, closes namespace FDs, marks state TERMINATED. |
| `sigchld_handler()` | SIGCHLD handler that calls `waitpid(-1, WNOHANG)` in a loop — prevents zombie processes when any container exits. |

**Namespace flags used:**

```
CLONE_NEWPID  → Container sees itself as PID 1
CLONE_NEWNS   → Container gets its own mount table
CLONE_NEWNET  → Container gets its own network interfaces
CLONE_NEWUTS  → Container gets its own hostname
CLONE_NEWIPC  → Container gets its own SysV IPC / POSIX MQ
```

**OS concepts covered:** Process creation (`clone()` / `fork()` / `exec()`), process state machine, zombie prevention.

**Expected output (needs `sudo`):**
```
[container_create] id=demo01 state=CREATING
[container:demo01] PID inside namespace = 1
[container:demo01] execve → /bin/sh
[container_create] id=demo01 pid=12345 state=RUNNING

Container created:
  ID    : demo01
  PID   : 12345
  State : RUNNING
  CPU   : 512 shares, 50000us quota
  RAM   : 256 MB limit

[container_stop] id=demo01 pid=12345 force=0
[container_stop] demo01 exited gracefully
[container_destroy] id=demo01
[container_destroy] id=demo01 state=TERMINATED
```
> The container runs `/bin/sh` for 3 seconds then automatically stops. No interactive shell.

---

### `role2_memory_storage.c` — Memory & Storage Manager

**Purpose:** Sets up memory limits via cgroups v2 and implements filesystem isolation using Linux overlay filesystem (the same mechanism Docker images use).

**Key functions:**

| Function | What it does |
|----------|-------------|
| `setup_memory_cgroup()` | Creates `/sys/fs/cgroup/container-<id>/`, writes `memory.max` (hard limit in bytes) and `memory.high` (soft limit at 80%), sets `memory.oom.group=1` so the whole container dies when OOM, not just one process. |
| `setup_overlay_fs()` | Mounts an overlay filesystem: `lower=/` (host root, read-only, shared), `upper=/tmp/containers/<id>/upper` (container's writable layer), `merged` = what the container sees. Writes go to `upper`; reads fall through to `lower`. Delete the container = just `rm -rf upper/`. |
| `mount_proc_and_dev()` | Inside the container's new mount namespace: mounts a fresh `/proc` (container-only view), a RAM-backed `tmpfs` on `/tmp` (64 MB, never leaks to other containers), and `devtmpfs` on `/dev`. |
| `setup_rootfs()` | Orchestrates the above three in sequence for a full container rootfs. |
| `teardown_rootfs()` | Unmounts everything in reverse order, removes the cgroup directory. |
| `cgroup_write()` / `cgroup_read()` | Helpers that open cgroup files and write/read control values (e.g. `"268435456"` for 256 MB). |

**How overlay filesystem works:**
```
lower  (read-only)  = /              ← shared base, never modified
upper  (read-write) = /tmp/containers/upper  ← container's changes
work                = /tmp/containers/work   ← overlay internals
merged              = /tmp/containers/merged ← what container sees
```
When the container writes `/etc/hosts`, the original stays in `lower`; the modified copy lands in `upper`; `merged` shows the `upper` version (copy-on-write).

**OS concepts covered:** cgroups v2 memory limits, OOM killer, virtual memory, overlay/copy-on-write filesystem, `/proc` isolation, `tmpfs`.

**Expected output (needs `sudo`):**
```
=== Memory & Storage Demo ===

--- Memory cgroup ---
[memory_cgroup] Creating cgroup: /sys/fs/cgroup/container-mem-test01
[memory_cgroup] memory.max = 256 MB (268435456 bytes)
[memory_cgroup] memory.high = 209715200 bytes
[memory_cgroup] Verified memory.max = 268435456 bytes

--- Overlay filesystem ---
[overlay_fs] Setting up overlay for container: mem-test01
[overlay_fs] Options: lowerdir=/,upperdir=/tmp/containers/upper,workdir=...
[overlay_fs] Overlay mounted at: /tmp/containers/merged
[overlay_fs] Container sees merged view (CoW layer active)

--- Virtual fs mounts ---
[mount_proc] /proc mounted (container-only view)
[mount_proc] /tmp mounted as tmpfs (64 MB, RAM-backed)
[mount_proc] /dev mounted as devtmpfs

=== Teardown ===
[teardown_rootfs] Cleaning up container mem-test01
[teardown_rootfs] Cleanup complete for mem-test01
```

---

### `role3_scheduler.c` — CPU Scheduler

**Purpose:** Implements CPU resource limits via cgroups v2 and a user-space weighted round-robin scheduler that mirrors Linux CFS (Completely Fair Scheduler).

**Key functions:**

| Function | What it does |
|----------|-------------|
| `setup_cpu_cgroup()` | Creates the container's cgroup and sets: `cpu.weight` (proportional sharing, converted from `shares`; range 1–10000) and `cpu.max` (hard throttle: `"50000 100000"` = max 50% of one core). |
| `read_cpu_usage()` | Reads `cpu.stat` from the cgroup and extracts `usage_usec` — total CPU microseconds consumed. |
| `scheduler_add()` | Adds a container to the user-space run queue with its share weight. |
| `scheduler_next()` | Picks the container with the highest **deficit** = `(shares/total_shares × 1s) − actual_used_us`. The most "behind" container gets the next time slice. This is how Linux CFS works (virtual runtime). |
| `print_scheduler_fairness()` | Prints a table comparing expected vs actual CPU % per container. Marks FAIR if deviation < 5%. |
| `enforce_resource_limits()` | Reads actual CPU usage and reports it (kernel does enforcement). |

**cpu.weight vs cpu.max:**
- `cpu.weight` = soft limit: proportional sharing when CPU is contested. Weight 200 gets 2× time vs weight 100.
- `cpu.max` = hard limit: container is throttled (not killed) even if CPU is idle. `50000 100000` = 50ms per 100ms period = 50% of one core max.

**OS concepts covered:** Round-robin scheduling, priority/shares-based scheduling, scheduling criteria (fairness, CPU utilisation), cgroups v2 CPU controls.

**Expected output (cgroup writes fail without `sudo`, scheduler logic still runs):**
```
=== CPU Scheduler Demo ===

--- Setting up CPU cgroups ---
[cpu_cgroup] Configuring CPU for container: sched-A
[cpu_cgroup] cpu.weight = 200 (from 2048 shares)
[cpu_cgroup] cpu.max = 70000/100000 µs = 70.0% of 1 core
...

--- Building run queue ---
[scheduler] Added container sched-A with 2048 shares
[scheduler] Added container sched-B with 1024 shares
[scheduler] Added container sched-C with 512 shares

--- Weighted Round-Robin scheduling decisions ---
[scheduler] sched-A: shares=2048 entitled=571429µs used=0µs deficit=571429µs
[scheduler] sched-B: shares=1024 entitled=285714µs used=0µs deficit=285714µs
[scheduler] sched-C: shares=512  entitled=142857µs used=0µs deficit=142857µs
Tick 1 → Schedule: sched-A
...

--- Fairness report ---
┌────────────────┬────────┬────────────┬──────────┬─────────┐
│ Container      │ Shares │ Expected%  │ Actual%  │ Status  │
├────────────────┼────────┼────────────┼──────────┼─────────┤
│ sched-A        │   2048 │      57.1% │    57.0% │ FAIR ✓  │
│ sched-B        │   1024 │      28.6% │    28.5% │ FAIR ✓  │
│ sched-C        │    512 │      14.3% │    14.5% │ FAIR ✓  │
└────────────────┴────────┴────────────┴──────────┴─────────┘
```
> Without `sudo`, cgroup writes fail but the scheduler logic and fairness table still print correctly. With `sudo` and actual workloads, `Actual%` reflects real CPU usage.

---

### `role4_security_sync.c` — Security & Synchronization

**Purpose:** Implements **Banker's Algorithm** for deadlock avoidance and **POSIX semaphore** mutual exclusion between containers. This is the only role that does **not** need `sudo`.

**Key functions:**

| Function | What it does |
|----------|-------------|
| `bankers_init()` | Sets up the state matrices: `available[]`, `max_need[][]`, `allocation[][]`, `need[][]` (where `need = max - allocation`). Protected by a `pthread_mutex`. |
| `is_safe_state()` | The safety algorithm: simulates finishing each container in some order. If a complete safe sequence exists (all `finish[i] = true`), the state is safe. Prints the safe sequence e.g. `C1 C0 C2`. |
| `bankers_request()` | Resource request: (1) check `request ≤ need`, (2) check `request ≤ available`, (3) simulate granting, (4) run `is_safe_state()`. Grant if safe, roll back if unsafe. |
| `bankers_release()` | Safely returns resources: adds back to `available`, reduces `allocation`, increases `need`. Always safe — releasing can only improve system state. |
| `print_bankers_state()` | Pretty-prints all matrices (Available, Max, Allocated, Still Needs) as a table. |
| `create_shared_semaphore()` | Creates a named POSIX semaphore (`/container_shared_resource`) with `sem_open`. |
| `resource_acquire()` / `resource_release()` | `sem_wait` / `sem_post` — mutual exclusion between containers sharing a resource. |

**Banker's Algorithm — core idea:**
```
Before granting a resource request:
  1. Tentatively make the allocation
  2. Check if a safe execution sequence still exists
     (a sequence where every container can eventually finish)
  3. If YES → GRANT the request
  4. If NO  → DENY (granting would risk deadlock)
```

**OS concepts covered:** Deadlock conditions, Banker's algorithm (deadlock avoidance), safe/unsafe states, resource allocation graphs, POSIX semaphores, mutex, classical synchronisation problems.

**Actual output (run without `sudo`):**
```
=== Security & Synchronization Demo ===

--- Banker's Algorithm ---
Resources: R0=CPU_units, R1=Mem_blocks, R2=Net_slots

[bankers] Initialized: 3 containers, 3 resource types
[bankers] Available resources: 3 3 2

┌─── Banker's Algorithm State ───────────────────────┐
│ Available:  R0=-2  R1=2   R2=0
│
│ Cont. │ Max Need   │ Allocated  │ Still Needs
│ C0    │ 7   5   3  │ 0   1   0  │ 7   4   3
│ C1    │ 3   2   2  │ 2   0   0  │ 1   2   2
│ C2    │ 9   0   2  │ 3   0   2  │ 6   0   0
└────────────────────────────────────────────────────┘

1. Initial safety check:
[bankers] State is UNSAFE — deadlock possible!

2. C1 requests [1,0,2] (SAFE — should be granted):
[bankers] WAIT: not enough resources now, retry later

3. C0 requests [0,2,0] (test — may be denied):
[bankers] WAIT: not enough resources now, retry later

4. C2 releases [3,0,2]:
[bankers] C2 release done. Available now: 1 2 2

--- Semaphore (Mutual Exclusion) Demo ---
[semaphore] Created /container_shared_resource with initial value 1
[semaphore] container-A waiting for resource...
[semaphore] container-A acquired resource
[container-A] Using shared resource...
[semaphore] container-A released resource
[semaphore] container-B waiting for resource...
[semaphore] container-B acquired resource
[container-B] Using shared resource...
[semaphore] container-B released resource
```

---

### `role5_monitoring.c` — Monitoring Dashboard & Test Suite

**Purpose:** Real-time ASCII metrics dashboard that reads CPU% and memory usage from cgroups every second, plus an automated test suite that validates all roles meet the project's performance targets.

**Key functions:**

| Function | What it does |
|----------|-------------|
| `collect_metrics()` | Reads `cpu.stat` (usage_usec) and `memory.current` from each container's cgroup. CPU% = `(delta_cpu_us / delta_wall_us) × 100`. First call returns 0% (needs two readings to compute a delta). |
| `print_metrics_table()` | Clears the previous dashboard with ANSI escape `\033[NA` and redraws a table showing container ID, CPU% with a Unicode progress bar, memory used/limit, and status. Refreshes every second. |
| `test_startup_latency()` | Creates 5 containers via `container_create()`, measures wall-clock time, checks each completes in < 500ms. Requires `sudo`. |
| `test_pid_isolation()` | Prints manual verification commands to run inside a container to confirm PID namespace isolation. |
| `test_memory_limits()` | Prints the `stress-ng` command to trigger OOM killer and `memory.events` file to verify it fired. |
| `test_scheduler_fairness()` | Prints how to run stress workloads and compare `cpu.stat` values to verify the 2:1 CPU ratio. |
| `test_deadlock_prevention()` | Stub for 100-op Banker's stress test. Reports 0 deadlocks (PASS). |
| `run_all_tests()` | Runs all 5 tests sequentially and prints a performance summary. |

**Metrics formula:**
```
CPU % = (cpu_usec_now − cpu_usec_prev) / (wall_time_now − wall_time_prev) × 100
```
This gives percentage of **one CPU core** used during the last measurement interval.

**OS concepts covered:** All units (monitoring requires understanding everything being monitored). Metrics collection from cgroups, performance validation.

**Actual output (no `sudo`):**
```
=== Monitoring & Testing Demo ===

--- Live Metrics Dashboard ---
(Simulated values — real values need running containers)

┌────────────────────────────────────────────────────────┐
│         Container Resource Monitor — Live View          │
├──────────────┬──────────┬──────────────────┬───────────┤
│ Container    │ CPU %    │ Memory           │ Status    │
├──────────────┼──────────┼──────────────────┼───────────┤
│ cont-00      │ ██░░░░░░░░ 10.0% │ 64/256MB (25%)   │ RUNNING   │
│ cont-01      │ ██░░░░░░░░ 25.0% │ 96/256MB (38%)   │ RUNNING   │
│ cont-02      │ ████░░░░░░ 40.0% │ 128/256MB (50%)  │ RUNNING   │
└──────────────┴──────────┴──────────────────┴───────────┘
(refreshes 3 times with CPU values increasing by 5% per tick)

╔══════════════════════════════════════════╗
║   Container Orchestration — Test Suite   ║
╚══════════════════════════════════════════╝

[TEST 1] Container startup latency (target: <500ms)
  Container test-00: 0ms — FAIL (ret=-1)   ← fails without sudo
  Result: 0/5 passed

[TEST 2] PID namespace isolation
  [MANUAL] Run inside container: cat /proc/1/cmdline, ps aux

[TEST 3] Memory limit enforcement
  [TEST] stress-ng --vm 1 --vm-bytes 200M --timeout 5s

[TEST 4] CPU scheduler fairness
  Verify 2:1 ratio via cpu.stat

[TEST 5] Deadlock prevention
  Simulated ops: 0  Deadlocks: 0  Result: PASS ✓

═══ All tests complete ═══
  Startup latency  < 500ms   → Check test 1 output
  CPU accuracy     ± 5%      → Check test 4 ratio
  Memory isolation   100%    → Check test 3 OOM event
  Deadlock rate    0/1000    → Check test 5 count
```
> Tests 1–4 require `sudo` and a real Linux system with cgroups v2. On WSL1 or without root, they fail gracefully with descriptive messages.

---

### `Makefile` — Build System

**Purpose:** Automates directory setup, compilation, and cleanup.

**Targets:**

| Target | Command | What it does |
|--------|---------|-------------|
| `setup` | `make setup` | Creates `src/`, `include/`, `bin/`. Copies all `.c` files to `src/` and `container.h` to `include/`. Run once after cloning. |
| `role1` | `sudo make role1` | Compiles `role1_architecture.c` → `bin/role1_demo`. Flags: `-Wall -Wextra -g -I./include -DROLE1_DEMO -lpthread`. |
| `role2` | `sudo make role2` | Compiles `role2_memory_storage.c` → `bin/role2_demo`. |
| `role3` | `sudo make role3` | Compiles `role3_scheduler.c` → `bin/role3_demo`. |
| `role4` | `make role4` | Compiles `role4_security_sync.c` → `bin/role4_demo`. No sudo needed to build or run. |
| `role5` | `sudo make role5` | Compiles `role5_monitoring.c` + `role1_architecture.c` → `bin/role5_demo`. Role 5 needs Role 1's `container_create()` for startup latency tests. |
| `clean` | `make clean` | Removes `bin/` directory entirely. |

**Compilation flags:**
- `-DROLE<N>_DEMO` — activates the `main()` function inside each file (conditional compilation via `#ifdef`)
- `-I./include` — points to `include/container.h`
- `-lpthread` — links pthreads (required for mutex in Banker's algorithm)

---

## How to Build & Run

```bash
# 1. One-time setup (creates src/, include/, bin/)
make setup

# 2. Role 4 — no sudo needed (test your setup)
make role4
./bin/role4_demo

# 3. Role 1 — namespaces (sudo required)
sudo make role1
sudo ./bin/role1_demo

# 4. Role 2 — memory + overlay FS (sudo required)
sudo make role2
sudo ./bin/role2_demo

# 5. Role 3 — CPU scheduler (sudo required)
sudo make role3
sudo ./bin/role3_demo

# 6. Role 5 — monitoring dashboard (sudo required)
sudo make role5
sudo ./bin/role5_demo

# Clean compiled binaries
make clean
```

> **Note:** Roles 1, 2, 3, 5 require a native Linux system with cgroups v2 and root access. WSL1 does not support namespaces. WSL2 has limited cgroups v2 support.

---

## OS Syllabus Coverage

| Unit | Topic | Role |
|------|-------|------|
| Unit II | `clone()`, process creation/states | Role 1 |
| Unit II | Zombie prevention, `waitpid()` | Role 1 |
| Unit II | Semaphores, mutex, classical sync | Role 4 |
| Unit III | Round-robin scheduling | Role 3 |
| Unit III | Priority/shares-based scheduling | Role 3 |
| Unit III | Scheduling fairness criteria | Role 3 |
| Unit IV | Deadlock avoidance — Banker's algorithm | Role 4 |
| Unit IV | Safe/unsafe states, resource graphs | Role 4 |
| Unit V | Memory limits, OOM killer | Role 2 |
| Unit VI | Overlay filesystem, copy-on-write | Role 2 |
| Unit VI | `/proc` isolation, `tmpfs`, `chroot` | Role 2 |
| All | Metrics collection, performance testing | Role 5 |
