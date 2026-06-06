# ROCmForge — Submission Checklist & Evidence Tracker (AMD ACT II)

Use this living document to ensure we hit every winning pattern and hackathon requirement. Update daily with evidence (screenshots, logs, links, commit hashes).

## 1. Winning Formula Checklist (from our research)

- [ ] **1 specific pain point + shock metric + real case**
  - Narrative hook: "CUDA vendor lock-in forces weeks of manual porting. ROCmForge autonomous swarm produces working ROCm ports + real MI300X benchmarks + migration guide in minutes."
  - Evidence location: README top, video 0:00-0:30, JUDGING.md

- [ ] **Genuine agentic workflow (not hardcoded pipeline)**
  - Agents make real decisions, use tools autonomously, enter repair loops based on observations.
  - Evidence: Live agent activity feed in UI, agent trace logs, example "Thought → Action → Observation" in README + video.

- [ ] **Deep AMD / ROCm / MI300X integration (≥2 angles)**
  - Native ROCm tools (hipify, hipcc), vLLM-ROCm for brains, real amd-smi / rocprof metrics with % efficiency on actual hardware.
  - Evidence: Multiple jobs with captured amd-smi timeseries, power/thermals/util, explicit "ran on AMD Instinct MI300X via ROCm using hackathon credits".

- [ ] **Production-ready signals**
  - Docker, health endpoints, job isolation, demo/seed + replay, structured logs, artifacts.
  - Evidence: `docker compose up` works, health returns GPU status, replay endpoint stable.

- [ ] **1 clear WOW moment in demo**
  - Live agents deciding + metrics spiking in real time on MI300X, or impressive before/after efficiency numbers.
  - Evidence: Video timestamp, UI screenshots, report with quantified gains.

- [ ] **Demo mode (no external services required for judges)**
  - Strong seed + replay paths that work quickly and stably.
  - Evidence: JUDGING.md 90-second path, offline Gradio replay mode.

- [ ] **README xuất sắc + architecture diagram**
  - Narrative hook, Mermaid diagram (with AMD callouts), stack table, demo flow, real evidence section, honest limitations + ✅/🔶/🔲 matrix.
  - Evidence: README.md at root of GitHub.

- [ ] **JUDGING.md with copy-paste verification**
  - Elevator pitch, exact 90s commands + expected outputs, code map, AMD-specific checks.
  - Evidence: JUDGING.md in repo root.

- [ ] **Learning / memory mechanism**
  - Patterns distilled post-job and reused.
  - Evidence: memory/porting_patterns.jsonl + example in report.

- [ ] **Strong business / real-world value**
  - Directly solves a painful, expensive problem for anyone wanting to adopt AMD GPUs.
  - Evidence: Narrative + "time/cost savings" framing in video + report.

## 2. Hackathon Submission Requirements

- [ ] Project Title + Short + Long Description (clear, keyword-rich for AMD/ROCm/MI300X/agents)
- [ ] Cover Image (professional, shows UI + AMD metrics or swarm in action)
- [ ] Video Presentation (2-4 min, audio, early WOW, real hardware evidence)
- [ ] Slide Presentation (supporting, not primary)
- [ ] Public GitHub Repository (clean, MIT license, all plan/spec/track preserved as proof of process)
- [ ] Demo Application URL (live on AMD cloud MI300X instance, or very strong replay + evidence)
- [ ] Technology & Category Tags (AMD, ROCm, MI300X, Multi-Agent, CUDA Migration, Performance Optimization, etc.)

## 3. AMD-Specific Evidence (Critical for this hackathon)

- [ ] Real MI300X execution shown (not just "works on cloud")
  - amd-smi / rocm-smi output with gfx942 / MI300X identification
  - Multiple jobs with live metrics during benchmark

- [ ] Quantified performance on the hardware
  - % of theoretical peaks (memory BW 5.3 TB/s, compute TFLOPS)
  - Power, temperature, utilization numbers
  - Before/after if optimizer is used

- [ ] Native ROCm toolchain usage visible
  - hipify (clang or perl) + hipcc commands and logs
  - vLLM-ROCm for agent brains (if used for reasoning)

- [ ] Profiling / observability artifacts
  - Timeseries JSON or screenshots
  - Any rocprof output

## 4. Daily / Phase Tracking (Update as we go)

**Day 0 (Prep / Hardware Verification)**
- [ ] AMD AI Developer Program + credits claimed
- [ ] MI300X instance launched and verified (vLLM image or ROCm base)
- [ ] `amd-smi`, hipify, hipcc, basic torch/ROCm working
- [ ] One manual seed port + full metrics captured
- Evidence file: `track/DAY0_HARDWARE_VERIFICATION.md`

**Phase 1 (Baseline Pipeline)**
- [x] FastAPI job system + workspace isolation working (src/main.py + workspace/manager.py + models)
- [x] End-to-end baseline on seed (hipify → compile → run → metrics → report + tar) — implemented in src/baseline/pipeline.py (MOCK + real path)
- [x] Health endpoint + SSE stub + demo/seed + replay endpoints
- [ ] All on real MI300X  ← pending Day 0 hardware claim + first run
- Evidence: seeds/ created (vectorAdd, tiledMatmul, reduction), full scaffold in src/, requirements.txt, scripts/day0_verify.py, track/DAILY_LOG updated 2026 session start

**Phase 1 — Seeds (critical foundation)**
- [x] 3 self-contained seeds written with host timing, self-checks, and hipify-friendly structure
- [x] Match exact frontend IDs (vectorAdd, tiledMatmul, reduction)

**Phase 2 (Agentic Swarm) — Preparation in progress**
- [x] Light preparation artifacts created (memory patterns, state machine, role docs)
- [x] Strong Phase 2 prep: detailed plan, polished ToolRegistry + Memory (easy to use, prompt-ready), working mock repair loop harness that demonstrates real "Thought → tool call → Observation → patch → success" behavior using the actual tools.
- [ ] Agents making visible autonomous decisions (implementation after real hardware)
- [ ] At least one successful repair loop on a seed
- [ ] Streaming logs / activity feed in UI (will reuse/extend existing SSE)
- [ ] Memory pattern storage started (jsonl exists, loader in progress)

**Phase 3 (AMD Depth + Optimization)**
- [ ] Live amd-smi sampling + % efficiency calculations
- [ ] Scoped optimizer showing measurable gain on at least one seed
- [ ] Impressive numbers in reports (e.g. >80% of theoretical BW)

**Phase 4 (Production + Demo Polish)**
- [x] Docker + compose works cleanly (docker-compose.yml created with device passthrough, healthcheck, jobs volume, MOCK vs real env notes, future vLLM skeleton)
- [x] JUDGING.md complete with copy-paste commands (90s paths for mock + real MI300X, claims table, elevator, reproducibility, links to evidence)
- [x] Demo/seed + replay endpoints improved (replay now supports ?job_id= to load real previous job reports + diagnostics)
- [x] UI polish: error surfacing (red banners + failed badges), loading/estimated time hints, recent jobs with status, progress indicators (PhaseTimeline + pulsing estimates), ReportViewer failure detection, CSS for failed phases
- [x] JUDGING.md heavily updated with failure inspection path, new replay job_id support, UI polish references, and dedicated partial-success section for judges
- [ ] Full UI (live feed, metrics, report viewer, downloads) — core is excellent; minor remaining polish possible after hardware data

**Phase 5 (Narrative + Submission Assets)**
- [ ] README final (hook, diagram, evidence, limitations)
- [ ] Video recorded (early WOW + real hardware + narrative)
- [ ] GitHub public + clean
- [ ] All track/ evidence populated
- [ ] Submission form filled with links, descriptions, tags

## 5. Risk & Anti-Pattern Watchlist

- [ ] No "it works locally but not on AMD Cloud" surprises → Test on real instance early and often.
- [ ] No hidden external dependencies for core demo → Demo mode + seeds are self-contained.
- [ ] No vague "we used AMD" claims → Every metric, log, and command explicitly shows ROCm + MI300X.
- [ ] No over-scope on complex CUDA → Stick to seeds + clear "partial + excellent guide" path.
- [ ] README / JUDGING.md not an afterthought → Write and test them in parallel with code.

## 6. Final Submission Day Checklist (July 11)

- [ ] All 4 judging criteria clearly addressed (Application of Technology = deep real AMD, Presentation = README+video+JUDGING, Business Value = pain + metric, Originality = autonomous ROCm swarm).
- [ ] Live demo stable on AMD cloud.
- [ ] Video uploaded and linked.
- [ ] GitHub repo public with clear README pointing to demo + JUDGING.md.
- [ ] Cover image + slides uploaded.
- [ ] Descriptions and tags optimized.
- [ ] Internal cross-check against this checklist complete.

---

**This document is the single source of truth for "are we on track to win?"**  
Update it every evening with concrete evidence (links to screenshots in repo, commit hashes, job IDs, metric numbers).

When this checklist is green and backed by real artifacts from MI300X, ROCmForge will be extremely hard to beat on the AMD-specific criteria.