# ROCmForge — Full Context for New Session (Copy-Paste Ready)

## Project Identity
**Name**: ROCmForge  
**One-liner**: Autonomous multi-agent swarm that ports CUDA → ROCm/HIP, validates correctness, runs deep performance benchmarks, and applies scoped optimizations — all executing natively on real AMD Instinct MI300X GPUs via the AMD Developer Cloud. Produces production-ready artifacts + polished migration reports with real hardware metrics.

**Hackathon**: AMD Developer Hackathon: ACT II (lablab.ai)  
**Dates**: 6–11 July 2026 (5 days). Submission closes 11 July 15:00 UTC.  
**Core Theme Alignment**: AI Agents + High-Performance AI apps on AMD GPUs (MI300X + ROCm). Explicitly encourages porting CUDA workloads and performance-focused development on real hardware (no local setup).

**Winning Formula** (from our research + ACT I winners):
- Genuine agentic behavior (real tool calling, autonomous decisions, repair loops, memory/pattern learning — NOT hardcoded pipelines).
- Deep, visible AMD integration (hipify + hipcc + amd-smi/rocprof metrics, vLLM-ROCm for agent brains, % of theoretical peaks, power/thermals/utilization on actual MI300X).
- Production-ready + judge-friendly (Docker, health checks, demo/seed + replay modes, excellent README + JUDGING.md with copy-paste verification <90s).
- Strong narrative + WOW moment (live agents thinking + real-time GPU metrics spiking on real hardware).
- Business value: Solves real CUDA vendor lock-in pain.

**Scope Guardrails (5-day reality)**:
- Only 2-3 self-contained seeds (vectorAdd for memory BW, tiled matmul for compute + shared memory, parallel reduction for control flow/atomics).
- Full autonomy on seeds + graceful "partial success + high-quality migration guide" for harder cases.
- Everything that matters runs on real MI300X (vLLM for agents + HIP execution + profiling). No simulation for core path.
- Do NOT expand to arbitrary large repos or complex 3rd-party libs during the event.

## Current Status (as of last update)

**Preparation Layer** — Extremely strong and complete:
- plan/ (5DAY_BLUEPRINT_AND_PHASES.md, ARCHITECTURE.md, MILESTONES_AND_RISKS.md)
- spec/ (PRD_ROCMFORGE.md, AGENT_ROLES_AND_PROMPTS.md, METRICS_AND_REPORT_SCHEMA.md, UI_DESIGN.md, UI_FLOWS_AND_DEMO_SEEDS.md, DEPLOYMENT_AND_CLOUD.md)
- track/ (SUBMISSION_CHECKLIST.md, DAY0_HARDWARE_VERIFICATION.md, DAILY_LOG.md)
- research/ (ROCm_hipify_vLLM_amd-smi_notes.md)
- Root guidance: AGENTS.md, CLAUDE.md, README_ROCMFORGE.md, WINNING_STRATEGIES_AMD_ACT_II.md, HACKATHON_INFO.md
- All winning patterns, scope rules, and AMD-specific requirements are documented.

**Frontend (UI)** — Mostly done and at high polished level (custom Next.js, not Gradio):
- Full scaffold: Next.js 15 + TS + Tailwind + shadcn + Framer Motion + Recharts.
- Beautiful dark tech "mission control" design explicitly following `impeccable` + `make-interfaces-feel-better` + `frontend-patterns` (concentric radius, layered shadows, explicit transitions only, tabular-nums, optical alignment, good hit areas, motion with purpose, no "transition: all", no AI slop).
- Key screens/components implemented:
  - Landing with premium hero + 3 seed cards.
  - LiveJobView (agent feed + metrics dashboard + phase timeline).
  - AgentFeed (polished, hierarchical, live simulation).
  - MetricsDashboard (real-time sparklines, big % of peak numbers, live pulse).
  - PhaseTimeline, ReportViewer, SeedCard.
- Design emphasizes the two things that win this hackathon: visible genuine agentic behavior + real high-performance MI300X metrics.
- Still needs: Real SSE/WebSocket integration with backend, full demo/replay mode wiring, minor polish iterations.

**Backend / Core Logic** — Still mostly in spec (biggest remaining work):
- No actual Python/FastAPI code yet in src/.
- Needs: Job management + workspace isolation, native ROCm tool wrappers (hipify, hipcc), agent swarm (LangGraph or custom ReAct with tool calling), vLLM-ROCm integration for agent brains, live metrics capture (amd-smi), validation against CPU refs, scoped optimizer, report generation, SSE streaming, demo/seed + replay endpoints, Docker setup.
- Seeds (actual self-contained CUDA examples + CPU refs) not yet written.
- The "1 ngày UI" ambition was delivered at high quality. The real heavy lifting (making the swarm actually run on MI300X and produce believable metrics) is still ahead.

**Overall**:
- Preparation + UI shell: Very strong (we can open new sessions and continue without losing direction).
- End-to-end working system (especially backend + real hardware integration): Not finished.
- The project is in excellent shape to execute the 5-day blueprint, but the "code" part is only ~40-50% complete (frontend UI heavy, backend light).

## Must-Follow Rules (from AGENTS.md + CLAUDE.md — read these first in every new session)

1. **Structure is sacred**. Always read relevant files from `plan/`, `spec/`, `track/`, `research/` before doing work. Update `track/DAILY_LOG.md` + evidence after any significant progress. Never scatter notes.
2. **Evidence-driven on real hardware**. Every claim about performance must be backed by captured amd-smi data from actual MI300X runs.
3. **Genuine agentic only**. Agents must use real tool calling and make visible autonomous decisions. No hardcoded sequences.
4. **Scope ruthlessly**. Stick to the 3 seeds during the event.
5. **Polish rules** (impeccable + make-interfaces-feel-better): Concentric radius, layered shadows + borders for depth, explicit transition properties, optical alignment for icons, tabular-nums for all numbers, good hit areas (44px+), motion that serves the story (agent decisions + live metrics), no flat/generic AI slop.
6. **Winning narrative**: The UI and report must make the "real MI300X + autonomous swarm solving CUDA lock-in" story land hard for judges.

**How to start any new session**:
1. Read AGENTS.md + CLAUDE.md + latest track/DAILY_LOG.md.
2. Read the relevant plan/spec file for the area you're touching.
3. Update track/ at the end of meaningful work.

## Immediate Next Priorities (from 5DAY_BLUEPRINT)

**Day 0 (do this first in real hardware)**:
- Claim AMD credits → launch MI300X instance.
- Complete full verification (fill track/DAY0_HARDWARE_VERIFICATION.md).
- Run at least one manual seed port + benchmark + capture real metrics.

**Phase 1 (Foundation — baseline pipeline, non-agent first)**:
- FastAPI job system + workspace isolation.
- End-to-end automated flow on seeds: hipify → hipcc → run + validation → metrics capture (amd-smi) → basic report + tar.
- Health endpoint + SSE streaming stub.
- Docker + basic deployment on the cloud instance.
- (Frontend can already consume the future SSE.)

**Phase 2+ (later)**:
- Layer genuine agents on top of the working baseline.
- Add live metrics sampling + optimizer.
- Full production polish (demo/replay, JUDGING.md, final README/video assets).

## Current Code State Summary

- **frontend/**: Ready-to-run Next.js app with beautiful, principle-driven UI. Landing + full live experience (agent feed + metrics + timeline). Uses mock data for now but wired for real SSE.
- **spec/ + plan/ + track/**: Authoritative source of truth. Do not contradict them.
- **src/ (Python)**: Empty / not started yet. This is where the real ROCmForge backend lives.
- No actual agent swarm, no ROCm tool integration, no real metrics pipeline yet.

The UI is the part that can make the project stand out visually and conceptually for judges. The backend is what actually proves it runs on real AMD hardware.

---

**You can copy everything above this line into a brand new session.**

When you paste this, the first thing the AI should do is:
"Read AGENTS.md, CLAUDE.md, and the latest files in track/. We are continuing ROCmForge implementation. Current status is in CONTEXT_FOR_NEW_SESSION.md."

Tell me what you want to tackle in the new session (e.g. "start Phase 1 backend baseline", "finish frontend SSE integration + demo mode", "write the actual CUDA seeds", "Day 0 verification script", etc.). I'm ready.