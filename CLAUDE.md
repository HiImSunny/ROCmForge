# CLAUDE.md — ROCmForge Guidance

This is a companion file to AGENTS.md. Read AGENTS.md first.

## Quick Reminders for Every Session

- The project lives inside the "AMD Developer Hackathon ACT II" folder.
- All planning, specs, and progress must go through the dedicated folders:
  - `plan/` (blueprints, architecture, risks)
  - `spec/` (requirements, agent definitions, schemas, UI, deployment)
  - `track/` (evidence, logs, checklists — update this often)
  - `research/` (AMD/ROCm technical notes)
- Never jump straight to writing code in `src/` without checking the plan/spec first.
- Scope is intentionally tight: only self-contained seeds during the 5-day hackathon.
- Every real step on hardware or agent work must produce evidence in `track/`.
- The goal is not just "it works" — it is to demonstrate deep, measurable use of real MI300X + ROCm + genuine agentic behavior.

## When Starting Any New Task

1. Read `AGENTS.md` (if not already).
2. Check the latest entry in `track/DAILY_LOG.md`.
3. Load the relevant file from `plan/` or `spec/`.
4. At the end of significant work, update the daily log and any relevant checklist/evidence files.

## Project Identity

ROCmForge = Autonomous multi-agent CUDA → ROCm porting + validation + benchmarking + optimization swarm running natively on AMD MI300X via the hackathon cloud credits.

Key differentiators we must protect:
- Genuine agentic (real tool calling + visible autonomous decisions)
- Deep AMD (real metrics from amd-smi on actual hardware, hipify/hipcc usage, vLLM-ROCm)
- Production + judge friendly (Docker, health, demo/replay, JUDGING.md, excellent README)

If a proposed change weakens any of the above, push back or document the trade-off in `track/`.

## Useful Commands / Patterns

- Always prefer updating existing structured files over scattering notes.
- When in doubt about scope, re-read `plan/MILESTONES_AND_RISKS.md` and `spec/PRD_ROCMFORGE.md`.
- For agent-related work, the source of truth is `spec/AGENT_ROLES_AND_PROMPTS.md`.

This file + AGENTS.md exist so the project stays disciplined across multiple sessions and different agents.