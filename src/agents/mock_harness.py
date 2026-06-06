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
    Runs a complete simulated repair loop using the actual ToolRegistry + Memory.
    The failure is injected for demo purposes, but all tool calls and memory
    retrieval are real.
    """
    if job_id is None:
        job_id = f"mock_repair_{seed_id.lower()}"

    ws = WorkspaceManager()
    job = JobState(seed_id=SeedId(seed_id))  # type: ignore[arg-type]
    job.job_id = job_id

    # Ensure workspace exists and has the seed
    ws_dir = ws.create_workspace(job)
    seeds_root = Path(__file__).resolve().parents[2] / "seeds"
    ws.copy_seed(job, seeds_root)

    # Create a fake hip_out with a "bad" translated file for the demo
    hip_out = ws_dir / "hip_out"
    hip_out.mkdir(exist_ok=True)
    bad_source = hip_out / "vectorAdd.hip.cpp"
    bad_source.write_text(
        "// Simulated output from hipify\n"
        "void vectorAdd(...) {\n"
        "    cudaLaunchKernel<<<grid, block>>>(vectorAdd, grid, block, 0, 0, args);\n"
        "}\n",
        encoding="utf-8"
    )

    # Also create a logs dir with a fake hipcc error
    logs_dir = ws_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    (logs_dir / "hipcc.log").write_text(
        "hipcc: error: unknown identifier 'cudaLaunchKernel'\n"
        "    cudaLaunchKernel<<<grid, block>>>(...)\n"
        "    ^\n"
        "1 error generated when compiling for gfx942\n",
        encoding="utf-8"
    )

    registry = create_tool_registry(job_id, ws, seeds_root)
    memory = get_memory()

    agent_name = "Porting Specialist (Mock)"

    _append_message(job, "Orchestrator", "thought", f"Delegating to Porting Specialist for repair loop on {seed_id}")

    # === Real agent-like flow ===

    _append_message(job, agent_name, "action", "Running hipify-clang...")
    hipify_res = registry.execute("run_hipify")
    _append_message(job, agent_name, "observation", f"hipify completed (mock). hip_out populated.")

    _append_message(job, agent_name, "action", "First hipcc compile attempt (O3 + gfx942)...")
    # We deliberately call with the "bad" source list to trigger our simulated failure path
    compile1 = registry.execute("run_hipcc", sources=["vectorAdd.hip.cpp"])

    # Inject a realistic failure for the demo (the real tool would have succeeded in pure MOCK)
    compile1 = {
        "success": False,
        "error": "error: unknown identifier 'cudaLaunchKernel'\n    cudaLaunchKernel<<<grid, block>>>(...);",
        "log": "hipcc failed with kernel launch syntax error",
    }
    _append_message(job, agent_name, "observation", f"hipcc FAILED on first attempt. Error: {compile1['error'][:80]}...")

    # Agent reads the evidence
    _append_message(job, agent_name, "action", "Reading hipcc.log and the generated HIP source to understand the failure...")
    error_log = registry.execute("read_file", relative_path="logs/hipcc.log")
    source = registry.execute("read_file", relative_path="hip_out/vectorAdd.hip.cpp")

    _append_message(job, agent_name, "thought", "Classic CUDA launch syntax not fully translated by hipify. This matches a known pattern in memory.")

    # Retrieve from memory (real call)
    patterns = memory.get_relevant_patterns("hipcc failed with unknown identifier cudaLaunchKernel")
    mem_context = memory.format_for_prompt(patterns)
    _append_message(job, agent_name, "observation", f"Memory returned {len(patterns)} relevant pattern(s).")

    # Apply the fix using the real apply_search_replace tool
    _append_message(job, agent_name, "action", "Applying targeted search-replace based on memory pattern...")
    patch_res = registry.execute(
        "apply_search_replace",
        relative_path="hip_out/vectorAdd.hip.cpp",
        old_text="cudaLaunchKernel<<<grid, block>>>(vectorAdd, grid, block, 0, 0, args);",
        new_text="hipLaunchKernel(grid, block, 0, 0, vectorAdd, args);  // repaired using stored porting pattern",
    )

    if patch_res.get("success"):
        _append_message(job, agent_name, "observation", "Patch applied successfully.")
    else:
        _append_message(job, agent_name, "observation", f"Patch result: {patch_res}")

    # Retry compile
    _append_message(job, agent_name, "action", "Re-attempting hipcc after the repair...")
    compile2 = registry.execute("run_hipcc", sources=["vectorAdd.hip.cpp"])

    if compile2.get("success"):
        _append_message(job, agent_name, "observation", "hipcc succeeded on second attempt. Binary is ready.")
        _append_message(job, "Orchestrator", "thought", "Repair loop completed successfully. Proceeding to validation.")
    else:
        _append_message(job, agent_name, "observation", f"Second compile still had issues: {compile2.get('error')}")

    # Final benchmark (uses the real tool)
    _append_message(job, "Benchmark & Profiler", "action", "Running the repaired binary + capturing metrics...")
    bench = registry.execute("run_benchmark")
    _append_message(job, "Benchmark & Profiler", "observation", f"Benchmark finished. wall_time={bench.get('wall_time_seconds')}s")

    _append_message(job, agent_name, "thought", "Mock repair demonstration complete. In production this entire loop would be driven by an LLM calling the same tools.")

    return job


if __name__ == "__main__":
    print("=" * 72)
    print("ROCmForge — Mock Phase 2 Repair Loop (using real ToolRegistry + Memory)")
    print("=" * 72)
    print("This demonstrates exactly how a Porting Specialist agent will behave.\n")

    job = run_mock_repair_loop()

    print("\n--- Last agent decisions (this is what the UI AgentFeed will show) ---")
    for msg in job.messages[-10:]:
        print(f"[{msg.timestamp}] {msg.agent}: {msg.content[:95]}")

    print("\n✅ Demonstration finished. The repair loop used actual tool calls and memory retrieval.")
    print("   When we have real hardware + vLLM, we will replace the decision logic with LLM calls.")
    print("=" * 72)
