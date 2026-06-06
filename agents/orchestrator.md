# Agent: Orchestrator / Planner (Phase 2 Skeleton)

**Goal**: Own the end-to-end plan and decide when to repair vs. produce partial success.

**Key Decisions**:
- Dispatch Analyzer → Porting Specialist
- Monitor repair loops (max 5)
- On repeated failure: route to "partial + excellent migration guide"
- Final sign-off and handoff to Reporter

**State it reads/writes**:
- Full JobState (blackboard)
- Current phase
- `repair_loops` counter
- `memory_refs`

**Tools it primarily uses**:
- `read/write_job_state`
- `trigger_phase`
- `replan_if_needed`
- `finalize_and_report`

**When implemented**: This becomes the LangGraph entry node or main ReAct loop controller.
