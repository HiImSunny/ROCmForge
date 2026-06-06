"""Phase 2 Agent Tool Registry (improved for usability).

This module provides a clean, LLM-friendly tool surface for agents.

Key improvements (B task):
- More tools (list files, blackboard notes, job summary)
- Excellent `get_tools_for_prompt()` and `format_tool_descriptions()` 
- Consistent return shape: always dict with "success", "result" or "error"
- `execute()` as the main agent-friendly entry point
- Better sandboxing and error messages
- Easy to extend

Agents should primarily use:
    registry.execute("tool_name", **args)
    tools_desc = registry.format_tool_descriptions()
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from src.tools.rocm import (
    capture_amd_smi_snapshot,
    run_binary,
    run_hipcc,
    run_hipify,
)
from src.workspace.manager import WorkspaceManager


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]          # JSON-schema style for LLMs
    func: Callable[..., dict[str, Any]]


class ToolRegistry:
    """Central registry of tools available to agents for a specific job."""

    def __init__(self, job_id: str, workspace: WorkspaceManager, seeds_root: Path):
        self.job_id = job_id
        self.ws = workspace
        self.seeds_root = seeds_root
        self._tools: dict[str, Tool] = {}
        self._register_core_tools()

    # ------------------------------------------------------------------
    # Public API (what agents will mostly use)
    # ------------------------------------------------------------------

    def execute(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Main entry point for agents. Always returns a dict."""
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"Unknown tool: {name}"}

        try:
            result = tool.func(**kwargs)
            if isinstance(result, dict):
                result.setdefault("success", True)
                return result
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e), "tool": name}

    def get_tool(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        """Raw tool metadata."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
            for t in self._tools.values()
        ]

    def format_tool_descriptions(self) -> str:
        """Beautiful markdown list ready to paste into a system prompt."""
        lines = ["# Available Tools (call them using the exact name and parameters):"]
        for t in self._tools.values():
            lines.append(f"\n## {t.name}")
            lines.append(t.description)
            if t.parameters.get("properties"):
                lines.append("Parameters:")
                for pname, pspec in t.parameters.get("properties", {}).items():
                    req = " (required)" if pname in t.parameters.get("required", []) else ""
                    lines.append(f"  - {pname}{req}: {pspec.get('description', '')}")
        return "\n".join(lines)

    def get_tools_for_prompt(self) -> list[dict[str, Any]]:
        """Compact form good for tool-calling frameworks (OpenAI style, LangChain, etc.)."""
        return self.list_tools()

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    # ------------------------------------------------------------------
    # Tool registration
    # ------------------------------------------------------------------

    def _register_core_tools(self) -> None:
        self.register(Tool(
            name="run_hipify",
            description="Run hipify-clang on the job's CUDA sources. Call this early when porting a new kernel.",
            parameters={"type": "object", "properties": {}},
            func=self._tool_run_hipify,
        ))

        self.register(Tool(
            name="run_hipcc",
            description="Compile HIP sources with hipcc for gfx942. Use after hipify or after applying patches.",
            parameters={
                "type": "object",
                "properties": {
                    "sources": {"type": "array", "items": {"type": "string"},
                                "description": "List of .cpp or .hip.cpp files relative to hip_out/"},
                    "arch": {"type": "string", "default": "gfx942"},
                },
                "required": ["sources"],
            },
            func=self._tool_run_hipcc,
        ))

        self.register(Tool(
            name="read_file",
            description="Read any file inside the current job workspace (cuda_src/, hip_out/, logs/, etc.).",
            parameters={
                "type": "object",
                "properties": {
                    "relative_path": {"type": "string", "description": "Path relative to the job root"},
                },
                "required": ["relative_path"],
            },
            func=self._tool_read_file,
        ))

        self.register(Tool(
            name="apply_search_replace",
            description="Precise search-and-replace edit. Preferred for small targeted fixes after reading the error and source.",
            parameters={
                "type": "object",
                "properties": {
                    "relative_path": {"type": "string"},
                    "old_text": {"type": "string", "description": "Exact string to replace (must exist)"},
                    "new_text": {"type": "string"},
                },
                "required": ["relative_path", "old_text", "new_text"],
            },
            func=self._tool_apply_search_replace,
        ))

        self.register(Tool(
            name="capture_amd_smi",
            description="Get current GPU metrics (util, power, temp, clocks). Call before and after benchmark runs.",
            parameters={"type": "object", "properties": {}},
            func=lambda: {"metrics": capture_amd_smi_snapshot().model_dump()},
        ))

        self.register(Tool(
            name="run_benchmark",
            description="Run the compiled binary and get stdout/stderr + wall time. Essential for validation and metrics.",
            parameters={
                "type": "object",
                "properties": {
                    "binary_name": {"type": "string", "description": "Optional. Defaults to the newest *_hip binary."},
                },
            },
            func=self._tool_run_benchmark,
        ))

        self.register(Tool(
            name="list_workspace_files",
            description="List files in a subdirectory of the job workspace (helpful for exploration).",
            parameters={
                "type": "object",
                "properties": {
                    "subdir": {"type": "string", "default": "", "description": "e.g. 'hip_out' or 'logs'"},
                },
            },
            func=self._tool_list_files,
        ))

        self.register(Tool(
            name="write_agent_note",
            description="Write a note to the job's blackboard (notes/ directory). Useful for sharing context between agents.",
            parameters={
                "type": "object",
                "properties": {
                    "note": {"type": "string"},
                    "filename": {"type": "string", "default": "agent_notes.txt"},
                },
                "required": ["note"],
            },
            func=self._tool_write_note,
        ))

    # ------------------------------------------------------------------
    # Internal tool implementations (return dicts)
    # ------------------------------------------------------------------

    def _get_job_dir(self) -> Path:
        return self.ws.get_workspace(self.job_id)

    def _tool_run_hipify(self) -> dict[str, Any]:
        ws_dir = self._get_job_dir()
        ok, log, err = run_hipify(ws_dir / "cuda_src", ws_dir / "hip_out", self.job_id)
        return {"success": ok, "log": log, "error": err}

    def _tool_run_hipcc(self, sources: list[str], arch: str = "gfx942") -> dict[str, Any]:
        ws_dir = self._get_job_dir()
        hip_out = ws_dir / "hip_out"
        source_paths = []
        for s in sources:
            p = Path(s)
            source_paths.append(p if p.is_absolute() else hip_out / p)
        binary = hip_out / f"{self.job_id}_hip"
        ok, log, err = run_hipcc(source_paths, binary, arch=arch)
        return {"success": ok, "log": log, "error": err, "binary_path": str(binary) if ok else None}

    def _tool_read_file(self, relative_path: str) -> dict[str, Any]:
        ws_dir = self._get_job_dir()
        target = (ws_dir / relative_path).resolve()
        if not str(target).startswith(str(ws_dir)):
            return {"success": False, "error": "Path escapes job workspace"}
        if not target.exists():
            return {"success": False, "error": f"File not found: {relative_path}"}
        return {"success": True, "content": target.read_text(encoding="utf-8", errors="replace")}

    def _tool_apply_search_replace(self, relative_path: str, old_text: str, new_text: str) -> dict[str, Any]:
        ws_dir = self._get_job_dir()
        target = (ws_dir / relative_path).resolve()
        if not str(target).startswith(str(ws_dir)):
            return {"success": False, "error": "Path escapes workspace"}
        if not target.exists():
            return {"success": False, "error": "File does not exist"}

        content = target.read_text(encoding="utf-8")
        if old_text not in content:
            return {"success": False, "error": "old_text not found in file (exact match required)"}

        new_content = content.replace(old_text, new_text, 1)
        target.write_text(new_content, encoding="utf-8")
        return {"success": True, "file": relative_path, "bytes_changed": len(new_text) - len(old_text)}

    def _tool_run_benchmark(self, binary_name: str | None = None) -> dict[str, Any]:
        ws_dir = self._get_job_dir()
        hip_out = ws_dir / "hip_out"
        if binary_name is None:
            candidates = list(hip_out.glob("*_hip")) + list(hip_out.glob("*hip"))
            if not candidates:
                return {"success": False, "error": "No compiled binary found"}
            binary = max(candidates, key=lambda p: p.stat().st_mtime)
        else:
            binary = hip_out / binary_name

        if not binary.exists():
            return {"success": False, "error": f"Binary not found: {binary}"}

        rc, stdout, stderr, wall = run_binary(binary, [])
        return {
            "success": rc == 0,
            "returncode": rc,
            "stdout": stdout,
            "stderr": stderr,
            "wall_time_seconds": round(wall, 4),
        }

    def _tool_list_files(self, subdir: str = "") -> dict[str, Any]:
        base = self._get_job_dir() / subdir if subdir else self._get_job_dir()
        if not base.exists():
            return {"success": False, "error": "Directory does not exist"}
        files = [str(p.relative_to(self._get_job_dir())) for p in base.rglob("*") if p.is_file()]
        return {"success": True, "files": sorted(files)[:50]}  # limit for prompt size

    def _tool_write_note(self, note: str, filename: str = "agent_notes.txt") -> dict[str, Any]:
        notes_dir = self._get_job_dir() / "notes"
        notes_dir.mkdir(exist_ok=True)
        path = notes_dir / filename
        with path.open("a", encoding="utf-8") as f:
            f.write(f"[{self.job_id}] {note}\n")
        return {"success": True, "written_to": str(path.relative_to(self._get_job_dir()))}


# ----------------------------------------------------------------------
# Convenience helpers (makes the system much easier to use from agents)
# ----------------------------------------------------------------------

def create_tool_registry(job_id: str, workspace: WorkspaceManager, seeds_root: Path) -> ToolRegistry:
    """Factory function — the recommended way to get a ready-to-use registry."""
    return ToolRegistry(job_id, workspace, seeds_root)


def build_agent_context(
    registry: ToolRegistry,
    memory,
    task_description: str,
    include_tools: bool = True,
    include_memory: bool = True,
) -> str:
    """One-call helper that returns a ready-to-paste block for an agent's system prompt."""
    parts = []
    if include_tools:
        parts.append(registry.format_tool_descriptions())
    if include_memory:
        mem_context = memory.get_context_for_agent(task_description)
        parts.append("\n" + mem_context)
    return "\n\n".join(parts) if parts else ""
