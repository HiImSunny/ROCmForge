# ROCmForge — System Architecture

**Version**: v0.1 (pre-kickoff detailed design)  
**Date**: Based on AMD ACT II winning patterns research

## High-Level Overview

ROCmForge is a FastAPI-backed multi-agent system that orchestrates an autonomous swarm of LLM-powered specialists. The swarm takes CUDA source code, uses native ROCm tools (hipify + hipcc) running on real AMD Instinct MI300X GPUs via the AMD Developer Cloud, validates correctness, captures deep performance metrics, applies scoped optimizations, and produces production-grade migration artifacts.

**Key Design Goals** (aligned with winning formula):
- Genuine agentic behavior (real tool calling + autonomous decisions, not hardcoded pipeline).
- Deep, visible AMD/ROCm/MI300X integration with real hardware metrics.
- Production-ready from day 1 (Docker, health, isolation, demo/replay).
- Excellent observability for judges (live UI + logs + JUDGING.md).
- 5-day feasible scope: focused on self-contained seeds + strong partial-success path.

## System Components

### 1. Backend (FastAPI + Job System)
- **Job Manager**: Creates isolated workspaces per job (`/jobs/<uuid>/`).
- **Workspace Structure per Job**:
  ```
  /jobs/<uuid>/
  ├── cuda_src/          # Original CUDA sources (seeds or limited upload)
  ├── hip_out/           # Ported HIP sources + build artifacts
  ├── logs/              # Structured agent + tool logs
  ├── metrics/           # amd-smi timeseries, derived JSON
  ├── reports/           # Final migration_report.md + artifacts
  ├── state.json         # Single source of truth JobState (immutable updates preferred)
  └── notes/             # Agent blackboard / scratchpad
  ```
- **Endpoints** (core):
  - POST /jobs (create with seed_id or simple source)
  - GET /jobs/{id}/status
  - GET /jobs/{id}/stream (SSE for live agent activity + metrics)
  - GET /jobs/{id}/report
  - GET /jobs/{id}/artifacts (tar download)
  - POST /demo/seed , POST /demo/replay
  - GET /health (includes GPU + vLLM status)

- **Background Execution**: Simple task queue (or asyncio + background tasks for 5-day simplicity). Each phase can run as a step that updates state.json.

### 2. Agent Swarm Layer
- **Framework**: LangGraph (preferred for state machines, conditional edges, persistence) or lightweight custom ReAct orchestrator if deps need to be minimized.
- **LLM Backend**: vLLM-ROCm running locally on the same MI300X instance (OpenAI-compatible endpoint). Use a strong coding/reasoning model (e.g., Qwen2.5-Coder class). The 192 GB VRAM allows good context + less aggressive quantization.
- **Tool Registry**: All tools are Python functions with clear schemas (for tool calling). Execution is sandboxed (cwd = job dir, timeouts, whitelists).
- **State Machine** (high-level):
  ```
  queued → analyzing → porting (repair loop possible) → validating → benchmarking+profiling → optimizing (scoped) → reporting → completed
  ```
  - Conditional edges: e.g., validation fails → back to porting or to partial report.
  - Orchestrator controls the graph and can replan.

**Agents** (see spec/AGENT_ROLES_AND_PROMPTS.md for full prompts and tools):
- Orchestrator/Planner
- Codebase Analyzer
- HIP Porting Specialist (core AMD depth agent)
- Validator
- Benchmark & Profiler (live amd-smi capture)
- Optimizer (Day 3+ scoped)
- Reporter/Documenter

**Collaboration**:
- Shared JobState (Pydantic model, persisted as JSON).
- Agent notes / blackboard in /notes/.
- Memory: repo-level `memory/porting_patterns.jsonl` (appended after successful jobs, prepended to relevant prompts).

**Observability**:
- Every tool call and LLM decision logged with agent_id, timestamp, input, output, duration.
- SSE events for UI: agent_thought, tool_call, metric_update, phase_change.

### 3. AMD / ROCm Execution Layer (The Hero Part)
- All heavy work happens natively on the MI300X:
  - vLLM-ROCm for agent reasoning (tool calling decisions).
  - hipify (clang preferred) + hipcc for porting.
  - Actual HIP binaries run for validation + benchmarking.
  - amd-smi / rocm-smi for live metrics (utilization, power, temp, clocks, memory BW).
- **Key Metrics Captured** (derived % efficiency vs theoretical peaks):
  - Memory bandwidth (bytes moved / time vs 5.3 TB/s peak).
  - Compute (TFLOPS achieved vs peak for the data type used).
  - Power (avg/peak W), temperature, utilization % during kernel.
- **Profiling**: Basic hipEvent timing + amd-smi sampling. Optional rocprof for kernel-level if time allows.
- **Isolation**: Each job runs in its own workspace. Docker-level device passthrough (`/dev/kfd`, `/dev/dri`).

### 4. Frontend / UI (Gradio Recommended for 5 Days)
- Gradio app (fast to build beautiful live UIs).
- Views:
  - Job list + create (seeds dropdown + limited upload).
  - Live job view: agent activity feed (streaming), file diff viewer, metric cards + live sparklines (util, power, temp), progress bar.
  - Report viewer (rendered MD) + download buttons (report, tar, JSON metrics, trace).
- Demo mode UI elements (big "Replay Seed X" buttons).
- Health status banner.

Alternative: Pure FastAPI + minimal HTML/JS if Gradio is not preferred.

### 5. Docker & Deployment
- Multi-service compose:
  - vllm-brain (ROCm + vLLM)
  - rocmforge-app (FastAPI + Gradio)
- Base image: ROCm official or vLLM quick-start with proper device flags.
- Health checks, volume for jobs/artifacts.
- Documented exact launch steps for AMD Developer Cloud (instance type, image, docker flags, vLLM model + serve command).

### 6. Data & Seeds
- Embedded self-contained seeds (vectorAdd for memory BW, tiled matmul for compute, simple reduction).
- Each seed ships with:
  - Original .cu + minimal host driver.
  - CPU reference implementation (for Validator).
  - Expected high-level behavior description.
- For demo/replay: pre-computed or fast-replay paths that avoid full re-execution when possible.

## Data Flow (Example Successful Seed Job)

1. User submits seed "vectorAdd".
2. Job created → state = analyzing.
3. Analyzer runs → produces structured analysis (kernels, patterns, risks).
4. Orchestrator dispatches to Porting Specialist.
5. Porting: hipify → hipcc fails → reads error + source → applies patch → retries (visible in logs).
6. On success → Validator runs with CPU ref.
7. Benchmark & Profiler: runs binary, live-samples amd-smi, computes % efficiency.
8. Optimizer (if enabled): proposes + applies safe flag / launch bound → re-benchmarks.
9. Reporter synthesizes everything into polished migration_report.md + artifacts.
10. State = completed. UI shows final metrics + "WOW" numbers (e.g., "87% of 5.3 TB/s achieved on real MI300X").

All steps update state.json and emit SSE events.

## Non-Functional / Production Concerns
- **Safety**: Tool execution sandboxed, timeouts, no destructive ops outside job dir, structured error returns.
- **Idempotency / Replay**: Job results are deterministic enough for demo replay.
- **Resource Management**: Monitor GPU usage; one primary MI300X instance for the hackathon.
- **Observability**: Structured logs + JSON state = easy to turn into beautiful evidence for judges.
- **Testing**: Even in 5 days, aim for basic unit tests on parsers/metrics + end-to-end on seeds.

## Diagrams (Text Mermaid — expand in actual docs)

**High-Level Architecture**:
```
User / Judges
   │
   ▼
[Gradio UI / FastAPI]  ← SSE live updates
   │
   ▼
Job Manager (FastAPI)
   │
   ├── Workspace Manager
   │
   ▼
Orchestrator (LangGraph / Agent Graph)
   │
   ├── Analyzer Agent ──tools──► FS / static analysis
   ├── Porting Specialist ──tools──► hipify, hipcc, apply_patch
   ├── Validator ──tools──► run_binary + CPU ref compare
   ├── Benchmark+Profiler ──tools──► run + amd-smi sampler
   ├── Optimizer (scoped)
   └── Reporter ──tools──► synthesize report + tar
          │
          ▼
   vLLM-ROCm (on same MI300X)  ← Agent brains
          │
          ▼
   Real MI300X (hipcc binaries + metrics)
```

**State Transitions** (simplified):
queued → analyzing → porting (loop on repair) → validating → benchmarking → [optimizing] → reporting → completed

## Scope Guardrails for 5 Days
- Focus on 2-3 excellent seeds.
- Full autonomy on seeds; graceful "partial success + high-quality guide" for anything harder.
- Prioritize real AMD metrics + visible agent decisions over perfect ports of complex code.
- Everything must be verifiable in <90 seconds by judges via JUDGING.md path.

This architecture directly implements the winning patterns: genuine agentic + deep visible AMD performance + production signals + judge-friendly presentation.

See spec/ for detailed agent prompts, metrics schema, UI flows, and deployment. See plan/ for the 5-day execution phases that build this incrementally.