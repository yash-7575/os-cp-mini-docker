# Role → OS Syllabus Mapping

Mini Docker — Container Orchestration System (ML2011, VIT Pune 2025-26)

This document maps each team member's subsystem to the exact units and topics of the ML2011 Operating Systems syllabus. Use it to answer "which OS concept is your part implementing?" during viva.

Syllabus reference: `os_syllabus.md` (Units I–VI).

---

## Role 1 — Architecture Lead (`role1_architecture.c`)

**Subsystem:** Container lifecycle, Linux namespaces, process creation.

### Syllabus coverage

| Unit | Topic | How this role implements it |
|------|-------|-----------------------------|
| **Unit I** — Introduction to OS | **System calls, types of system calls** | Uses `clone()`, `execve()`, `waitpid()`, `kill()` — direct system calls into the Linux kernel. The demo prints the call path on each lifecycle event. |
| **Unit I** | **OS Services** | Provides process creation / destruction services to the upper layer (the rest of the "Mini Docker"). |
| **Unit II** — Process Management | **Process concept, Process Control Block (PCB)** | The `container_t` struct (`container.h:32-42`) *is* the PCB: PID, state, resource config, rootfs path, namespace FDs, timestamp. |
| **Unit II** | **Process states — 5-state / 7-state model** | Implements a 6-state model: `PENDING → CREATING → RUNNING → STOPPING → STOPPED → TERMINATED` (`container.h:8-15`). Maps directly to the textbook 7-state diagram (no swapped-out states because we don't swap). |
| **Unit II** | **Process description, process control** | `container_create`, `container_start`, `container_stop`, `container_destroy` — the classical process-control primitives (create / dispatch / suspend / terminate). |
| **Unit II** | **Multithreading — kernel-level threads** | `clone()` with `CLONE_NEWPID/NS/NET/UTS/IPC` creates a new kernel-scheduled task with isolated namespaces — a kernel thread with its own "view" of the OS. |
| **Unit II** | **SIGCHLD zombie reaping** | The `SIGCHLD` handler in `role1_architecture.c` near line 326 reaps zombie children, a classic Unit-II concurrency problem. |

**Viva one-liner:** "My part implements Unit II Process Management — the PCB, the process state machine, and the `clone()` system call from Unit I."

---

## Role 2 — Memory & Storage (`role2_memory_storage.c`)

**Subsystem:** Memory limits via cgroups v2, OverlayFS rootfs, virtual filesystem mounts.

### Syllabus coverage

| Unit | Topic | How this role implements it |
|------|-------|-----------------------------|
| **Unit V** — Memory Management | **Memory management requirements — protection, sharing, logical organization** | cgroups v2 `memory.max` enforces **protection** (hard cap per container); `memory.high` gives soft throttling. |
| **Unit V** | **Memory partitioning — fixed / dynamic** | Each container gets a **fixed partition** of RAM (e.g., 128 MB) through `memory.max`. The host OS dynamically allocates physical pages under that cap. |
| **Unit V** | **Virtual Memory — VM with paging, swapping** | `memory.high` triggers proactive reclaim (page-out equivalent). When a container exceeds the limit, the kernel OOM killer fires — textbook thrashing / OOM handling. |
| **Unit V** | **Swapping issues — thrashing** | Demonstrable via `stress-ng --vm 1 --vm-bytes 200M` against a 128 MB cap — watch `/sys/fs/cgroup/<id>/memory.events` for `oom_kill 1`. |
| **Unit VI** — I/O and File Management | **File organization, file sharing** | OverlayFS: `lower` (shared read-only base) + `upper` (per-container writes) + `merged` (what the container sees). Classic file-sharing via copy-on-write. |
| **Unit VI** | **Secondary storage management, free space** | `storage_limit_mb` in `resource_config_t` maps to disk quotas. The overlay upper dir is the only space that grows per container. |
| **Unit VI** | **File directories, mount points** | `mount_proc_and_dev()` sets up `/proc`, `/tmp` (tmpfs), `/dev` (devtmpfs) — each container gets its own file-directory tree. |

**Viva one-liner:** "My part implements Unit V Memory Management (cgroup memory limits + OOM = the protection + swapping concepts) and Unit VI File Management (OverlayFS = file sharing with copy-on-write)."

---

## Role 3 — CPU Scheduler (`role3_scheduler.c`)

**Subsystem:** CPU cgroups (`cpu.weight`, `cpu.max`), weighted round-robin scheduler with fairness guarantee.

### Syllabus coverage

| Unit | Topic | How this role implements it |
|------|-------|-----------------------------|
| **Unit III** — Process Scheduling | **Types of scheduling — long / medium / short term** | Adding a container to the run queue = **long-term admission**. Tick-by-tick `Schedule: container-X` decisions = **short-term dispatcher**. |
| **Unit III** | **Preemptive vs Non-preemptive scheduling** | The weighted round-robin loop picks a *different* container each tick based on `shares / usage` ratio — classic preemptive behavior. |
| **Unit III** | **Scheduling algorithms — Round Robin (RR)** | Implemented directly as Weighted RR. Each container gets a time slice proportional to its `shares`. |
| **Unit III** | **Scheduling algorithms — Priority** | `cpu.weight` (range 1–10000) **is** a priority number; higher weight → more CPU. Demo shows a 2048 vs 1024 ratio producing ~66.7% vs 33.3% CPU. |
| **Unit II** — Process Management | **Process states during scheduling** | The scheduler transitions containers between `RUNNING` (currently scheduled) and waiting (ready but not picked this tick). |

*(Scheduling-criteria measurement and ±5% fairness verification are owned by Role 5 — Role 3 owns the algorithm, Role 5 owns the verification.)*

**Viva one-liner:** "My part implements Unit III Process Scheduling — specifically weighted Round Robin with `cpu.weight` as the priority knob, covering the short-term dispatcher, preemptive type, and Priority algorithm."

---

## Role 4 — Security & Synchronization (`role4_security_sync.c`) ⭐

**Subsystem:** Banker's algorithm (deadlock avoidance), POSIX semaphores (mutual exclusion), safe-state verification.

### Syllabus coverage

| Unit | Topic | How this role implements it |
|------|-------|-----------------------------|
| **Unit II** — Process Management | **Concurrency — issues with concurrency** | Multiple containers competing for shared resources (CPU units, memory blocks, network slots) without stepping on each other. |
| **Unit II** | **Mutual Exclusion — OS support: Semaphores** | `sem_open("/container_shared_resource", ...)` — POSIX **named** semaphore. The demo shows container-A and container-B alternating acquisition. |
| **Unit II** | **Classical synchronization — Producer-Consumer, Dining Philosophers** | The semaphore demo is a minimal Producer-Consumer pattern. The Banker's three-resource model is a generalised Dining-Philosophers arrangement. |
| **Unit IV** — Deadlocks | **Principles of deadlock — 4 conditions** | Mutual exclusion, hold-and-wait, no preemption, circular wait — all present in the resource model, which is why an algorithm is needed. |
| **Unit IV** | **Deadlock Prevention** | The semaphore enforces single-access (breaks hold-and-wait when used correctly). |
| **Unit IV** | **Deadlock Avoidance — Banker's Algorithm** | **Core of this role.** `bankers_request()` simulates the grant, runs `is_safe_state()`, and only commits if the resulting state is safe. See the `Available / Max / Allocated / Still Needs` table in the demo output. |

*(Deadlock Detection and Recovery are owned by Role 5 via Test 5; the Readers-Writers classical problem is owned by Role 5 via the monitor-as-reader pattern.)*

**Viva one-liner:** "My part implements Unit IV Deadlock **Prevention + Avoidance** — the Banker's algorithm as the safe-state checker — plus Unit II's mutual-exclusion-via-semaphore and the Producer-Consumer classical problem."

---

## Role 5 — Monitoring, I/O & Verification (`role5_monitoring.c`) ⭐

**Subsystem:** Live resource dashboard, I/O sampling from `/proc` + cgroups, integration test suite, deadlock detection, and **disk scheduling simulation (FCFS, SSTF, SCAN, C-SCAN)**.

### Syllabus coverage

| Unit | Topic | How this role implements it |
|------|-------|-----------------------------|
| **Unit I** — Introduction to OS | **Basic functions of OS — resource management, monitoring** | The live dashboard is the "OS activity monitor" concept — it reads `/proc` and cgroup files, which are the kernel's standard monitoring interface. |
| **Unit I** | **OS Services — accounting** | CPU % (delta between samples) and memory usage are the textbook "accounting" service. |
| **Unit I** | **Types of OS — Time-Sharing / Multiprogramming** | The dashboard repeatedly samples multiple containers on a tick — that is the textbook time-shared monitoring loop. |
| **Unit II** — Process Management | **Classical synchronization — Readers-Writers problem** | The monitor is a **Reader** that samples `/proc` while containers (the **Writers**) update their stats. Classic Readers-Writers pattern implemented in the sampling loop. |
| **Unit II** | **Symmetric Multiprocessing (SMP)** | CPU-% delta computation is per-core aware — the dashboard works correctly on multi-core hosts where containers may be scheduled on different CPUs simultaneously. |
| **Unit III** — Process Scheduling | **Scheduling criteria — CPU utilization, throughput, fairness** | Test 4 and the live fairness report **measure** the ±5% deviation target. Role 3 owns the algorithm; this role owns the criteria-measurement side. |
| **Unit IV** — Deadlocks | **Deadlock Detection** | Test 5 runs 100 simulated resource requests, detects circular-wait occurrences, and reports a deadlock count (target: 0 / 1000). |
| **Unit IV** | **Deadlock Recovery** | When detection fires, the test logs the offending request and rolls it back — that is the "abort one process" recovery strategy from the textbook. |
| **Unit VI** — I/O & File Management | **I/O Management — I/O devices, characteristics** | Pseudo-devices `/proc/<pid>/stat`, `/sys/fs/cgroup/<id>/cpu.stat`, `.../memory.current` are read as kernel-exported I/O streams. `collect_metrics()` is the device-driver wrapper. |
| **Unit VI** | **I/O Buffering** | CPU-% is computed from **buffered** delta samples (previous reading vs current). Without buffering the first sample would always be zero — this is textbook double-buffer I/O. |
| **Unit VI** | **Disk Scheduling — FCFS** | Test 6 simulates 18 I/O requests from 5 containers. FCFS services them in arrival order — simple, no starvation, but worst seek distance. Demonstrates O(n) traversal. |
| **Unit VI** | **Disk Scheduling — SSTF** | Shortest Seek Time First: at each step picks the cylinder nearest the current head position. Best average seek time but can **starve** requests at far cylinders — illustrated in test output. |
| **Unit VI** | **Disk Scheduling — SCAN (Elevator)** | Head sweeps high, services all requests along the way, then reverses. No starvation. This is the algorithm used inside real HDDs. Mapped directly from textbook elevator analogy. |
| **Unit VI** | **Disk Scheduling — C-SCAN** | Like SCAN but the head jumps back to cylinder 0 after reaching the end instead of reversing. Produces more **uniform wait times** across all cylinders — preferred for fairness in multi-container I/O. |
| **Cross-cutting** | **Performance targets — acceptance suite** | Startup < 500 ms (Unit II) • CPU fairness ± 5 % (Unit III) • memory isolation 100 % (Unit V) • deadlock rate 0 / 1000 (Unit IV) • disk scheduling validated (Unit VI). Every unit verified here. |

**This role spans FIVE units of the syllabus** (I, II, III, IV, VI) — the widest coverage in the project.

**Viva one-liner:** "My part owns Unit VI completely — I/O buffering, and all four disk scheduling algorithms (FCFS, SSTF, SCAN, C-SCAN) running against simulated container I/O — plus Readers-Writers from Unit II, scheduling-criteria verification from Unit III, deadlock detection + recovery from Unit IV, and the cross-unit acceptance test suite."

---

## Quick syllabus-to-role lookup

When mam asks "who covers Unit X?" —

| Syllabus unit | Primary owner | Secondary owners |
|---------------|--------------|------------------|
| **Unit I** — Introduction to OS, system calls | Role 1 (clone/execve) | Role 5 (monitoring, time-sharing loop) |
| **Unit II** — Process Management, Concurrency | Role 1 (PCB, states, kernel threads) | Role 4 (semaphores, mutex, Producer-Consumer) • Role 5 (Readers-Writers, SMP) |
| **Unit III** — Process Scheduling | Role 3 (RR + Priority algorithms) | Role 5 (scheduling-criteria verification) |
| **Unit IV** — Deadlocks | Role 4 (Prevention + Avoidance / Banker's) | Role 5 (Detection + Recovery via Test 5) |
| **Unit V** — Memory Management | Role 2 (cgroups memory, OOM, thrashing) | Role 5 (OOM test) |
| **Unit VI** — I/O & File Management | Role 2 (File Management: OverlayFS, mounts) | **Role 5** (I/O Buffering + **Disk Scheduling: FCFS, SSTF, SCAN, C-SCAN** via Test 6) |

Every unit of the syllabus is covered. After rebalancing, workload is spread:
- Role 1 → 2 units (I, II)
- Role 2 → 2 units (V, VI-files)
- Role 3 → 1 unit + partial (III, II-states)
- Role 4 → 2 units (II-sync, IV-prevention/avoidance)
- Role 5 → 5 units (I, II-RW/SMP, III-criteria, IV-detection, VI-I/O)

Good luck with the presentation!
