# Makefile — Container Orchestration System (Mini Docker)
# ML2011 Operating Systems — VIT Pune 2025-26
#
# Source of truth: src/*.c and include/container.h
# (root-level .c duplicates have been removed)
#
# BUILD & RUN:
#   make role4          → Security & Deadlock demo  (no sudo needed)
#   sudo make role1     → Architecture / namespaces demo
#   sudo make role2     → Memory & storage demo
#   sudo make role3     → CPU scheduler demo
#   sudo make role5     → Monitoring + Disk Scheduling demo
#   make clean          → Remove all binaries
#   make setup          → Create bin/ and include/ directories (run once)

CC      = gcc
CFLAGS  = -Wall -Wextra -g -I./include
LDFLAGS = -lpthread

SRC_DIR = src
BIN_DIR = bin

# Auto-create bin dir before any build target
$(shell mkdir -p $(BIN_DIR))

# ── First-time directory structure setup ────────────────────
# src/*.c are the canonical source files (no root-level copies)
setup:
	mkdir -p src include bin
	@if [ ! -f include/container.h ]; then \
	  cp container.h include/container.h; \
	  echo "  copied container.h -> include/container.h"; \
	fi
	@echo ""
	@echo "Setup complete! Now run your role:"
	@echo "  make role4              # no sudo needed"
	@echo "  sudo make role1         # needs root"
	@echo "  sudo make role5         # monitoring + disk scheduling"

# ── Individual role demos ───────────────────────────────────
role1:
	$(CC) $(CFLAGS) -DROLE1_DEMO \
		$(SRC_DIR)/role1_architecture.c \
		-o $(BIN_DIR)/role1_demo $(LDFLAGS)
	@echo "Built. Run: sudo ./$(BIN_DIR)/role1_demo"

role2:
	$(CC) $(CFLAGS) -DROLE2_DEMO \
		$(SRC_DIR)/role2_memory_storage.c \
		-o $(BIN_DIR)/role2_demo $(LDFLAGS)
	@echo "Built. Run: sudo ./$(BIN_DIR)/role2_demo"

role3:
	$(CC) $(CFLAGS) -DROLE3_DEMO \
		$(SRC_DIR)/role3_scheduler.c \
		-o $(BIN_DIR)/role3_demo $(LDFLAGS)
	@echo "Built. Run: sudo ./$(BIN_DIR)/role3_demo"

role4:
	$(CC) $(CFLAGS) -DROLE4_DEMO \
		$(SRC_DIR)/role4_security_sync.c \
		-o $(BIN_DIR)/role4_demo $(LDFLAGS)
	@echo "Built. Run: ./$(BIN_DIR)/role4_demo"

role5:
	$(CC) $(CFLAGS) -DROLE5_DEMO \
		$(SRC_DIR)/role5_monitoring.c \
		$(SRC_DIR)/role1_architecture.c \
		-o $(BIN_DIR)/role5_demo $(LDFLAGS)
	@echo "Built. Run: sudo ./$(BIN_DIR)/role5_demo"

clean:
	rm -rf $(BIN_DIR)

.PHONY: setup role1 role2 role3 role4 role5 clean
