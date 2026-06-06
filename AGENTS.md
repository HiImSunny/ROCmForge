# AGENTS.md — ROCmForge (AMD Developer Hackathon ACT II)

**Project**: ROCmForge  
**Goal**: Build a genuinely agentic, production-grade multi-agent swarm that autonomously ports CUDA → ROCm/HIP, validates, benchmarks, and optimizes directly on real AMD Instinct MI300X GPUs via AMD Developer Cloud. Deliver measurable performance evidence and clear migration artifacts.

This file is the single source of truth for any new session or sub-agent. **Always read this file first** when starting work on ROCmForge.

---

## Core Principles (Never Break These)

1. **Structure is sacred** — Never work without referencing and updating the dedicated folders:
   - `plan/` — Execution plans, architecture, milestones, risks.
   - `spec/` — Product requirements, agent definitions, schemas, UI flows, deployment.
   - `track/` — Progress, evidence, checklists, daily logs, verification.
   - `research/` — ROCm/hipify/vLLM/amd-smi notes and AMD-specific learnings.
   - `docs/` — Supporting documentation.

2. **Evidence-driven** — Every meaningful step must leave a trace in `track/`. Screenshots, logs, metrics, decisions, and artifacts go here.

3. **Scope ruthlessly** — 5-day hackathon reality:
   - Focus on **2-3 self-contained seeds** (vectorAdd, tiled matmul, reduction).
   - Full autonomy on seeds + graceful "partial success + excellent guide" for harder cases.
   - Do **not** expand to arbitrary large codebases or complex libraries during the event.

4. **Real AMD depth** — Everything that matters must run on actual MI300X via ROCm (vLLM-ROCm for agents + hipify/hipcc + amd-smi profiling). No simulation for the core path.

5. **Winning formula alignment** (from our research):
   - Genuine agentic behavior (real tool calling, autonomous decisions, repair loops, memory).
   - Deep, visible AMD/ROCm/MI300X integration with real metrics (% of theoretical peaks, power, utilization).
   - Production signals (Docker, health, demo/seed + replay, JUDGING.md).
   - Strong narrative + excellent presentation (README + video).
   - One clear WOW moment (live agents + real-time GPU metrics on MI300X).

---

## Folder Usage Rules

**Before doing any implementation or major change:**
- Read relevant files from `plan/` and `spec/`.
- Check `track/SUBMISSION_CHECKLIST.md` and current `track/DAILY_LOG.md`.

**When making progress:**
- Update `track/DAILY_LOG.md` (what was done, blockers, decisions, evidence).
- Update `track/` evidence files (screenshots, metrics, traces).
- If you discover new ROCm/AMD gotchas, append to `research/`.

**When planning or designing:**
- Update or reference `plan/5DAY_BLUEPRINT_AND_PHASES.md`.
- Keep architecture in sync with `plan/ARCHITECTURE.md`.

**Never**:
- Ignore the folders and just write code in `src/`.
- Skip updating `track/` after significant work.
- Expand scope without updating `plan/MILESTONES_AND_RISKS.md`.

---

## Current Project Status (as of last update)

- Detailed pre-hackathon preparation is complete.
- Strong alignment with hackathon theme: AI Agents + High-Performance on real MI300X + ROCm + CUDA porting.
- 5-day blueprint, full specs for agents/metrics/UI/deployment, and tracking system are ready.
- Next real work: Day 0 hardware verification on actual MI300X, then Phase 1 baseline pipeline (non-agent).

See `README_ROCMFORGE.md` for the high-level one-pager and `plan/5DAY_BLUEPRINT_AND_PHASES.md` for the execution roadmap.

---

## How to Start Work in a New Session

1. Read this `AGENTS.md`.
2. Read the latest `track/DAILY_LOG.md` to know where we left off.
3. Read the relevant `plan/` or `spec/` file for the area you're working on.
4. Update `track/DAILY_LOG.md` at the end of significant work.

**Example starting prompt for a new session:**
"Read AGENTS.md, the latest track/DAILY_LOG.md, and plan/5DAY_BLUEPRINT_AND_PHASES.md. We are starting Phase 1 baseline pipeline. Follow the structure."

---

## Key Files to Know

- `plan/5DAY_BLUEPRINT_AND_PHASES.md` — Master execution plan
- `spec/AGENT_ROLES_AND_PROMPTS.md` — Agent definitions and prompts
- `spec/METRICS_AND_REPORT_SCHEMA.md` — What metrics and report structure we need
- `track/SUBMISSION_CHECKLIST.md` — Everything required to win / submit
- `research/ROCm_hipify_vLLM_amd-smi_notes.md` — Living AMD/ROCm technical notes

---

**This file exists so future sessions (or sub-agents) do not lose the discipline of the structure.** Treat it as mandatory reading.

If you are an AI agent working on this project, acknowledge that you have read and will follow AGENTS.md at the start of your work.