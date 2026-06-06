# ROCmForge — Milestones, Risks & Success Gates

This document defines clear, verifiable milestones per phase and the main risks with mitigations. Use it to stay on track during the 5-day sprint and for daily stand-ups (even if solo).

## Overall Success Definition (What "Perfect" Looks Like at Submission)

- A genuinely autonomous multi-agent swarm (visible decisions + repair loops) that successfully ports, validates, benchmarks, and (optionally) optimizes at least 2 self-contained CUDA seeds.
- All heavy work (agent reasoning via vLLM + HIP execution + profiling) runs natively on a real AMD Instinct MI300X via the hackathon credits.
- Quantified, impressive performance metrics captured on the actual hardware (utilization, power, % of theoretical peaks such as 5.3 TB/s HBM bandwidth).
- Production-grade signals: Docker works, health endpoints, stable demo/seed + replay, clean artifacts.
- Judge-friendly package: Excellent README + JUDGING.md that allows full verification in <90 seconds, strong video with early WOW moment (live agents + real MI300X metrics updating).
- Clear narrative: "CUDA lock-in solved autonomously on real AMD hardware in minutes, not weeks."

If the above is green with real artifacts from MI300X, we have a top-tier AMD-native submission.

---

## Phase-by-Phase Milestones (Verifiable Exit Criteria)

### Day 0 / Prep — Hardware & Baseline Confidence Gate
**Exit Criteria** (must be green before heavy coding):
- [ ] Real MI300X instance launched and verified (`amd-smi` / `rocm-smi` shows gfx942 + ~192 GB memory).
- [ ] Core toolchain works: `hipify-clang` (or Perl), `hipcc --version`, hipcc can target gfx942.
- [ ] vLLM-ROCm can serve a coding/reasoning model (OpenAI-compatible endpoint reachable).
- [ ] One full manual seed (e.g. vectorAdd) completed end-to-end on the instance:
  - hipify → hipcc compile success
  - Binary runs + produces correct output
  - amd-smi / rocm-smi captured during the run (util, power, temp)
  - Rough efficiency % calculated (e.g. "X% of 5.3 TB/s")
- [ ] Screenshots + key outputs saved to `track/DAY0_HARDWARE_VERIFICATION.md`
- [ ] First entries added to `research/ROCm_hipify_vLLM_amd-smi_notes.md`

**Risk if not met**: Everything later is built on fantasy hardware. Block and resolve.

### Phase 1 — Foundation + Baseline Pipeline (End of Day 1)
**Exit Criteria**:
- [ ] FastAPI app with job creation, workspace isolation, and status polling.
- [ ] End-to-end automated pipeline on at least one seed (no agents yet):
  - hipify + basic post-processing
  - hipcc compile
  - Run + validation (CPU ref compare)
  - Metrics capture (amd-smi) + derived % efficiency
  - Basic report.md + tar artifact generated
- [ ] Health endpoint returns GPU + basic status.
- [ ] Minimal UI stub (Gradio or simple HTML) that can submit a seed and show status + download links.
- [ ] All execution happened on real MI300X (not simulation).
- [ ] Evidence: screenshots of successful automated run + first real metrics from the code path, saved in track/.

**Success Signal**: `curl` (or UI) submit → full success artifacts with real MI300X numbers in < a few minutes.

### Phase 2 — Genuine Agentic Swarm (End of Day 2)
**Exit Criteria**:
- [ ] Multi-agent layer in place (Orchestrator + at least Porting Specialist + Analyzer).
- [ ] At least one seed runs with visible autonomous behavior:
  - Agents make tool calls (hipify, hipcc, read, patch).
  - At least one successful repair loop (error → patch → recompile success) without human intervention.
  - Decisions logged with "Thought / Action / Observation" style in logs and UI.
- [ ] Streaming / live agent activity feed working in the UI (SSE or equivalent).
- [ ] Basic memory / pattern storage started (even if simple).
- [ ] Still 100% on real MI300X hardware.
- [ ] Evidence: sanitized agent trace examples in `track/AGENT_TRACE_EXAMPLES.md`, UI screenshots of live feed during a repair.

**Success Signal**: Watching the UI or logs, you can clearly see the agents "thinking" and fixing issues autonomously.

### Phase 3 — AMD Depth, Validation, Optimization & Profiling (End of Day 3)
**Exit Criteria**:
- [ ] Robust live metrics:
  - Background amd-smi / rocm-smi sampler during benchmark.
  - Timeseries stored + basic sparklines or cards in UI.
  - Derived efficiency calculations (% of theoretical peaks) in reports.
- [ ] Validator agent working on seeds (correctness + numerical closeness reported).
- [ ] Scoped Optimizer (at minimum on one seed): proposes/applies safe change (flags, launch bounds, etc.) and shows measurable before/after delta.
- [ ] Reports now contain impressive, data-backed numbers (e.g., "87% of 5.3 TB/s achieved, sustained 680W, 94% util").
- [ ] Evidence: multiple jobs with rich metrics JSON, before/after optimizer numbers, updated reports.

**Success Signal**: The metrics section of the generated report looks professional and AMD-judge-impressive.

### Phase 4 — Production Polish, Demo/Replay, UI & Deployment (End of Day 4)
**Exit Criteria**:
- [ ] Docker + docker-compose works cleanly on the MI300X instance (devices, groups, health).
- [ ] Strong demo modes:
  - `/api/demo/seed` prepares fast jobs.
  - `/api/demo/replay?job_id=xxx` re-runs only benchmark + metrics (fast and stable).
- [ ] Full JUDGING.md written, tested, and contains copy-paste 90-second verification path.
- [ ] UI is functional and polished enough: live agent feed, metric cards + updates, report viewer, download buttons.
- [ ] Health endpoints are rich (GPU status, vLLM reachable, etc.).
- [ ] Deployment docs started (exact AMD Cloud launch steps).
- [ ] Evidence: `docker compose up` logs, working replay demo, completed JUDGING.md, UI screenshots.

**Success Signal**: A fresh person (or judge) can follow JUDGING.md and verify the core claims in under 90 seconds with copy-paste commands.

### Phase 5 — Narrative, Assets, Video & Submission (End of Day 5)
**Exit Criteria**:
- [ ] Final README.md (strong hook narrative, Mermaid architecture with AMD callouts, real evidence with numbers/screenshots, stack table, demo flow, honest limitations + feature matrix ✅/🔶/🔲).
- [ ] High-quality video (2-4 min, audio, early WOW moment showing live agents + real MI300X metrics, clear narrative close).
- [ ] All submission elements ready (cover image ideas, slide outline, descriptions, tags).
- [ ] GitHub repo public, clean, with plan/spec/track preserved.
- [ ] Live demo (or very strong replay + evidence) stable on AMD Cloud.
- [ ] Full track/ populated (DAY0, daily logs, metrics evidence, submission checklist green).
- [ ] Internal cross-check against WINNING_STRATEGIES_AMD_ACT_II.md and SUBMISSION_CHECKLIST.md complete.

**Success Signal**: Everything required for submission is done and the project tells a compelling, evidence-backed story of real AMD high-performance agentic work.

---

## Major Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation / Contingency |
|------|------------|--------|--------------------------|
| Hardware / credits issues or MI300X not behaving as expected | Medium | High | Day 0 is non-negotiable verification gate. Have fallback seeds that are known to be simple. Document everything. |
| hipify + repair loops take too long or fail on seeds | Medium | Medium-High | Scope to 2-3 excellent seeds. Cap repair loops (e.g. 5). Strong "partial success + excellent migration guide" path in Reporter. Pre-load common mappings in memory. |
| Resource contention (vLLM brain + heavy HIP benchmarks on same GPU) | Medium | Medium | Use efficient model + good gpu-memory-utilization. Run benchmarks with representative but not maximum sizes. Monitor with amd-smi. The 192 GB is a big advantage here. |
| Demo / replay not stable for judges | Medium | High | Heavy investment in seed + replay modes. Pre-capture rich evidence (traces, metrics, reports). Offline Gradio replay of traces + metrics as backup. |
| Not enough "WOW" or AMD-specific depth | Low-Medium | High | Prioritize live agent visibility + real metrics (% efficiency, power, utilization) from Day 1. Every report and the video must scream "this ran on real MI300X via ROCm". |
| Scope creep (trying to support arbitrary large CUDA projects) | High | High | Ruthless scoping in PRD and daily stand-ups. Seeds + clear "extend this yourself" guide is the deliverable. |
| Time for both deep agentic behavior and production polish | Medium | Medium | Front-load working baseline (Phase 1) and real hardware metrics. Layer autonomy and polish in parallel where possible. JUDGING.md and README written in parallel with code. |
| LLM agent reliability (hallucinations in patches, bad decisions) | Medium | Medium | Strong system prompts + few-shot memory patterns + limited repair loops + good error context. The "visible autonomy" is more important than 100% perfect ports for winning. |

**Daily Risk Review**: At the end of each day, quickly review this table and update status. Escalate anything moving to "high impact" immediately.

---

## Anti-Patterns to Avoid (Learned from Previous Winners Research)

- Treating AMD as a black box ("it runs on the cloud").
- Hardcoded pipeline disguised as agents.
- Demo that only works with external services or on localhost.
- Weak README / no JUDGING.md.
- Vague metrics ("faster") instead of quantified % of theoretical peaks on real hardware.
- Over-promising scope in the narrative.

---

Use this document as the north star. When in doubt during the 5 days, ask: "Does this move us closer to the overall success definition and the phase exit criteria?"

Update the status of milestones daily in your personal notes or in `track/DAILY_LOG.md`.