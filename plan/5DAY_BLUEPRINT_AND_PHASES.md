# ROCmForge — 5-Day Blueprint & Phases (AMD ACT II)

**Project**: ROCmForge — Autonomous Multi-Agent Swarm for CUDA → ROCm Porting, Validation & Optimization on real AMD Instinct MI300X GPUs.

**Goal**: Deliver a production-grade, genuinely agentic system that takes CUDA code (seeds or GitHub), autonomously ports it using ROCm tools (hipify + hipcc), validates correctness, runs deep performance profiling on MI300X, applies scoped optimizations, and produces actionable migration reports + artifacts — all visible, benchmarked, and running natively on the hackathon AMD Developer Cloud credits.

This document is the master execution plan. Follow phases strictly. Capture evidence daily for track/ and submission assets.

---

## Core Principles (Non-Negotiable)

- **Real AMD, real metrics**: Every core job must execute on actual MI300X via ROCm (vLLM-ROCm for agent brains + hipcc/amd-smi for workloads). Show utilization, bandwidth, power, efficiency % vs theoretical peaks.
- **Genuine agentic, not scripted pipeline**: Agents use real tool calling, make autonomous decisions, enter repair loops, collaborate via shared state, and improve over jobs (memory/patterns).
- **Production from day 1**: Docker, health endpoints, job isolation, demo/seed + replay, structured logs, artifacts (tar + MD report).
- **Judge-friendly**: 90-second verifiable path. Strong JUDGING.md with copy-paste commands. Live UI showing agents + metrics spiking in real time.
- **5-day ruthless scope**: Start with 2-3 self-contained seed kernels (vectorAdd for memory, tiled matmul for compute, reduction). Support basic .cu + headers. Full autonomy on seeds; graceful partial + guide for more complex. Max repair loops = 5.
- **Winning formula alignment** (from our WINNING_STRATEGIES_AMD_ACT_II.md):
  - Specific pain + shock metric ("CUDA porting takes weeks → minutes on MI300X").
  - Deep AMD (not wrapper).
  - WOW = live agent decisions + real-time GPU metrics + final impressive efficiency numbers.
  - Narrative, README, JUDGING.md, demo mode.
  - Learning loop.

---

## 5-Day Calendar (July 6-11 2026, UTC kickoff)

Assume kickoff ~15:00 UTC July 6. Submissions close 15:00 UTC July 11.

**Prep / Day 0 (Pre-kickoff or first 2-4 hours)** — Non-negotiable hardware validation
- Sign up / claim AMD AI Developer Program credits if not done.
- Launch 1x MI300X instance (prefer vLLM Quick Start or ROCm base image with Docker + devices).
- Verify stack:
  - `amd-smi` or `rocm-smi` shows GPU (gfx942 / MI300X).
  - `hipify-clang --help` or `hipify-perl`.
  - `hipcc --version`.
  - Torch + ROCm works.
  - vLLM serve (small coder model) works.
- Clone this repo skeleton to the instance.
- Manually run one full baseline on a seed (vectorAdd): copy CUDA → hipify → hipcc compile → run + capture amd-smi json + timing + derived metrics (% of 5.3 TB/s BW).
- Screenshot everything (amd-smi output, successful run, metrics).
- **Milestone**: Hardware confirmed. One manual port + real MI300X metrics captured and saved to track/.

**Phase 1 — Foundation + Baseline Pipeline (Day 1, July 6-7)**
Goal: End-to-end non-agent baseline that works on real hardware.

- FastAPI backend: /jobs create (seed id or simple upload), status poll, artifacts download.
- Job workspace manager: isolated dir per job (`/jobs/<uuid>/{cuda_src/, hip_out/, logs/, reports/, metrics/, state.json}`).
- Baseline flow (hardcoded first):
  1. Prepare workspace (copy seed or safe git clone limited).
  2. Run hipify (tool wrapper around hipify-clang preferred).
  3. Basic post-hipify fixes (common mappings: cuda→hip, Memcpy variants, launch syntax).
  4. hipcc compile (capture full output).
  5. Run benchmark harness (for seeds: timing + correctness against CPU ref).
  6. Capture live-ish amd-smi (or rocm-smi) — json parse for util, power, temp, clocks.
  7. Compute derived: achieved BW/TFLOPS, % efficiency vs MI300X peaks (document constants: 5.3 TB/s HBM, 163.4 TFLOPS FP32, 1307 TFLOPS FP16 matrix, etc.).
  8. Generate basic report.md + tar of artifacts.
- Health endpoint (include GPU status + vLLM ping if used).
- Seed data embedded in repo (self-contained minimal CUDA examples: vectorAdd, matrixMul tiled, reduction).
- Minimal UI stub (Gradio highly recommended for velocity — live job list, submit button, status + log tail).
- Logging + error handling + cleanup.
- **Milestone (end Day 1)**: `curl` or UI submit a seed → full success: ported sources, compiles, runs, metrics with real utilization/power + %eff numbers, downloadable report + tar. All on real MI300X. Screenshot + save to track/.

**Phase 2 — Genuine Agentic Swarm (Day 2, July 7-8)**
Goal: Wrap the baseline with visible, autonomous multi-agent intelligence.

- Choose framework: LangGraph (recommended for stateful graphs + conditional routing) or lightweight custom ReAct orchestrator (to keep deps light).
- Define agents (see spec/AGENT_ROLES_AND_PROMPTS.md for starters):
  - Orchestrator/Planner
  - Codebase Analyzer
  - HIP Porting Specialist (star — drives hipify + repair loops)
  - Validator
  - Benchmark & Profiler
  - (Optimizer on Day 3)
  - Reporter
- Shared blackboard: state.json + /notes/ + memory (porting_patterns.jsonl — successful fixes appended and prepended to prompts).
- Every agent is tool-calling: they decide next action, call tools (run_hipify, run_hipcc, read_file, apply_patch, capture_metrics, etc.), observe results, replan or repair.
- Streaming: SSE or WebSocket for live agent activity feed + metric updates in UI.
- Visible decisions in logs: "Porting agent: hipify partial success on 3/5 files. hipcc failed with 'unknown identifier hipLaunchKernel'. Reading error + kernel source. Applying targeted patch... Retrying (2/5)."
- Learning: After successful job, distill patterns and store for future.
- **Milestone**: Run seed job end-to-end. Observe (in logs/UI) real autonomous tool calls + repair decisions. At least one successful autonomous repair loop on a seed. Still using real MI300X for all execution.

**Phase 3 — AMD Depth, Validation, Optimization & Profiling (Day 3, July 8-9)**
Goal: Make AMD signals impressive and add intelligence depth.

- Robust metrics:
  - Background amd-smi sampler during benchmark (timeseries JSON + sparklines in UI).
  - hipEvent or equivalent for precise kernel timing.
  - Derived efficiency % (memory BW achieved vs 5.3 TB/s, compute vs peaks).
  - Optional: basic rocprof stats (kernel names, durations) if stable.
- Validator agent: correctness harness (CPU ref compare for seeds), flag numerical issues or crashes.
- Scoped Optimizer agent: safe wins only (compile flags --offload-arch=gfx942, O3, launch bounds hints, simple block-size sweep via re-bench, known ROCm perf tips). Log rationale + before/after metrics.
- Improve Porting Specialist: richer error pattern memory, better patch generation (search-replace + unified diff), context from Analyzer.
- Tighten scope for complex inputs: partial success + high-quality migration guide in report.
- **Milestone**: End-to-end autonomous runs on seeds produce data-backed impressive numbers (e.g. "92% of theoretical memory BW, sustained 720W, 94% util during kernel"). Optimizer step shows measurable gain on at least one seed. All artifacts include real captured AMD profiling.

**Phase 4 — Production Polish, Demo/Replay, UI & Deployment (Day 4, July 9-10)**
Goal: Make it judge-proof and easy to verify.

- Dockerization: Base on official ROCm/vLLM image or custom with proper --device /dev/kfd /dev/dri, group video, shm. docker-compose with vLLM service (agent brain) + app service.
- Health/ready endpoints (GPU + vLLM status).
- Strong **Demo Mode**:
  - POST /api/demo/seed → prepares a job with pre-done or fast path.
  - POST /api/demo/replay?job_id=xxx → re-runs only benchmark + metrics capture (fast, stable, no full re-port).
- Full UI (Gradio ideal for 5 days):
  - Job submit (seeds dropdown + "upload simple .cu" limited).
  - Live view: agent activity feed (streaming), file diffs, metric cards + live sparklines (util, power, temp), progress.
  - Report viewer + download (MD + tar + JSON metrics).
- Job persistence + artifact storage (simple volume or local FS with cleanup policy).
- JUDGING.md (complete with copy-paste verification).
- README draft started in parallel (narrative, architecture diagram Mermaid with AMD callouts, stack table, quickstart, evidence section with real screenshots/numbers).
- Deployment docs: exact steps to launch on AMD Developer Cloud (instance type, image, docker flags, vLLM model choice like Qwen2.5-Coder-32B or equivalent that fits in 192GB).
- **Milestone**: `docker compose up` (or equivalent on cloud) → UI live. Submit seed or replay → watch full live swarm + metrics updating in real time on MI300X. Health works. Artifacts downloadable. Judges can verify core claims in <90 seconds with copy-paste from JUDGING.md.

**Phase 5 — Narrative, Assets, Video, Submission Polish (Day 5, July 10-11)**
Goal: Package for maximum impact.

- Finalize:
  - README.md (hook narrative, Mermaid arch, real evidence, limitations honest, feature matrix ✅/🔶/🔲, deployment guide).
  - JUDGING.md (elevator, 90s path, copy-paste, code map, AMD verification section).
  - Architecture diagram asset.
  - Cover image / slide outline.
- Record video (3-4 min, screen + voiceover):
  - Problem hook (CUDA lock-in pain).
  - Submit seed → agents activate visibly (different "personalities" in logs).
  - Live metrics spiking on real MI300X.
  - Final polished report with numbers ("X% efficiency", power, "autonomous repair in 2 loops").
  - Close with "This entire swarm + validation ran natively on AMD Instinct MI300X via ROCm using hackathon credits."
- Test full submission flow on a clean-ish instance if credits remain.
- Populate track/ with final evidence (screenshots, traces, metrics tables).
- Public GitHub push (clean, MIT, all plan/spec/track preserved as proof of process).
- **Milestone (ready to submit)**: All submission requirements complete. Stable demo on AMD cloud. Real perf + autonomy evidence. Cross-checked against winning formula checklist.

**Daily rhythm recommendation**:
- Morning: Hardware sanity (amd-smi, vLLM ping) + capture baseline metrics.
- Core work + lightweight testing (parsers, metric calc, tool wrappers).
- Evening: Full end-to-end seed run on MI300X → screenshots + logs + update track/.
- Commit + push daily. Update track/DAILY_LOG.md.

---

## Risks & Mitigations (Scoped for 5 Days)

- Hipify limitations / complex CUDA → Mitigate by seeds + scoped support + strong "partial + guide" reporter. Agents handle repair loops.
- Resource contention (vLLM brain + heavy benchmark on same MI300X) → Use efficient coder model, batch small, monitor with amd-smi. 192GB is the hero — it helps.
- Demo stability → Heavy investment in seed/replay + cached paths + offline Gradio replay mode.
- Time for "real" autonomy → Build working baseline pipeline first (Phase 1), then layer agents (Phase 2). Visible logs make even partial autonomy impressive.
- Credits exhaustion → One MI300X instance. Front-load hardware validation. Use seeds for most testing.

---

## Success Metrics (Internal + for Judges)

- Autonomous success rate on seeds: ≥80% full port + metrics without manual intervention after initial submit.
- Real MI300X evidence: Multiple jobs with captured amd-smi timeseries, % efficiency numbers, power/thermals.
- Judge verification time: <90 seconds via JUDGING.md path.
- WOW factor: Live agent decisions visible + metrics updating in real time while running on actual AMD hardware.
- Production signals: Docker works, health, artifacts, clear deployment docs.

---

## Next Immediate Actions (Right Now)

1. Complete Day 0 hardware verification on a real MI300X instance and populate `track/DAY0_HARDWARE_VERIFICATION.md`.
2. Read the full research (WINNING_STRATEGIES_AMD_ACT_II.md, PROJECT_IDEAS.md, previous AMD_ACT_I analysis).
3. Create the files listed in the subagent blueprint (plan/, spec/, track/ sections below).
4. Choose concrete seeds + agent framework (LangGraph vs custom) + UI (Gradio).
5. Start Phase 1 baseline pipeline implementation in src/.

This blueprint turns ROCmForge into a standout, AMD-native, agentic, measurable, production-ready submission that directly hits every winning pattern and the specific themes of ACT II (high-performance on real MI300X + ROCm + agents).

Update this file and track/ daily. Let's ship a winner. ⚡

*Source: Combined from local winning research + fresh AMD ACT II context + specialized planner subagent.*