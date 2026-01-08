.PHONY: all lint format test help run-hello-world run-terminal-bench-modal run-terminal-bench-docker run-namicode-docker run-namicode-daytona

# Default target executed when no arguments are given to make.
all: help

######################
# TESTING AND COVERAGE
######################

# Define a variable for the test file path.
TEST_FILE ?= tests/unit_tests
INTEGRATION_FILES ?= tests/integration_tests

test:
	uv run pytest --disable-socket --allow-unix-socket $(TEST_FILE)

test_integration:
	uv run pytest $(INTEGRATION_FILES)

test_watch:
	uv run ptw . -- $(TEST_FILE)


######################
# RUN DEEPAGENTS WRAPPER
######################

run-hello-world:
	@mkdir -p jobs/hello-world
	harbor run --agent-import-path deepagents_harbor:DeepAgentsWrapper --dataset hello-world --task-name hello-world -n 1 --jobs-dir tmp/hello-world --env docker

run-terminal-bench-modal:
	@mkdir -p jobs/terminal-bench
	harbor run --agent-import-path deepagents_harbor:DeepAgentsWrapper --dataset terminal-bench@2.0 -n 4 --jobs-dir jobs/terminal-bench --env modal

run-terminal-bench-daytona:
	@mkdir -p jobs/terminal-bench
	harbor run --agent-import-path deepagents_harbor:DeepAgentsWrapper --dataset terminal-bench@2.0 -n 40 --jobs-dir jobs/terminal-bench --env daytona

run-terminal-bench-docker:
	@mkdir -p jobs/terminal-bench
	harbor run --agent-import-path deepagents_harbor:DeepAgentsWrapper --dataset terminal-bench@2.0 -n 1 --jobs-dir jobs/terminal-bench --env docker

run-terminal-bench-runloop:
	@mkdir -p jobs/terminal-bench
	harbor run --agent-import-path deepagents_harbor:DeepAgentsWrapper --dataset terminal-bench@2.0 -n 10 --jobs-dir jobs/terminal-bench --env runloop

######################
# RUN NAMI CODE WRAPPER
######################

# Run Nami Code agent on Terminal-Bench with Docker (1 task, local testing)
run-namicode-docker:
	@mkdir -p jobs/namicode
	harbor run --agent-import-path deepagents_harbor:NamiCodeWrapper --dataset terminal-bench@2.0 -n 1 --jobs-dir jobs/namicode --env docker

# Run Nami Code agent on Terminal-Bench with Daytona (10 tasks)
run-namicode-daytona:
	@mkdir -p jobs/namicode
	harbor run --agent-import-path deepagents_harbor:NamiCodeWrapper --dataset terminal-bench@2.0 -n 10 --jobs-dir jobs/namicode --env daytona

# Run Nami Code agent on Terminal-Bench with Modal (4 tasks)
run-namicode-modal:
	@mkdir -p jobs/namicode
	harbor run --agent-import-path deepagents_harbor:NamiCodeWrapper --dataset terminal-bench@2.0 -n 4 --jobs-dir jobs/namicode --env modal

# Run Nami Code agent on specific task (use: make run-namicode-task TASK=code-from-image)
TASK ?= hello-world
run-namicode-task:
	@mkdir -p jobs/namicode-$(TASK)
	harbor run --agent-import-path deepagents_harbor:NamiCodeWrapper --dataset terminal-bench@2.0 --task-name $(TASK) -n 1 --jobs-dir jobs/namicode-$(TASK) --env docker

# Run comparison: DeepAgents vs Nami Code on same task
run-compare:
	@echo "Running DeepAgents wrapper..."
	@mkdir -p jobs/compare-deepagents
	harbor run --agent-import-path deepagents_harbor:DeepAgentsWrapper --dataset terminal-bench@2.0 -n 1 --jobs-dir jobs/compare-deepagents --env docker
	@echo ""
	@echo "Running Nami Code wrapper..."
	@mkdir -p jobs/compare-namicode
	harbor run --agent-import-path deepagents_harbor:NamiCodeWrapper --dataset terminal-bench@2.0 -n 1 --jobs-dir jobs/compare-namicode --env docker

######################
# LINTING AND FORMATTING
######################

# Define a variable for Python and notebook files.
lint format: PYTHON_FILES=deepagents_harbor/ tests/
lint_diff format_diff: PYTHON_FILES=$(shell git diff --relative=. --name-only --diff-filter=d master | grep -E '\.py$$|\.ipynb$$')

lint lint_diff:
	[ "$(PYTHON_FILES)" = "" ] ||	uv run ruff format $(PYTHON_FILES) --diff
	@if [ "$(LINT)" != "minimal" ]; then \
		if [ "$(PYTHON_FILES)" != "" ]; then \
			uv run ruff check $(PYTHON_FILES) --diff; \
		fi; \
	fi
	# [ "$(PYTHON_FILES)" = "" ] || uv run mypy $(PYTHON_FILES)

format format_diff:
	[ "$(PYTHON_FILES)" = "" ] || uv run ruff format $(PYTHON_FILES)
	[ "$(PYTHON_FILES)" = "" ] || uv run ruff check --fix $(PYTHON_FILES)

format_unsafe:
	[ "$(PYTHON_FILES)" = "" ] || uv run ruff format --unsafe-fixes $(PYTHON_FILES)
	

######################
# HELP
######################

help:
	@echo '===================='
	@echo '-- LINTING --'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo '-- TESTS --'
	@echo 'test                         - run unit tests'
	@echo 'test TEST_FILE=<test_file>   - run all tests in file'
	@echo '-- DEEPAGENTS EVALUATION --'
	@echo 'run-terminal-bench-docker    - run 1 task with DeepAgents (Docker)'
	@echo 'run-terminal-bench-daytona   - run 40 tasks with DeepAgents (Daytona)'
	@echo 'run-terminal-bench-modal     - run 4 tasks with DeepAgents (Modal)'
	@echo '-- NAMI CODE EVALUATION --'
	@echo 'run-namicode-docker          - run 1 task with Nami Code (Docker)'
	@echo 'run-namicode-daytona         - run 10 tasks with Nami Code (Daytona)'
	@echo 'run-namicode-modal           - run 4 tasks with Nami Code (Modal)'
	@echo 'run-namicode-task TASK=name  - run specific task with Nami Code'
	@echo 'run-compare                  - compare DeepAgents vs Nami Code'
	@echo '-- DOCUMENTATION tasks are from the top-level Makefile --'


