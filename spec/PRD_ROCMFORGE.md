# ROCmForge — Product Requirements Document (PRD)

**Project Name**: ROCmForge  
**Tagline**: Autonomous AI Agent Swarm that ports CUDA to ROCm and optimizes it on real AMD Instinct MI300X GPUs — in minutes.  
**Hackathon**: AMD Developer Hackathon: ACT II (lablab.ai)  
**Theme Alignment**: AI Agents + High-Performance AI Apps on AMD GPUs (ROCm, MI300X, bare-metal cloud performance).

## Problem Statement
CUDA vendor lock-in forces developers and companies to spend weeks or months manually porting code to AMD ROCm/HIP. This creates:
- High switching costs and delayed AMD adoption.
- Risk of bugs, performance regressions, and incomplete ports.
- Talent bottleneck (few engineers deeply understand both CUDA and ROCm).

**Shock Metric**: A typical CUDA kernel port + validation + basic optimization can take 1-5 days of expert time. ROCmForge aims to reduce the initial autonomous pass to minutes on real MI300X hardware, with full artifacts and a clear migration guide.

Target users: CUDA developers, ML engineers, companies evaluating or migrating to AMD GPUs (enterprise, research, startups).

## Solution Overview
ROCmForge is a production-ready, genuinely agentic multi-agent system that:
1. Accepts CUDA source (pre-loaded seeds or limited GitHub upload).
2. Runs an autonomous swarm of specialist agents on AMD Developer Cloud (MI300X via ROCm).
3. Uses native ROCm tools (hipify, hipcc) + LLM reasoning for porting, repair loops, validation, benchmarking, and scoped optimization.
4. Captures real hardware metrics (utilization, power, temperature, achieved vs theoretical peak performance).
5. Outputs: ported HIP sources, compilation logs, benchmark reports, performance analysis (% efficiency), and a human-readable migration guide.
6. Provides live visibility into agent decisions and metrics.

The entire swarm (agent reasoning via vLLM-ROCm + heavy benchmark workloads) runs natively on the same MI300X instance, showcasing the 192 GB VRAM advantage for large-context agents + compute-intensive validation.

## Core User Flow (90-Second Judge Verification Path)
1. User selects a seed (e.g., vectorAdd, tiled matmul) or provides simple CUDA snippet.
2. Submits job → UI shows live agent activity feed + real-time GPU metrics.
3. Swarm autonomously: analyzes → hipify + repair loop → compiles → validates correctness → benchmarks with amd-smi capture → scoped optimize → generates report.
4. User downloads: full migration_report.md, ported sources tar, JSON metrics, agent trace log.
5. Judges can replay via demo endpoint or view pre-captured evidence.

## Success Metrics (for this hackathon)
- **Autonomy**: ≥80% success rate on seed examples with zero manual intervention after submit (agents handle repair loops).
- **AMD Depth**: Real MI300X execution with visible metrics (utilization >70% during kernels, power/thermals, % of theoretical 5.3 TB/s BW or TFLOPS peaks). Multiple jobs with captured amd-smi / rocprof data.
- **Judge Experience**: Full verification possible in <90 seconds via live UI or JUDGING.md copy-paste commands. Clear WOW moment (live agent decisions + metrics spiking on real hardware).
- **Production Quality**: Docker works, health endpoints, demo/seed + replay modes, clean artifacts, deployment guide for AMD Cloud.
- **Narrative Strength**: One memorable hook + quantified before/after on actual AMD hardware.
- **Originality**: Autonomous swarm purpose-built for the exact pain AMD wants solved (CUDA → ROCm migration at scale).

## Non-Goals (Ruthless 5-Day Scope)
- Full arbitrary large CUDA projects / complex 3rd-party libs (cuDNN, Thrust, textures, dynamic parallelism) — focus on self-contained kernels + limited .cu/.cuh.
- Perfect numerical equivalence on all cases (flag issues + provide guidance).
- Production deployment of the ported code (focus on the porting/optimization process + report as the deliverable).
- UI polish beyond functional Gradio/FastAPI (live feed, metrics cards, report viewer, downloads).

## Key Features & Requirements

### Agentic Swarm (Genuine, Visible Autonomy)
- Multi-agent architecture with clear roles (Orchestrator, Analyzer, HIP Porting Specialist, Validator, Benchmark+Profiler, Optimizer, Reporter).
- Real tool calling (not hardcoded pipelines): agents decide when to call hipify, hipcc, read files, apply patches, capture metrics, etc.
- Repair loops with memory (successful patterns stored and reused).
- Shared blackboard state + visible "thoughts" / decisions in logs and UI.
- Learning loop: post-job pattern distillation.

### Deep AMD / ROCm Integration (Core Differentiator)
- All heavy work (agent LLM serving via vLLM-ROCm + HIP compilation + benchmarking) runs natively on MI300X.
- Native tool usage: hipify-clang / hipify-perl, hipcc, amd-smi / rocm-smi (live sampling), optional rocprof.
- Real metrics captured and presented: GPU utilization, memory bandwidth achieved vs 5.3 TB/s, compute TFLOPS vs peaks, power, temperature, clocks.
- Showcase MI300X strengths: large context for agents (192 GB allows better models with less quantization), parallel benchmark workloads.
- Explicit ROCm version, arch (gfx942), and % efficiency calculations in reports.

### Production-Ready & Judge-Friendly
- Docker + docker-compose (devices for /dev/kfd /dev/dri, proper groups).
- Health / ready endpoints (GPU + vLLM status).
- Job isolation, sandboxing, timeouts, cleanup.
- **Demo mode**: seed + replay endpoints (fast, stable, minimal GPU for demo/judges).
- Structured logging + full artifact tar + polished MD report.
- JUDGING.md with copy-paste verification commands and expected outputs.

### UI / Observability
- Live job view: agent activity feed (streaming), file diffs, metric cards + sparklines (util, power, temp), progress.
- Report viewer + downloads.
- (Gradio recommended for 5-day velocity; can be pure FastAPI + minimal frontend if preferred.)

### Output Artifacts (What "wins" the migration)
- migration_report.md (step-by-step swarm journey, before/after snippets, metrics tables with %eff + hardware context, "how to extend to your codebase", honest limitations).
- Ported sources + build script.
- JSON metrics + timeseries.
- Agent trace log (for replay / audit).
- Tar of everything.

## Technical Constraints & Assumptions (5-Day Reality)
- One MI300X instance via AMD Developer Cloud ($100 credits).
- vLLM-ROCm for agent brains (choose a strong coding model that fits comfortably, e.g., Qwen2.5-Coder 32B class or equivalent available in 2026).
- Seeds: 2-3 self-contained examples (vectorAdd for memory BW, tiled matmul for compute, simple reduction). Provide CPU reference for validation.
- Framework: LangGraph (preferred for stateful agent graphs) or lightweight custom ReAct + tools. Python/FastAPI backend.
- UI: Gradio (fastest for live components) or Streamlit.
- Scope limit: Focus on kernels + basic host code that hipify + hipcc can handle with LLM-assisted repair. No promise of full complex codebases.

## Risks & Mitigations
- Hipify is imperfect → Agents treat it as first pass; explicit repair loop with rich error context and memory is core.
- Resource contention (vLLM + heavy HIP workloads) → Efficient model choice, monitor with amd-smi, use the 192 GB advantage.
- Demo stability on judges' side → Strong replay mode + pre-captured real evidence + offline Gradio replay of traces + metrics.
- Time for full autonomy → Build working baseline pipeline Day 1, layer agents Day 2. Visible logs make partial autonomy impressive.

## Narrative Hook (Use Everywhere)
"CUDA vendor lock-in is real. ROCmForge is an autonomous agent swarm that ports, validates, benchmarks, and optimizes your CUDA code on real AMD Instinct MI300X GPUs — producing production-ready artifacts and a clear migration guide in minutes, not weeks."

## Out of Scope for This Hackathon (Future Ideas)
- Web UI with GitHub integration + larger codebases.
- Fine-tuning a domain-specific porting model.
- Full CI/CD integration or enterprise dashboard.
- Support for the entire CUDA ecosystem.

---

**This PRD is the single source of truth for what "perfect" looks like for ROCmForge in AMD ACT II.** All implementation, docs, and demos must map back to these requirements and the winning patterns from our research (genuine agentic, deep visible AMD metrics, production signals, strong narrative + JUDGING.md, WOW real-time/performance moment).

Next: See plan/ for execution phases and spec/ for detailed agent roles, metrics schema, etc.