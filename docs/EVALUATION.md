# Evaluation Framework Documentation

This document provides comprehensive guidance on setting up and using the Nami-Code evaluation framework, which integrates with **Harbor** for agent evaluation and **LangSmith** for observability and tracing.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Running Evaluations](#running-evaluations)
5. [LangSmith Integration](#langsmith-integration)
6. [Analyzing Results](#analyzing-results)
7. [Available Commands](#available-commands)
8. [Terminal Bench 2.0 Tasks](#terminal-bench-20-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Harbor?

[Harbor](https://github.com/laude-institute/harbor) is an evaluation framework that simplifies running agents on challenging benchmarks. It provides:

- **Sandbox environments** (Docker, Modal, Daytona, Runloop, E2B)
- **Automatic test execution** and verification
- **Reward scoring** (0.0 - 1.0 based on test pass rate)
- **Trajectory logging** in ATIF format (Agent Trajectory Interchange Format)

### What is Terminal Bench 2.0?

[Terminal Bench 2.0](https://github.com/laude-institute/terminal-bench-2) is an evaluation benchmark that measures agent capabilities across several domains:

- **90+ tasks** across software engineering, biology, security, gaming, and more
- Tests agent ability to operate via terminal/computer environment
- Each task has specific instructions, environment setup, and success criteria

**Example Tasks:**
- `path-tracing`: Reverse-engineer C program from rendered image
- `chess-best-move`: Find optimal move using chess engine
- `git-multibranch`: Complex git operations with merge conflicts
- `sqlite-with-gcv`: Build SQLite with code coverage, analyze reports

### DeepAgent Architecture

The Nami-Code harness ships with validated design patterns:

1. **Detailed System Prompt**: Expansive, instructional prompts with tool guidance
2. **Planning Middleware**: `write_todos` tool for structured thinking
3. **Filesystem Tools**: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
4. **SubAgents**: `task` tool spawns specialized subagents for isolated work

---

## Prerequisites

### System Requirements

- **Python**: 3.12+ (required for evaluation framework)
- **uv**: Package manager (recommended)
- **Docker**: For local container execution
- **API Keys**:
  - `ANTHROPIC_API_KEY` - Required for Claude models
  - `LANGSMITH_API_KEY` - Required for tracing
  - `DAYTONA_API_KEY` - Optional, for Daytona cloud sandboxes

### Directory Structure

```
evaluation/
├── Makefile                              # Development commands
├── pyproject.toml                        # Dependencies
├── README.md                             # Original documentation
├── uv.lock                               # Locked dependencies
├── deepagents_harbor/                    # Harbor integration
│   ├── __init__.py
│   ├── backend.py                        # HarborSandbox implementation
│   ├── deepagents_wrapper.py             # DeepAgentsWrapper agent
│   └── tracing.py                        # LangSmith tracing utilities
├── scripts/                              # Analysis scripts
│   ├── analyze.py                        # Result analysis
│   └── harbor_langsmith.py               # LangSmith integration
├── tests/                                # Test suite
└── terminal-bench-2/                     # Git submodule (benchmark tasks)
    ├── adaptive-rejection-sampler/
    ├── bn-fit-modify/
    ├── build-cython-ext/
    └── ... (90+ task directories)
```

---

## Setup

### Step 1: Navigate to Evaluation Directory

```bash
cd evaluation
```

### Step 2: Install Dependencies

```bash
# Install all dependencies
uv sync

# Or with all optional groups
uv sync --all-groups
```

### Step 3: Configure Environment Variables

Create a `.env` file in the `evaluation/` directory:

```bash
# Required: Claude API key for model
ANTHROPIC_API_KEY=sk-ant-...

# Required: LangSmith for tracing
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_TRACING_V2=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=nami-code-evaluation

# Optional: Daytona for cloud sandbox
DAYTONA_API_KEY=...

# Optional: Experiment name for side-by-side comparison
LANGSMITH_EXPERIMENT=nami-code-baseline-v1
```

**Alternative**: Export directly (useful for CI/CD):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export LANGSMITH_API_KEY="lsv2_..."
export LANGSMITH_TRACING_V2=true
export LANGSMITH_EXPERIMENT="nami-code-baseline-v1"
```

### Step 4: Initialize Git Submodule (if needed)

```bash
# Terminal-bench-2 is included as a git submodule
git submodule update --init --recursive
```

---

## Running Evaluations

### Quick Start

#### Run 1 Task Locally (Docker)

```bash
make run-terminal-bench-docker
```

#### Run 10 Tasks on Daytona

```bash
make run-terminal-bench-daytona
```

#### Run 4 Tasks on Modal

```bash
make run-terminal-bench-modal
```

### Direct Harbor Commands

#### Run with Docker (1 task)

```bash
uv run harbor run \
  --agent-import-path deepagents_harbor:DeepAgentsWrapper \
  --dataset terminal-bench@2.0 \
  -n 1 \
  --jobs-dir jobs/terminal-bench \
  --env docker
```

#### Run with Daytona (10 tasks)

```bash
uv run harbor run \
  --agent-import-path deepagents_harbor:DeepAgentsWrapper \
  --dataset terminal-bench@2.0 \
  -n 10 \
  --jobs-dir jobs/terminal-bench \
  --env daytona
```

#### Run with Modal (4 tasks)

```bash
uv run harbor run \
  --agent-import-path deepagents_harbor:DeepAgentsWrapper \
  --dataset terminal-bench@2.0 \
  -n 4 \
  --jobs-dir jobs/terminal-bench \
  --env modal
```

#### Run with Runloop (10 tasks)

```bash
uv run harbor run \
  --agent-import-path deepagents_harbor:DeepAgentsWrapper \
  --dataset terminal-bench@2.0 \
  -n 10 \
  --jobs-dir jobs/terminal-bench \
  --env runloop
```

### Command Parameters

| Parameter | Description |
|-----------|-------------|
| `--agent-import-path` | Import path to the agent wrapper (`deepagents_harbor:DeepAgentsWrapper`) |
| `--dataset` | Benchmark dataset (`terminal-bench@2.0`) |
| `-n` | Number of tasks to run |
| `--jobs-dir` | Output directory for job results |
| `--env` | Sandbox environment (`docker`, `daytona`, `modal`, `runloop`) |

---

## LangSmith Integration

### Overview

LangSmith provides tracing and observability for agent runs. The workflow:

```
Nami-Code → Harbor (evaluate) → LangSmith (analyze) → Improve → Repeat
```

### Setup LangSmith

```bash
# Create .env file with LangSmith credentials
export LANGSMITH_API_KEY="lsv2_..."
export LANGSMITH_TRACING_V2=true
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
```

### Dataset and Experiment Setup

#### Step 1: Create Dataset from Harbor Tasks

```bash
python scripts/harbor_langsmith.py create-dataset terminal-bench --version 2.0
```

#### Step 2: Create Experiment Session

```bash
python scripts/harbor_langsmith.py create-experiment terminal-bench --name nami-code-baseline-v1
```

This outputs a session ID and LangSmith URL for tracking.

### Running with Tracing

#### Option 1: For Experiments (side-by-side comparison)

```bash
export LANGSMITH_EXPERIMENT="nami-code-baseline-v1"
make run-terminal-bench-daytona
```

#### Option 2: For Development (simpler project view)

```bash
export LANGSMITH_PROJECT="nami-code-development"
make run-terminal-bench-daytona
```

#### Option 3: Direct Harbor Command

```bash
export LANGSMITH_EXPERIMENT="nami-code-baseline-v1"
uv run harbor run \
  --agent-import-path deepagents_harbor:DeepAgentsWrapper \
  --dataset terminal-bench@2.0 \
  -n 10 \
  --jobs-dir jobs/terminal-bench \
  --env daytona
```

### Adding Feedback Scores

After benchmark completion, push reward scores to LangSmith:

```bash
python scripts/harbor_langsmith.py add-feedback jobs/terminal-bench/2025-01-08__10-30-00 \
  --project-name nami-code-baseline-v1
```

This matches trials to traces and adds `harbor_reward` feedback (0.0-1.0) from Harbor's test results.

---

## Analyzing Results

### Trajectory Analysis

Each task generates:

- **trajectory.json**: Complete agent interaction trace (ATIF format)
- **stdout.log**: Standard output from the agent
- **stderr.log**: Error messages and warnings
- **test_results.json**: Test pass/fail status and scores

### Common Patterns & Fixes

| Pattern | Symptom | Potential Fix |
|---------|---------|---------------|
| **Poor Planning** | Agent jumps into coding without reading requirements | Add upfront planning requirement to prompt |
| **Incorrect Tool Usage** | Uses `bash cat` instead of `read_file` | Improve tool descriptions with examples |
| **No Incremental Testing** | Writes 200 lines, then tests once | Prompt to test after each logical unit |
| **Hallucinated Paths** | Reads files before checking existence | Add "always `ls` before read" rule |
| **Wrong Model** | Model fails on complex reasoning | Use more capable model for hard tasks |

### Using LangSmith Insights

1. Open LangSmith project/experiment
2. Filter by `harbor_reward` score
3. Compare successful vs. failed runs
4. Use the Insights Agent to identify patterns
5. Review tool calls and agent reasoning traces

### Analyzing Failed Runs

```bash
# List all job directories
ls jobs/terminal-bench/

# Check a specific run
cat jobs/terminal-bench/2025-01-08__10-30-00/trajectory.json | jq

# View test results
cat jobs/terminal-bench/2025-01-08__10-30-00/test_results.json
```

---

## Available Commands

### Makefile Commands

| Command | Description |
|---------|-------------|
| `make test` | Run unit tests (network disabled) |
| `make test_integration` | Run integration tests |
| `make format` | Format code with Ruff |
| `make lint` | Run linters |
| `make run-terminal-bench-docker` | Run 1 task locally with Docker |
| `make run-terminal-bench-daytona` | Run 40 tasks on Daytona |
| `make run-terminal-bench-modal` | Run 4 tasks on Modal |
| `make run-terminal-bench-runloop` | Run 10 tasks on Runloop |
| `make help` | Show all available commands |

### Harbor LangSmith Script Commands

```bash
# Create dataset from Harbor tasks
python scripts/harbor_langsmith.py create-dataset terminal-bench --version 2.0

# Create experiment session
python scripts/harbor_langsmith.py create-experiment terminal-bench --name my-experiment

# Add feedback scores
python scripts/harbor_langsmith.py add-feedback <jobs-dir> --project-name <project>
```

---

## Terminal Bench 2.0 Tasks

The benchmark includes 90+ tasks in various domains:

### Software Engineering
- `build-cython-ext`: Build Cython extension from source
- `build-pov-ray`: Build POV-Ray renderer
- `configure-git-webserver`: Configure git with web server
- `db-wal-recovery`: Database WAL recovery
- `install-windows-3.11`: Install Python Windows 3.11
- `nginx-request-logging`: Configure nginx logging
- `pypi-server`: Set up PyPI server

### Biology & Science
- `bn-fit-modify`: Bayesian network fitting
- `cobol-modernization`: COBOL code modernization
- `dna-assembly`: DNA sequence assembly
- `mcmc-sampling-stan`: MCMC sampling with Stan
- `modernize-scientific-stack`: Modernize scientific Python stack
- `protein-assembly`: Protein structure assembly

### Cryptography & Security
- `crack-7z-hash`: Crack 7z password hash
- `feal-differential-cryptanalysis`: FEAL cryptanalysis
- `feal-linear-cryptanalysis`: Linear cryptanalysis on FEAL
- `fix-code-vulnerability`: Fix security vulnerability
- `password-recovery`: Password recovery

### Gaming & AI
- `chess-best-move`: Find optimal chess move
- `extract-moves-from-video`: Extract moves from video
- `make-doom-for-mips`: Compile Doom for MIPS
- `path-tracing`: Path tracing rendering
- `polyglot-c-py`: Polyglot programming (C/Python)
- `polyglot-rust-c`: Polyglot programming (Rust/C)

### Data & Analytics
- `count-dataset-tokens`: Count dataset tokens
- `distribution-search`: Distribution search
- `financial-document-processor`: Financial document processing
- `mteb-leaderboard`: MTEB benchmark evaluation
- `multi-source-data-merger`: Merge data from multiple sources

### Code & Development
- `cancel-async-tasks`: Cancel async tasks
- `code-from-image`: Generate code from image
- `extract-elf`: Extract ELF binary information
- `filter-js-from-html`: Filter JS from HTML
- `git-leak-recovery`: Recover from git leak
- `git-multibranch`: Complex git operations

### Math & Algorithms
- `circuit-fibsqrt`: Fibonacci square root circuit
- `constraints-scheduling`: Constraint-based scheduling
- `largest-eigenval`: Largest eigenvalue computation
- `portfolio-optimization`: Portfolio optimization
- `prove-plus-comm`: Prove addition commutativity

---

## Troubleshooting

### Common Issues

#### 1. Missing API Keys

**Error**: `AuthenticationError` or 401 status code

**Solution**: Ensure API keys are set in `.env` or exported:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export LANGSMITH_API_KEY="lsv2_..."
```

#### 2. Docker Not Available

**Error**: `docker not found` or connection refused

**Solution**: 
- Install Docker Desktop (Windows/Mac) or Docker (Linux)
- Ensure Docker daemon is running: `docker ps`

#### 3. Python Version Error

**Error**: `requires-python` version conflict

**Solution**: Use Python 3.12+:

```bash
# Check Python version
python --version

# If needed, install Python 3.12
uv python install 3.12
```

#### 4. Harbor Not Found

**Error**: `harbor: command not found`

**Solution**: Use `uv run harbor` instead of direct command:

```bash
uv run harbor run --agent-import-path ...
```

#### 5. Submodule Not Initialized

**Error**: `terminal-bench-2` directory empty

**Solution**: Initialize git submodule:

```bash
git submodule update --init --recursive
```

#### 6. LangSmith Traces Not Linked

**Error**: Runs appear as separate projects

**Solution**: Set `LANGSMITH_EXPERIMENT` environment variable:

```bash
export LANGSMITH_EXPERIMENT="my-experiment-name"
```

#### 7. Daytona/Modal API Errors

**Error**: Authentication or quota errors

**Solution**: Verify API keys and quotas:

```bash
# Check Daytona key
echo $DAYTONA_API_KEY

# Check Modal key
echo $MODAL_API_KEY
```

### Debug Mode

Enable verbose output:

```bash
# Set debug environment
export DEEP_AGENTS_DEBUG=1

# Run with verbose logging
make run-terminal-bench-docker
```

### Logs Location

| Log Type | Location |
|----------|----------|
| Task stdout | `jobs/terminal-bench/<run-id>/stdout.log` |
| Task stderr | `jobs/terminal-bench/<run-id>/stderr.log` |
| Trajectories | `jobs/terminal-bench/<run-id>/trajectory.json` |
| Test results | `jobs/terminal-bench/<run-id>/test_results.json` |

---

## Best Practices

### 1. Start Small

Begin with 1-2 tasks using Docker to verify setup before scaling:

```bash
make run-terminal-bench-docker  # Test setup
make run-terminal-bench-daytona # Scale up
```

### 2. Use LangSmith Early

Set up LangSmith tracing from the start for better debugging:

```bash
export LANGSMITH_EXPERIMENT="nami-code-iteration-1"
```

### 3. Version Your Experiments

Use descriptive experiment names:

```bash
LANGSMITH_EXPERIMENT="nami-code-v0.0.10-baseline"
LANGSMITH_EXPERIMENT="nami-code-v0.0.11-with-planning"
```

### 4. Track Metrics

After each run, add feedback scores to LangSmith:

```bash
python scripts/harbor_langsmith.py add-feedback jobs/terminal-bench/<run> \
  --project-name nami-code-baseline-v1
```

### 5. Compare Iterations

Use LangSmith to compare runs across experiments:

1. Filter by `harbor_reward` score
2. Compare tool usage patterns
3. Identify systematic improvements

---

## References

- [DeepAgents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [Harbor GitHub](https://github.com/laude-institute/harbor)
- [Terminal Bench 2.0](https://github.com/laude-institute/terminal-bench-2)
- [LangSmith](https://smith.langchain.com)
- [Nami-Code GitHub](https://github.com/Babitdor/namicode-cli)

---

## Quick Reference

### One-Line Setup

```bash
cd evaluation
uv sync
cp .env.example .env  # Create and edit .env
# Edit .env with your API keys
```

### Run Evaluation (Docker - 1 task)

```bash
make run-terminal-bench-docker
```

### Run Evaluation (Daytona - 40 tasks)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export LANGSMITH_API_KEY="lsv2_..."
export LANGSMITH_TRACING_V2=true
export LANGSMITH_EXPERIMENT="nami-code-baseline-v1"
make run-terminal-bench-daytona
```

### Add Feedback to LangSmith

```bash
python scripts/harbor_langsmith.py add-feedback jobs/terminal-bench/<run-id> \
  --project-name nami-code-baseline-v1
```