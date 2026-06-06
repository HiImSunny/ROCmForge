# ROCmForge — Daily Log & Decision Tracker

**Project**: ROCmForge (CUDA → ROCm Autonomous Agent Swarm on MI300X)  
**Hackathon**: AMD Developer Hackathon ACT II

Use one section per day. Be honest about blockers, decisions, and evidence captured. This becomes gold for the final README / video narrative ("here is how the swarm evolved on real hardware").

---

## Day 0 — Prep & Hardware Verification (Date: Session start — pre-hardware claim)

**Focus**: Get real MI300X instance, verify full stack, run first manual seed end-to-end, capture metrics.

**What was done** (this dev session on Windows machine):
- Full mandatory start ritual executed: read AGENTS.md, CLAUDE.md, latest track/ files (DAILY_LOG, SUBMISSION_CHECKLIST, DAY0_HARDWARE_VERIFICATION), CONTEXT_FOR_NEW_SESSION.md, plan/5DAY_BLUEPRINT_AND_PHASES.md + ARCHITECTURE.md, spec/PRD_ROCMFORGE.md + METRICS_AND_REPORT_SCHEMA.md.
- Confirmed current state: beautiful polished custom Next.js frontend (mocked, wired for SSE) + empty src/ + complete planning artifacts. No backend code yet.
- **Decision**: Start Phase 1 Foundation (non-agent baseline pipeline) + write the 3 self-contained seeds immediately. This is the highest-leverage work while the user claims AMD credits and launches the real MI300X instance (Day 0 hardware verification is still the absolute first thing to do on the actual hardware).
- Created `seeds/vectorAdd.cu`, `tiledMatmul.cu`, `reduction.cu` — minimal, self-contained, with host timing (events), self-checks, and comments for hipify expectations. These match the exact seed IDs in the frontend (vectorAdd, tiledMatmul, reduction).
- Scaffolded core Phase 1 backend:
  - `src/models/job.py` — Pydantic JobState, phases, metrics (raw + derived per METRICS schema), AgentMessage (for feed), etc.
  - `src/workspace/manager.py` — exact layout from ARCHITECTURE (cuda_src/, hip_out/, logs/, metrics/, reports/, state.json).
  - `src/tools/rocm.py` — thin wrappers for hipify/hipcc/amd-smi/run_binary + parse helpers. Clearly supports ROCFORGE_MOCK=1 for local dev (no simulation on real path).
  - `src/baseline/pipeline.py` — full sequential baseline (prepare → hipify → tiny post-fix → hipcc → run + amd-smi capture → validate → derived metrics + efficiency % → report.md following the exact schema + tar).
  - `src/main.py` — FastAPI with POST /jobs, /status, /stream (SSE stub), /report, /artifacts, /demo/seed, /demo/replay, /health. Background task runner. CORS open for cloud.
- Added `requirements.txt`, `src/__init__.py`, `scripts/day0_verify.py` (automates checklist commands for the instance).
- All work strictly scoped to Phase 1 non-agent baseline. No LangGraph, no real agents, no vLLM calls yet.

**Hardware / Environment confirmed**:
- This session: Windows dev machine (PowerShell). All real MI300X execution will happen after user claims credits + launches instance.
- Seeds + pipeline are ready to be `git clone`'d or `scp`'d to the instance and exercised immediately.

**Decisions made**:
- UI framework: keep the existing high-quality custom Next.js "mission control" (already delivered). Do not switch to Gradio.
- Phase order: baseline pipeline (Phase 1) before genuine agents (Phase 2). Visible logs from baseline already give strong "swarm journey" narrative.
- Seeds: exactly the three self-contained ones (vectorAdd for BW, tiledMatmul for compute+shared, reduction for control flow/atomics).
- MOCK mode: explicit env flag so local development of reports, state, SSE shape, and UI wiring is possible without ROCm. All production paths and comments emphasize "real MI300X only".
- Metrics derivation: implemented for vectorAdd (BW % of 5.3 TB/s) and matmul (TFLOPS). amd-smi snapshot + binary stdout parsing.

**Blockers & Risks surfaced**:
- Real hardware verification (Day 0) has not happened yet — must be done first on the instance before trusting any numbers.
- hipify/hipcc/amd-smi behavior will only be known after Day 0 runs (the wrappers are intentionally thin and will be hardened on the instance).
- Frontend is still 100% mock data. Next integration step (after baseline works on hardware) is real SSE + job polling wiring.

**Evidence captured today** (screenshots, logs, json):
- All new source files created under `seeds/`, `src/`, `scripts/`, `requirements.txt`.
- Updated this DAILY_LOG + SUBMISSION_CHECKLIST (see below).
- Seeds are small, reviewable, and directly usable on MI300X.

**Tomorrow plan** (for user):
1. Claim AMD credits → launch MI300X instance (prefer vLLM/ROCm image with Docker device passthrough).
2. On the instance: run `scripts/day0_verify.py`, manually execute at least one full vectorAdd hipify→hipcc→run + amd-smi capture, fill `track/DAY0_HARDWARE_VERIFICATION.md` completely with real output + screenshots.
3. `pip install -r requirements.txt`, `ROCFORGE_MOCK=0 python -m uvicorn src.main:app --host 0.0.0.0 --port 8000` (or Docker).
4. Submit a seed via curl or the (future-wired) frontend → watch full baseline end-to-end on real hardware → capture first automated report + metrics.
5. Update track/ + checklist with the first real MI300X numbers.

**Mood / Confidence**: 8/10 — We pushed hard on making the system "plug in ROCm and go".

Backend Phase 1 foundation is solid and tested.
Frontend is now partially wired to the real FastAPI (job creation calls backend, Live view polls + attempts SSE, components accept real data, download buttons work).
Added Dockerfile.backend + HOW_TO_RUN_WITH_REAL_HARDWARE.md.

Still not 100% "full live" because some UI components still fall back to local animation when no real data arrives, and we haven't done end-to-end testing against a real ROCm environment.

**Evidence from this session (mock execution)**:
- Ran full baseline end-to-end for all 3 seeds via `python scripts/test_baseline.py <seed>`
- vectorAdd (mock): **4601.23 GB/s → 86.8% of 5.3 TB/s**, Validation PASSED, 12 activity messages, full migration_report.md + .tar created.
- tiledMatmul (mock): 1.15 TFLOPS captured + efficiency calc, Validation PASSED.
- reduction (mock): Completed successfully with validation PASSED.
- Workspaces + reports live under `jobs/job_*/` (you can inspect the generated reports right now).
- Report format exactly follows `spec/METRICS_AND_REPORT_SCHEMA.md`.
- `scripts/test_baseline.py` is now the easiest way to exercise Phase 1 locally or on hardware (`ROCFORGE_MOCK=0`).

**Tomorrow plan** (for user):
1. Claim credits + launch real MI300X instance.
2. Run `python scripts/day0_verify.py` + manual vectorAdd port + capture real amd-smi.
3. `ROCFORGE_MOCK=0 python scripts/test_baseline.py vectorAdd` on the instance → get the **first real MI300X numbers** into track/.
4. Start the FastAPI and test via curl or prepare frontend wiring.

---

## Day 1 — Foundation + Baseline Pipeline (to be filled after first real hardware run)

---

## Day 1 — Foundation + Baseline Pipeline

**Focus**: Working non-agent end-to-end on real hardware for at least one seed.

**What was done**:
- [ ]

**Key technical achievements**:
- Job creation + workspace isolation working.
- hipify + hipcc + run + metrics pipeline (baseline).
- Health endpoint.
- First real MI300X numbers from the automated path.

**Decisions / Changes**:
- [e.g., switched to hipify-clang after Perl had issues]

**Blockers**:
- [ ]

**Evidence / Metrics**:
- Link to first automated report + amd-smi capture.
- % efficiency observed on seed:

**Tomorrow plan**:
- Wrap baseline with agent layer (start with Orchestrator + Porting Specialist).

**Mood / Confidence**:

---

## Day 2 — Genuine Agentic Swarm

**Focus**: Agents making visible autonomous decisions and repair loops.

**What was done**:
- [ ]

**Agent behavior observed**:
- Example decision trace (paste sanitized):
  ```
  [Porting Specialist]
  Thought: hipify succeeded on 3 files but hipcc failed with unknown identifier on kernel launch. Reading source...
  Action: apply_patch on vectorAdd.hip.cpp
  Observation: hipcc now succeeds. Moving to validation.
  ```

**Key wins**:
- First successful autonomous repair loop on a seed.
- Live logs / SSE working in UI.

**Blockers**:
- [ ]

**Evidence**:
- Agent trace logs saved.
- UI screenshots of live feed.

**Tomorrow plan**:
- Add Validator + full Benchmark+Profiler with live amd-smi sampling.
- Start collecting impressive metrics.

**Mood / Confidence**:

---

## Day 3 — AMD Depth, Validation, Optimization & Profiling

**Focus**: Real metrics that will make AMD judges happy + scoped optimization.

**What was done**:
- [ ]

**Metrics & Performance Highlights** (update with real numbers):
- Seed 1 (vectorAdd): Achieved XXX GB/s (Y% of 5.3 TB/s), sustained power Z W, util W%.
- Optimizer delta (if any): Before/After improvement.

**Evidence**:
- amd-smi timeseries JSONs.
- Report sections with % efficiency tables.
- Optimizer before/after numbers.

**Blockers**:
- [ ]

**Tomorrow plan**:
- Production polish: Docker, demo/replay, JUDGING.md, full UI.

**Mood / Confidence**:

---

## Day 4 — Production Polish, Demo/Replay, UI & Deployment

**Focus**: Make it judge-proof and easy to verify in <90 seconds.

**What was done**:
- [ ]

**Production artifacts**:
- Docker compose works on MI300X instance.
- Demo/seed + replay endpoints stable.
- JUDGING.md written and tested.
- UI live with agent feed + metrics sparklines.

**Evidence**:
- `docker compose up` logs.
- JUDGING.md content (or link).
- Video draft timestamps.

**Blockers**:
- [ ]

**Tomorrow plan**:
- Narrative, video recording, final README, submission package.

**Mood / Confidence**:

---

## Day 5 — Narrative, Assets, Video & Submission

**Focus**: Ship a complete, polished, winning submission.

**What was done**:
- [ ]

**Final Assets**:
- README.md (link or key excerpts)
- Video (link + description of WOW moment)
- GitHub repo URL
- Live demo URL (or replay evidence)
- All track/ evidence populated

**Submission Form**:
- Title:
- Short description:
- Long description:
- Tags:
- Links added.

**Post-submission notes** (if any):
- [ ]

**Overall retrospective**:
- What worked extremely well for AMD angle:
- What we would do differently:
- Confidence this hits the winning patterns:

---

**Instructions for use**:
- Update this file every evening (even if short).
- Link to specific evidence files in track/ and research/.
- Be specific with numbers and decisions — this becomes source material for the final video script and README "journey" section.

This log proves we built a real, iterative, hardware-grounded project rather than a last-minute prototype.