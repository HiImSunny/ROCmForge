"""Base classes for ROCmForge agents (Phase 2 preparation)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from src.models.job import AgentMessage, JobState
from src.agents.tools import ToolRegistry
from src.memory.loader import PortingMemory


class BaseAgent(ABC):
    """Abstract base for all agents in the swarm."""

    def __init__(
        self,
        name: str,
        job: JobState,
        tools: ToolRegistry,
        memory: PortingMemory,
    ):
        self.name = name
        self.job = job
        self.tools = tools
        self.memory = memory
        self._message_counter = len(job.messages) + 1

    def log(
        self,
        content: str,
        msg_type: str = "observation",
    ) -> AgentMessage:
        """Append a structured message to the job (visible in UI)."""
        msg = AgentMessage(
            id=self._message_counter,
            agent=self.name,
            timestamp=datetime.utcnow().strftime("%H:%M:%S"),
            type=msg_type,  # type: ignore[arg-type]
            content=content,
        )
        self.job.messages.append(msg)
        self._message_counter += 1
        return msg

    def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Call a registered tool and log the action."""
        self.log(f"Calling tool: {tool_name} with {list(kwargs.keys())}", "action")
        result = self.tools.call(tool_name, **kwargs)
        self.log(f"Tool {tool_name} result: {str(result)[:300]}...", "observation")
        return result

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Main entry point for the agent. Must be implemented by subclasses."""
        raise NotImplementedError


class OrchestratorAgent(BaseAgent):
    """High-level planner and dispatcher. Owns the overall plan and repair budget."""

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.log("Orchestrator starting job planning", "thought")
        # In full implementation this will build a plan and dispatch specialists.
        # For now this is a stub that demonstrates the interface.
        return {"status": "planned", "next": "porting_specialist"}


class PortingSpecialistAgent(BaseAgent):
    """The star agent for CUDA → HIP porting and autonomous repair loops.

    Contains real repair logic (diagnosis + memory-guided patching + retry).
    When we have vLLM-ROCm this will become LLM-driven tool calling,
    but the structure and tool usage remain identical.
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.log("Porting Specialist activated. Beginning hipify + compile + repair loop.", "thought")
        return {"status": "repair_loop_ready", "repair_budget": 5}

    def repair_with_memory(self, max_loops: int = 3) -> dict[str, Any]:
        """Real (non-LLM) repair logic using tools + memory.

        This is the 'logic thật' for Phase 2 preparation.
        It diagnoses errors, queries memory for known patterns,
        applies precise patches via the tool, and retries.
        """
        registry = self.tools
        mem = self.memory

        self.log(f"Starting repair loop (budget = {max_loops})", "thought")

        # Ensure we have hipified output
        self.log("Running hipify...", "action")
        registry.execute("run_hipify")

        for attempt in range(1, max_loops + 1):
            self.log(f"hipcc compile attempt #{attempt}...", "action")
            res = registry.execute("run_hipcc", sources=["vectorAdd.hip.cpp"])

            if res.get("success"):
                self.log("hipcc succeeded.", "observation")
                return {"status": "success", "attempts": attempt}

            error = res.get("error") or res.get("log", "")
            self.log(f"hipcc failed: {error[:160]}...", "observation")

            # Read evidence
            self.log("Reading logs and source for diagnosis...", "action")
            log_res = registry.execute("read_file", relative_path="logs/hipcc.log")
            src_res = registry.execute("read_file", relative_path="hip_out/vectorAdd.hip.cpp")
            error_text = str(log_res.get("content", "")) + "\n" + error
            source_text = str(src_res.get("content", ""))

            # Query real memory
            self.log("Querying memory for known fixes...", "action")
            patterns = mem.get_relevant_patterns(error_text + " " + source_text, top_k=3)
            if patterns:
                self.log(f"Memory matched {len(patterns)} pattern(s).", "observation")
            else:
                self.log("No strong memory match.", "observation")

            # === Real decision logic using memory patterns ===
            self.log("Analyzing error against retrieved memory patterns...", "thought")

            patched = False
            for pattern in patterns:
                cuda_str = str(pattern.get("cuda", ""))
                hip_str = str(pattern.get("hip", ""))
                notes = str(pattern.get("notes", ""))

                # Try to find a matching bad string in the current source based on the pattern
                if cuda_str and cuda_str in source_text:
                    self.log(f"Applying pattern '{pattern.get('pattern_id')}' : {cuda_str} → {hip_str}", "thought")
                    self.log(f"Reason from memory: {notes}", "observation")

                    # Record decision on blackboard
                    registry.execute(
                        "write_agent_note",
                        note=f"Applied pattern {pattern.get('pattern_id')}: {cuda_str} -> {hip_str}. Reason: {notes}"
                    )

                    patch = registry.execute(
                        "apply_search_replace",
                        relative_path="hip_out/vectorAdd.hip.cpp",
                        old_text=cuda_str,
                        new_text=hip_str + "  // repaired using memory pattern " + pattern.get('pattern_id', ''),
                    )
                    if patch.get("success"):
                        self.log("Memory-guided patch applied successfully.", "action")
                        patched = True
                        break

            if not patched:
                # Fallback to a couple of well-known patterns if memory didn't give exact string
                if "cudaLaunchKernel" in error_text or "cudaLaunchKernel" in source_text:
                    self.log("Falling back to known kernel launch repair...", "thought")
                    for old in [
                        "cudaLaunchKernel<<<grid, block>>>(vectorAdd, grid, block, 0, 0, args);",
                        "cudaLaunchKernel<<<grid, block>>>(vectorAddKernel, grid, block, 0, 0, args);",
                    ]:
                        patch = registry.execute(
                            "apply_search_replace",
                            relative_path="hip_out/vectorAdd.hip.cpp",
                            old_text=old,
                            new_text="hipLaunchKernel(grid, block, 0, 0, vectorAdd, args);  // repaired by Porting Specialist + memory",
                        )
                        if patch.get("success"):
                            self.log("Fallback kernel launch patch applied.", "action")
                            patched = True
                            break

            if not patched:
                self.log("Could not find a matching patch from memory or fallbacks. Would escalate to LLM in full mode.", "observation")

        self.log("Repair budget exhausted. Will produce diagnostic report.", "thought")
        return {"status": "exhausted", "attempts": max_loops}
