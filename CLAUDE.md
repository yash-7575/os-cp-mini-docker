# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

Academic OS project (VIT Pune, ML2011, 2025-26) implementing a mini Docker-like container orchestration system in C. Each `role*.c` file is an independent demo representing one team member's ~40% implemented subsystem.

## Build Commands

**Source of truth is `src/*.c` and `container.h`** (root-level `.c` duplicates have been removed).
`include/container.h` is the only file still copied by `make setup`.

```bash
# First-time setup (creates include/ with container.h if missing)
make setup

# Build individual role demos
make role4          # No sudo needed (Banker's algorithm — pure userspace)
sudo make role1     # Needs root (clone() + Linux namespaces)
sudo make role2     # Needs root (cgroups + overlay FS mounts)
sudo make role3     # Needs root (CPU cgroups)
sudo make role5     # Needs root (container creation via role1 + disk scheduling)

# Run the built binary
sudo ./bin/role1_demo
./bin/role4_demo    # Only role4 runs without sudo
sudo ./bin/role5_demo   # Includes TEST 6: disk scheduling (FCFS/SSTF/SCAN/C-SCAN)

make clean          # Remove bin/
```

Compiler flags: `gcc -Wall -Wextra -g -I./include -lpthread`

Each `role*.c` file has its own `main()` gated behind `#ifdef ROLE<N>_DEMO`. The Makefile passes `-DROLE<N>_DEMO` when building individually.

## Architecture

**`container.h`** — single shared header defining all cross-role types and function declarations:
- `container_t` — core struct (id, pid, state, resources, rootfs path, namespace FDs)
- `resource_config_t` — CPU/memory/storage limits per container
- `container_table_t` — global array of up to 64 containers
- `container_state_t` enum — `PENDING → CREATING → RUNNING → STOPPING → STOPPED → TERMINATED`

**Role responsibilities:**

| File | Linux mechanism | Key functions |
|------|----------------|---------------|
| `role1_architecture.c` | `clone()` with `CLONE_NEWPID/NS/NET/UTS/IPC` | `container_create`, `container_start`, `container_stop`, `container_destroy` |
| `role2_memory_storage.c` | cgroups v2 (`memory.max`/`memory.high`), overlayfs, chroot | `setup_memory_cgroup`, `setup_rootfs`, `setup_overlay_fs`, `mount_proc_and_dev`, `teardown_rootfs` |
| `role3_scheduler.c` | cgroups v2 (`cpu.weight`, `cpu.max`) + weighted round-robin | `setup_cpu_cgroup`, `read_cpu_usage`, `enforce_resource_limits` |
| `role4_security_sync.c` | Banker's algorithm, POSIX semaphores, SysV IPC/shm | `bankers_request`, `bankers_release`, `is_safe_state` |
| `role5_monitoring.c` | `/proc` + cgroup reads, delta CPU%, **disk scheduling simulation** | `collect_metrics`, `print_metrics_table`, `disk_schedule_fcfs`, `disk_schedule_sstf`, `disk_schedule_scan`, `disk_schedule_cscan` |

**role5 depends on role1 at compile time**: `make role5` compiles `role5_monitoring.c` + `role1_architecture.c` together (`Makefile:70-75`) because role5's monitoring loop invokes `container_create()` from role1.

`container.h` declares `setup_ipc_namespace()` and `apply_seccomp_filter()` for Role 4, but **neither is implemented yet** — they are part of the remaining 60% documented in `README.md`. Do not assume they exist when making changes.

## Implementation Status

Each file is ~40% complete. The remaining 60% per role is documented in `README.md` with exact Claude prompts. Key gaps: REST API (role1), `pivot_root` (role2), dynamic CPU rebalancing (role3), seccomp filters (`-lseccomp`, role4), stress-test runner (role5).

## Linux-Only

All roles except role4's Banker's algorithm require Linux with cgroups v2 mounted and root privileges. Role4 runs on any POSIX system.

**Common first-run failures** (cgroups v2 not mounted, WSL1 lacks namespace support, missing `src/` dir) are documented in `README.md` "Troubleshooting" and `project_guide.md`.
