# agents/ — Light Phase 2 Preparation (Documentation Only)

This folder contains **preparation artifacts** created while Phase 1 was being hardened and while waiting for real MI300X hardware verification.

## Contents
- `orchestrator.md` — High-level responsibilities and tools for the main planner.
- `porting_specialist.md` — The star agent that will perform visible autonomous hipify + repair loops.

These are intentionally lightweight (markdown role descriptions) so that when we move to implementation we have clear contracts.

## Related Artifacts
- `memory/porting_patterns.jsonl` — The learning memory the agents will query.
- `plan/PHASE2_AGENT_STATE_MACHINE.md` — Mermaid diagram + transition rules.
- `spec/AGENT_ROLES_AND_PROMPTS.md` — Full detailed prompts and tool definitions (source of truth for prompts).

Do not implement actual agent code here until:
1. Real hardware Day 0 is complete and tracked.
2. Baseline pipeline is proven stable on MI300X with real numbers.
3. Decision is made on framework (LangGraph vs custom).

Current date of preparation: during Phase 1 production readiness polish.
