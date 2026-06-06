"""Mock Agent Harness for Phase 2 preparation.

This allows us to develop and demonstrate agent logic (especially repair loops)
using the real ToolRegistry and Memory, but with controlled/mock failures.

Run this with:
    python -m src.agents.mock_harness

It will simulate a realistic scenario:
1. Workspace is prepared (seed copied + hipify "run")
2. First hipcc fails (classic cudaLaunchKernel error - simulated)
3. Agent reads the error log + source using tools
4. Retrieves relevant pattern from memory
5. Applies a targeted patch using apply_search_replace
6. Re-compiles successfully
7. All decisions are logged as proper AgentMessage (will show in the real UI)

This is **not** real autonomous agents yet — it's a harness to build, test, and
show the exact "Thought → Action (tool call) → Observation → repair" behavior
that Phase 2 will deliver once we have real hardware + vLLM-ROCm.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.models.job import JobState, SeedId, AgentMessage
from src.workspace.manager import WorkspaceManager
from src.agents.tools import create_tool_registry
from src.memory.loader import get_memory


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def _append_message(job: JobState, agent: str, typ: str, content: str) -> None:
    msg = AgentMessage(
        id=len(job.messages) + 1,
        agent=agent,
        timestamp=_now(),
        type=typ,  # type: ignore[arg-type]
        content=content,
    )
    job.messages.append(msg)


def run_mock_repair_loop(
    seed_id: str = "vectorAdd",
    job_id: str | None = None,
    scenario: str = "kernel_launch",
) -> JobState:
    """
    Polished demo harness supporting multiple error scenarios.

    Scenarios (based on memory/porting_patterns.jsonl):
      - "kernel_launch": classic <<< >>> / cudaLaunchKernel issue
      - "memcpy": cudaMemcpy not translated
      - "atomic": atomicAdd in reduction
      - "arch": wrong -arch compile flag (simulated as hipcc error)

    The harness sets up the appropriate "bad" source + error log,
    then runs the real PortingSpecialistAgent.repair_with_memory() logic.
    """
    if job_id is None:
        job_id = f"mock_{scenario}_{seed_id.lower()}"

    ws = WorkspaceManager()
    job = JobState(seed_id=SeedId(seed_id))  # type: ignore[arg-type]
    job.job_id = job_id

    ws_dir = ws.create_workspace(job)
    seeds_root = Path(__file__).resolve().parents[2] / "seeds"
    ws.copy_seed(job, seeds_root)

    hip_out = ws_dir / "hip_out"
    hip_out.mkdir(exist_ok=True)
    logs = ws_dir / "logs"
    logs.mkdir(exist_ok=True)

    # === Scenario setup: always write the bad source to vectorAdd.hip.cpp (what the current agent patch code targets)
    # The content is chosen to match one of the patterns exactly for reliable dynamic patching.
    if scenario == "kernel_launch":
        (hip_out / "vectorAdd.hip.cpp").write_text(
            "cudaLaunchKernel<<<grid, block>>>(vectorAdd, grid, block, 0, 0, args);\n",
            encoding="utf-8")
        (logs / "hipcc.log").write_text(
            "hipcc: error: unknown identifier 'cudaLaunchKernel'\n", encoding="utf-8")

    elif scenario == "memcpy":
        (hip_out / "vectorAdd.hip.cpp").write_text(
            "cudaMemcpy(d_c, d_a, size, cudaMemcpyDeviceToHost);\n",
            encoding="utf-8")
        (logs / "hipcc.log").write_text(
            "hipcc: error: no member named 'cudaMemcpyDeviceToHost' in namespace 'hip'\n", encoding="utf-8")

    elif scenario == "atomic":
        (hip_out / "vectorAdd.hip.cpp").write_text(
            "atomicAdd(&result, val);\n",
            encoding="utf-8")
        (logs / "hipcc.log").write_text(
            "hipcc: warning: atomicAdd may have performance issues on gfx942. Use HIP version.\n", encoding="utf-8")

    elif scenario == "arch":
        (hip_out / "vectorAdd.hip.cpp").write_text("// source is fine\n", encoding="utf-8")
        (logs / "hipcc.log").write_text(
            "hipcc: error: unsupported target 'sm_80' for this ROCm version. Use --offload-arch=gfx942\n", encoding="utf-8")

    else:
        (hip_out / "vectorAdd.hip.cpp").write_text(
            "cudaLaunchKernel<<<grid, block>>>(vectorAdd, grid, block, 0, 0, args);\n",
            encoding="utf-8")
        (logs / "hipcc.log").write_text("unknown identifier 'cudaLaunchKernel'\n", encoding="utf-8")

    registry = create_tool_registry(job_id, ws, seeds_root)
    memory = get_memory()

    from src.agents.base import PortingSpecialistAgent
    specialist = PortingSpecialistAgent("Porting Specialist", job, registry, memory)

    _append_message(job, "Orchestrator", "thought", f"Starting repair for {seed_id} (scenario={scenario})")

    result = specialist.repair_with_memory(max_loops=3)

    _append_message(job, "Orchestrator", "thought",
                    f"Repair finished: {result.get('status')} after {result.get('attempts', '?')} attempts")

    return job


if __name__ == "__main__":
    print("=" * 72)
    print("ROCmForge — Phase 2 Mock Repair Loop Demo (multiple scenarios)")
    print("=" * 72)
    print("Demonstrates the *real* PortingSpecialistAgent logic + Memory + Tools\n")

    scenarios = ["kernel_launch", "memcpy", "atomic"]
    for sc in scenarios:
        print(f"\n--- Scenario: {sc} ---")
        job = run_mock_repair_loop(scenario=sc)
        # Print last few messages for this scenario
        for msg in job.messages[-6:]:
            prefix = "💭" if msg.type == "thought" else ("🔧" if msg.type == "action" else "👁")
            print(f"  {prefix} {msg.agent}: {msg.content[:80]}")

    print("\n" + "=" * 72)
    print("✅ All scenarios completed.")
    print("   Each run uses the same smart agent logic + memory patterns.")
    print("   On real MI300X + vLLM this becomes fully autonomous.")
    print("=" * 72)
