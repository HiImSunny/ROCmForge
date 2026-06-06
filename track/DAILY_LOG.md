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

---

## Current Session — Production Readiness Polish + Mandatory Start Ritual (Windows dev machine)

**Date / Context**: Fresh session following the full AGENTS.md / CLAUDE.md ritual. User provided complete "Full Context for New Session" briefing. Focus per user + plan: finish Phase 1 production signals (Docker, JUDGING.md, resilience, partial-success narrative) while hardware claim is pending. Real MI300X Day 0 verification remains the #1 non-negotiable blocker.

**Ritual executed (mandatory)**:
- Read AGENTS.md (structure sacred, evidence in track/, 3 seeds only, real AMD depth).
- Read CLAUDE.md (no jumping to src/ without plan/track, protect key differentiators).
- Read latest track/DAILY_LOG.md + SUBMISSION_CHECKLIST.md + DAY0_HARDWARE_VERIFICATION.md.
- Read plan/5DAY_BLUEPRINT_AND_PHASES.md + MILESTONES_AND_RISKS.md.
- Checked git status (main, up-to-date with origin; 1 benign local change in frontend/lib/api.ts — small error helper).
- Confirmed list_dir + key files.

**What was done (local, high-leverage, no scope creep)**:
- Verified full Phase 1 baseline still healthy: `ROCFORGE_MOCK=1 python scripts/test_baseline.py vectorAdd` → fresh job, 12 messages, 4601 GB/s (86.8%), validation PASSED, tar + report generated cleanly.
- Created `docker-compose.yml` at root (Phase 1 focused, with crystal-clear device passthrough comments, env notes for MOCK vs real, volumes for jobs/seeds, healthcheck, and future vLLM service skeleton). Matches spec/DEPLOYMENT_AND_CLOUD.md guidance.
- Created `JUDGING.md` (excellent 90-second copy-paste paths for both local mock and real MI300X instance; elevator + shock metric; claims table; demo/replay usage; reproducibility notes; links to all evidence locations). Directly addresses multiple [ ] items in SUBMISSION_CHECKLIST.
- Code polish for resilience + judge experience:
  - Enhanced `/demo/replay` to return rich realistic payload (efficiency, power, util, validation) + clear note pointing to JUDGING.md and real-hardware instructions.
  - Added prominent "Migration Notes & Limitations (Partial Success Path)" section to the generated `migration_report.md`. Explicitly documents that hipify/hipcc can be imperfect on first pass, logs are the source of truth, and Phase 2 agents will do autonomous repair. Prepares the "graceful partial + excellent guide" story required by PRD/plans.
  - Minor health observability notes (mock status is already visible via job messages + reports; real tool availability already reported).
- Confirmed .gitignore, existing Dockerfile.backend, HOW_TO_RUN_WITH_REAL_HARDWARE.md, scripts/, and frontend wiring are all in good shape.
- All new artifacts created in the correct structured folders (no scattering).

**Blockers / Reality check (unchanged)**:
- Real hardware verification on MI300X has still not occurred. DAY0_HARDWARE_VERIFICATION.md remains a template. All numbers and amd-smi in current jobs/ are MOCK.
- Per AGENTS.md, 5DAY_BLUEPRINT, and every checklist: Day 0 on actual hardware (ROCFORGE_MOCK=0, real amd-smi/hipify/hipcc output, real % numbers) is non-negotiable before claiming production metrics or moving deep into Phase 2 agents.
- One tiny uncommitted frontend helper (error extractor) — positive polish, can be committed with next hygiene pass.

**Evidence produced this session**:
- Successful end-to-end test run (new job_8b49a314317d with full artifacts).
- New root files: `docker-compose.yml` + `JUDGING.md` (both referenced as Phase 4 must-haves).
- Improved reports now contain explicit partial-success guidance section.
- This DAILY_LOG entry + implied checklist updates.

**Decisions**:
- Stay ruthlessly in Phase 1 production readiness until real MI300X data exists. No agent skeletons or Phase 2 code yet.
- JUDGING.md + compose are higher immediate value than further UI micro-polish or deeper error parsing (those can follow first real run).
- The baseline messaging already gives strong "agentic journey" narrative even before real agents — lean into that for early demos.

**Tomorrow / Next (user actions + what this session enables)**:
1. **Highest priority (user)**: Claim AMD credits → launch MI300X instance (vLLM/ROCm image preferred) → run `python scripts/day0_verify.py` + `ROCFORGE_MOCK=0 python scripts/test_baseline.py vectorAdd` (or via the new compose) → fill `track/DAY0_HARDWARE_VERIFICATION.md` with real amd-smi, hipify/hipcc logs, power/util, and screenshots. Update DAILY_LOG + SUBMISSION_CHECKLIST.
2. On the instance: `docker compose up -d --build`, hit /health, submit via /demo/seed or UI, download a real tar + report.
3. After first real numbers land: update reports (remove MOCK notes), re-generate JUDGING examples if needed, start light Phase 2 prep (tool registry, memory patterns file, agent role skeletons) only.
4. Commit/push the new production files + this log entry.

**Mood / Confidence**: 8.5/10 for Phase 1 completeness on the software side. The system really is "plug hardware (with ROCFORGE_MOCK=0) and the pipeline + UI + reports + Docker just work." The missing piece is the actual MI300X run that turns all the MOCK impressive numbers into real evidence.

**Files touched / created**:
- docker-compose.yml (new)
- JUDGING.md (new)
- src/main.py (demo_replay + health polish)
- src/baseline/pipeline.py (major: hardened failure paths — now always produce diagnostic report + tar + full error capture even if hipcc fails; also fixed a falsy-bug in compile_success + report timing)
- HOW_TO_RUN_WITH_REAL_HARDWARE.md (updated with new compose + JUDGING emphasis)
- track/DAILY_LOG.md (this entry + previous)

**Important resilience win**: On real MI300X, if hipify or hipcc returns non-zero on first try (very common), the job will now still complete with status=FAILED but you will get a full `migration_report.md`, the tar with all logs + attempted HIP sources, and clear messages. This is exactly what we need for the "partial success + excellent guide" story. Phase 2 agents will later turn those failures into autonomous repair loops.

**Error surfacing (previous)**: [see above]

**This session — Small UI polish + JUDGING.md preparation + Phase status clarification**:

**Small UI polish done**:
- Added `.phase-dot.failed` styling (red) in globals.css and wired it in PhaseTimeline when `status=failed`.
- ReportViewer now auto-detects failure reports (looks for "FAILED" or "hipcc failed") and shows a prominent red warning header + adjusted title.
- Added subtle pulsing dot + "streaming" indicator next to phase estimates in LiveJobView while a job is running.
- These are low-risk, high-visibility improvements that make both success and (especially) real-hardware failure cases look polished for judges.

**JUDGING.md significantly expanded**:
- Updated 90s mock path to mention new UI elements (phase estimates, Recent Jobs status badges, error banners).
- Added dedicated section "**Inspecting Failures & Partial Success (Very Important for AMD Judges)**" with step-by-step how to trigger/observe a diagnostic run, what the red UI looks like, and why the report + tar are still valuable.
- Updated Demo/Replay section with the new `&job_id=` support for loading real previous job reports (success or failure).
- Added new row in the Claims table for graceful failure visibility.
- Strengthened reproducibility section.

**Phase overview & "can we do full Phase 2 now?" answer** (also recorded below):
- Total: **Day 0 (Hardware gate) + 5 Phases**.
- Current reality: Phase 1 software + production signals are very strong (baseline, error hardening, UI wiring, docker, JUDGING, loading states, recent jobs, replay improvements, light Phase 2 artifacts). 
- **However**: Real MI300X runs (Day 0) have still not happened. Per AGENTS.md, 5DAY_BLUEPRINT, MILESTONES, and every checklist — this is the non-negotiable gate before we can credibly claim deep AMD metrics or move into full agentic behavior.
- Recommendation given to user: Continue small polish + light prep is fine. Full Phase 2 agent implementation (real tool-calling repair loops with vLLM-ROCm) should wait until we have at least one solid real-hardware baseline run with actual amd-smi numbers in track/.

All changes tracked. Ready for hardware or more targeted polish.

**2. Loading / estimated time / progress hints**
- Added global `isStarting` state + disabled state on SeedCards during job submission.
- Clear "est. 30-90s" hint under the seed grid + live phase estimate in LiveJobView header (e.g. "Porting: 15-40s (hipify + hipcc)").
- PhaseTimeline now receives `status` and shows "STOPPED ON FAILURE" when relevant.
- Better visual feedback while the swarm is working on real MI300X.

**3. Recent Jobs polish**
- Completely rewrote the inline RecentJobs component.
- Now shows colored status badges (FAILED in danger red, completed in emerald).
- Better layout, tooltips, and explanatory text.
- Clicking a failed job from the list opens LiveJobView which now has excellent error surfacing.
- Real jobs (not just mock) are properly supported thanks to listJobs + full status fetch.

**4. Light Phase 2 preparation (only artifacts, no heavy code)**
- Created `memory/` directory + `memory/porting_patterns.jsonl` with 6 high-quality, real patterns derived from the 3 seeds + common ROCm porting knowledge (hipMemcpy, kernel launch, atomics, arch flag, etc.). Ready for future agents to search/inject.
- Created `plan/PHASE2_AGENT_STATE_MACHINE.md` with detailed Mermaid diagram covering the full agent flow + repair loop + partial failure path.
- Created light agent role skeletons under `agents/`:
  - `orchestrator.md`
  - `porting_specialist.md` (the star agent for visible autonomous repairs)
- These are documentation + data only — implementation will come after hardware is verified.

**5. Other high-value polish**
- Improved `/demo/replay` backend endpoint: now accepts optional `job_id`. If the job exists and has a report, it returns the **real** report markdown (great for replaying actual success or failure diagnostics from previous real runs).
- Frontend `replayDemo` updated to support passing a previousJobId.
- Small cleanups in PhaseTimeline and LiveJobView for failure states.
- All work tracked in DAILY_LOG + todos.

**Overall Phase 1 readiness**: Very strong now. UI is much more judge- and operator-friendly for the inevitable first real-hardware compile issues. Phase 2 has clear starting artifacts without scope creep.

Ready for hardware. Let's get the real MI300X numbers into track/ and make the checklist green on the AMD depth column.

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