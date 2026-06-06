# ROCmForge Phase 2 — Implementation Plan (Preparation)

**Date started**: After Phase 1 software completion (commit 1a68fd7)  
**Status**: Preparation / Design. Full coding of autonomous agents should wait for real MI300X verification.

## Goals for Phase 2
- Wrap the existing solid Phase 1 baseline pipeline with genuine multi-agent intelligence.
- Agents make visible, autonomous decisions using real tool calling.
- At least one successful repair loop on a seed (hipcc error → read source + logs → targeted patch → recompile success).
- All heavy execution (including future vLLM-ROCm for agent brains) still happens on real MI300X.
- Reuse and extend existing UI (AgentFeed, SSE, messages) so the "swarm journey" becomes much richer.

## High-Level Architecture

The Phase 1 baseline already produces excellent structure:
- JobState as blackboard
- Structured AgentMessage logs
- Workspace isolation
- Tool wrappers in `src/tools/rocm.py`
- Pipeline steps that map naturally to agent phases

Phase 2 turns the **baseline into a set of tools** that agents can call, and adds an intelligent layer on top.

### Recommended Stack (to be confirmed on hardware)
- **Orchestration**: LangGraph (preferred for stateful graphs, conditional routing, and repair loops) or a lightweight custom ReAct loop if we want to stay very light on deps.
- **LLM Brain**: vLLM-ROCm (Qwen2.5-Coder or similar) running on the same MI300X instance.
- **Memory**: `memory/porting_patterns.jsonl` (already started) + simple retrieval injected into prompts.
- **Tools**: Thin, well-documented wrappers around existing functionality.

## Key Work Packages (in recommended order)

### 1. Tool Surface (Foundation)
- Create `src/agents/tools.py` or `src/agents/tool_registry.py`
- Expose the existing capabilities as first-class tools with:
  - name
  - description (for LLM)
  - input schema (pydantic or json schema)
  - implementation that calls the current rocm.py + pipeline functions
- Tools to expose initially:
  - run_hipify
  - run_hipcc
  - read_file (sandboxed to job workspace)
  - apply_patch (safe search/replace or unified diff)
  - capture_amd_smi
  - run_benchmark (the compiled binary + metrics)
  - get_job_state / update_job_state (for blackboard)
  - search_memory (query porting_patterns)

The baseline pipeline.py can be refactored so each major step is callable as a tool or sub-graph.

### 2. Memory System
- Build `src/memory/loader.py`:
  - Load all patterns from `memory/porting_patterns.jsonl`
  - Simple retrieval: keyword match + confidence filter + top-k
  - Future: embedding-based if we add a small model
- Function: `get_relevant_patterns(task_description: str, top_k=3) -> list[dict]`
- Patterns are prepended to the relevant agent's system prompt.

### 3. Agent Base + Roles (Skeletons first)
- `src/agents/base_agent.py`: Abstract base with common behavior (log_message, call_tool, update_state, think).
- Implement (or stub) the roles from `spec/AGENT_ROLES_AND_PROMPTS.md`:
  - Orchestrator
  - Porting Specialist (the most important for repair loops)
  - Analyzer, Validator, Profiler, Reporter (as needed)

Start with stubs that have clear method signatures and docstrings.

### 4. State Machine / Graph
- Use the Mermaid in `plan/PHASE2_AGENT_STATE_MACHINE.md` as the spec.
- In LangGraph: nodes = agents or phases, edges = conditional on success/failure/repair count.
- Key special handling:
  - Repair loop with max_loops counter (stored in JobState)
  - Explicit "Partial Success" exit that still produces excellent report + guide

### 5. Integration with existing system
- The main FastAPI job runner (`src/main.py`) should still work.
- When Phase 2 is active, instead of calling `run_baseline` directly, we call `agents.orchestrator.run_job(job, ws, seeds_root)`.
- All agent thoughts/actions/observations must still produce `AgentMessage` objects so the existing UI (AgentFeed, SSE) works with zero or minimal changes.
- The pipeline's rich messages can become the "baseline agent" trace.

### 6. Prompt Engineering & Observability
- Move / improve the starter prompts from `spec/AGENT_ROLES_AND_PROMPTS.md` into the code (or load from files).
- Every tool call and decision must be logged with timestamps and agent id.
- Make sure failed repair loops still produce high-quality reports (we already have good support for this from Phase 1 hardening).

### 7. Testing Strategy (while waiting for hardware)
- Unit test the memory loader and tool registry in isolation.
- Create "mock agent harness" that can run the graph with fake tool responses (so we can test repair logic without ROCm).
- Once we have real hardware, do end-to-end tests with real hipify/hipcc failures on the seeds.

## Risks & Mitigations
- vLLM + heavy benchmark on same MI300X → Use efficient model, good gpu-memory-utilization, run benchmarks after agent planning or with lower priority.
- Agent hallucinating bad patches → Strong few-shot from memory + limited repair budget (5 loops) + always keep human-visible logs + diagnostic report path.
- Scope creep → Ruthlessly limit to the 3 seeds during the hackathon.

## Success Criteria for Phase 2 (when we execute)
- Submit a seed via UI or /jobs.
- Observe in the live AgentFeed clear autonomous decisions and at least one repair loop (e.g. "hipcc failed on unknown identifier → reading hip_out + error log → applying patch for hipLaunchKernel → recompile succeeded").
- Final report + artifacts still generated.
- All numbers from real MI300X.

## Current Preparation Artifacts (already created)
- `memory/porting_patterns.jsonl`
- `plan/PHASE2_AGENT_STATE_MACHINE.md` (Mermaid + transitions)
- `agents/*.md` (role summaries)
- This document

## Next Immediate Preparation Steps (this session / next)
1. Implement memory loader utility.
2. Create ToolRegistry with the core tools + schemas.
3. Create `src/agents/` Python skeleton (base + orchestrator + porting_specialist stubs).
4. Write a small "agent harness" script that can simulate a run using the tools (for testing the graph logic on this machine).
5. Update `spec/AGENT_ROLES_AND_PROMPTS.md` with concrete tool names and signatures once the registry is defined.

## When to Move to Full Implementation
Only after:
- Real MI300X instance is up and verified (`scripts/day0_verify.py` + at least one successful `ROCFORGE_MOCK=0` baseline).
- `track/DAY0_HARDWARE_VERIFICATION.md` is filled with real evidence.
- We have confirmed the ROCm environment (hipify-clang, hipcc targeting gfx942, amd-smi, vLLM-ROCm) works well for agent brains + workloads.

This plan keeps us disciplined while making Phase 2 implementation much faster and higher quality when the time comes.

---
Update this document as we complete each preparation step.
