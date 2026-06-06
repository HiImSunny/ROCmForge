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

    The `run_mock_repair` method below uses the real ToolRegistry + Memory
    to demonstrate a full repair loop (for development and narrative purposes).
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.log("Porting Specialist activated. Beginning hipify + compile + repair loop.", "thought")
        return {"status": "repair_loop_ready", "repair_budget": 5}

    def run_mock_repair(self) -> dict[str, Any]:
        """Demo / development method that executes a realistic repair loop
        using the actual tools and memory (no real LLM yet).
        """
        from src.agents.mock_harness import run_mock_repair_loop
        # For now we delegate to the harness for the demo flow.
        # In real implementation this class would contain the decision logic.
        result = run_mock_repair_loop(job_id=self.job.job_id)
        self.job.messages.extend(result.messages[-10:])  # bring in the demo messages
        return {"status": "repair_completed_in_mock", "messages_added": 10}
