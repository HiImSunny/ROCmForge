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
) -> JobState:
    """
    Clean, polished demo harness for Phase 2 repair behavior.

    - Sets up a realistic job workspace with a deliberately broken HIP file.
    - Delegates to PortingSpecialistAgent.repair_with_memory() which contains
      the actual diagnosis + memory + patching logic.
    - All steps produce proper AgentMessage objects that will render in the
      existing UI (AgentFeed + LiveJobView).
    """
    if job_id is None:
        job_id = f"mock_repair_{seed_id.lower()}"

    ws = WorkspaceManager()
    job = JobState(seed_id=SeedId(seed_id))  # type: ignore[arg-type]
    job.job_id = job_id

    ws_dir = ws.create_workspace(job)
    seeds_root = Path(__file__).resolve().parents[2] / "seeds"
    ws.copy_seed(job, seeds_root)

    # Prepare a "bad" post-hipify file that triggers a known memory pattern
    hip_out = ws_dir / "hip_out"
    hip_out.mkdir(exist_ok=True)
    (hip_out / "vectorAdd.hip.cpp").write_text(
        "// Intentionally left with classic CUDA launch syntax after hipify\n"
        "void vectorAdd(...) {\n"
        "    cudaLaunchKernel<<<grid, block>>>(vectorAdd, grid, block, 0, 0, args);\n"
        "}\n",
        encoding="utf-8"
    )

    # Seed a realistic compiler error log
    logs = ws_dir / "logs"
    logs.mkdir(exist_ok=True)
    (logs / "hipcc.log").write_text(
        "hipcc: error: unknown identifier 'cudaLaunchKernel'\n"
        "    cudaLaunchKernel<<<grid, block>>>(...);\n"
        "    ^\n"
        "1 error generated when compiling for gfx942\n",
        encoding="utf-8"
    )

    registry = create_tool_registry(job_id, ws, seeds_root)
    memory = get_memory()

    # Create the specialist that now holds the real logic
    from src.agents.base import PortingSpecialistAgent
    specialist = PortingSpecialistAgent("Porting Specialist", job, registry, memory)

    _append_message(job, "Orchestrator", "thought", f"Starting autonomous repair for seed {seed_id} on mock MI300X")

    # === Call the real logic ===
    result = specialist.repair_with_memory(max_loops=3)

    _append_message(
        job, "Orchestrator", "thought",
        f"Repair loop completed. Final status: {result.get('status')} after {result.get('attempts', '?')} attempts"
    )

    return job


if __name__ == "__main__":
    print("=" * 72)
    print("ROCmForge — Phase 2 Mock Repair Loop Demo")
    print("=" * 72)
    print("This harness runs the *real* repair logic living in PortingSpecialistAgent")
    print("using the actual ToolRegistry + Memory (no LLM yet).\n")

    job = run_mock_repair_loop()

    print("\n" + "=" * 72)
    print("AGENT TRACE (this is what will appear in the Live UI AgentFeed)")
    print("=" * 72)
    for msg in job.messages:
        prefix = "💭" if msg.type == "thought" else ("🔧" if msg.type == "action" else "👁")
        print(f"{prefix} [{msg.timestamp}] {msg.agent}: {msg.content}")

    print("\n✅ Harness complete.")
    print("   The job object now contains a full realistic repair trace.")
    print("   In production this trace will be produced by an LLM calling the same tools.")
    print("=" * 72)
