"""Porting Memory for ROCmForge Phase 2 agents.

This module provides a lightweight, dependency-free memory system
for storing and retrieving successful CUDA → HIP porting patterns.

Agents use this to:
- Retrieve relevant past fixes before attempting a repair.
- Inject high-quality few-shot examples into their prompts.
- (Future) Learn by appending new successful patterns after a job.

Usage (from an agent):
    mem = get_memory()
    patterns = mem.get_relevant_patterns("hipcc failed on kernel launch syntax")
    context = mem.format_for_prompt(patterns)
    # put `context` into the system prompt
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PortingMemory:
    """In-memory + file-backed store of porting patterns.

    Patterns are stored as JSON Lines in memory/porting_patterns.jsonl.
    Each pattern should have at minimum:
        pattern_id, cuda, hip, notes, confidence, source
    """

    def __init__(self, patterns_path: str | Path | None = None, auto_load: bool = True):
        if patterns_path is None:
            patterns_path = Path(__file__).resolve().parents[2] / "memory" / "porting_patterns.jsonl"
        self.patterns_path = Path(patterns_path).resolve()
        self._patterns: list[dict[str, Any]] = []
        if auto_load:
            self._load()

    def _load(self) -> None:
        self._patterns = []
        if not self.patterns_path.exists():
            return
        with self.patterns_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        self._patterns.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    def reload(self) -> None:
        """Reload patterns from disk (useful after another process appends)."""
        self._load()

    def save(self) -> None:
        """Persist current patterns back to disk (overwrites file)."""
        self.patterns_path.parent.mkdir(parents=True, exist_ok=True)
        with self.patterns_path.open("w", encoding="utf-8") as f:
            for p in self._patterns:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

    def add_pattern(self, pattern: dict[str, Any], persist: bool = False) -> None:
        """Add a new pattern to the in-memory store.

        Args:
            pattern: dict with at least pattern_id, cuda, hip, notes, confidence.
            persist: if True, immediately append to the jsonl file.
        """
        self._patterns.append(pattern)
        if persist:
            self.patterns_path.parent.mkdir(parents=True, exist_ok=True)
            with self.patterns_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(pattern, ensure_ascii=False) + "\n")

    def get_relevant_patterns(
        self,
        task_description: str,
        top_k: int = 5,
        min_confidence: float = 0.65,
        task_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve the most relevant patterns for a task.

        Simple but effective scoring:
        - Keyword overlap on cuda/hip/notes/pattern_id
        - Boost for exact matches
        - Confidence weighting
        """
        if not self._patterns:
            return []

        query = task_description.lower()
        query_words = set(query.split())

        scored: list[tuple[float, dict[str, Any]]] = []

        for p in self._patterns:
            if p.get("confidence", 0) < min_confidence:
                continue

            text = " ".join([
                str(p.get("cuda", "")),
                str(p.get("hip", "")),
                str(p.get("notes", "")),
                str(p.get("pattern_id", "")),
            ]).lower()

            # Score calculation
            matches = len(query_words & set(text.split()))
            exact_boost = 2 if any(w in text for w in query_words if len(w) > 4) else 0
            score = (matches * 1.0) + (p.get("confidence", 0.5) * 1.5) + exact_boost

            if matches > 0 or exact_boost > 0:
                scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:top_k]]

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._patterns)

    def format_for_prompt(self, patterns: list[dict[str, Any]] | None = None) -> str:
        """Nice compact format for injecting into an LLM system prompt."""
        if patterns is None:
            patterns = self.get_all()

        if not patterns:
            return "No relevant prior porting patterns found."

        lines = [
            "# Successful porting patterns from previous jobs (use these as guidance for fixes):"
        ]
        for p in patterns:
            pid = p.get("pattern_id", "unknown")
            cuda = p.get("cuda", "?")
            hip = p.get("hip", "?")
            notes = p.get("notes", "")
            conf = p.get("confidence", 0.8)
            lines.append(f"- [{pid}]  CUDA: {cuda}  →  HIP: {hip}")
            lines.append(f"    Notes: {notes} (confidence={conf})")
        return "\n".join(lines)

    def get_context_for_agent(self, task_description: str, top_k: int = 4) -> str:
        """One-call convenience: retrieve + format for prompt."""
        patterns = self.get_relevant_patterns(task_description, top_k=top_k)
        return self.format_for_prompt(patterns)


# Global singleton (convenient for agents)
_default_memory: PortingMemory | None = None

def get_memory() -> PortingMemory:
    global _default_memory
    if _default_memory is None:
        _default_memory = PortingMemory()
    return _default_memory

