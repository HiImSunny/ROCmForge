# ROCmForge Backend (Phase 1)

This is the Python/FastAPI side of ROCmForge — the autonomous CUDA → ROCm porting + benchmarking swarm.

## Current Phase
**Phase 1 — Foundation + Baseline Pipeline (non-agent)**

See `plan/5DAY_BLUEPRINT_AND_PHASES.md` and the root `AGENTS.md` / `CLAUDE.md`.

## Quick Start (on the MI300X instance)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run with REAL tools (never mock on the instance)
ROCFORGE_MOCK=0 python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# 3. Submit a seed (from another terminal or the frontend once wired)
curl -X POST http://localhost:8000/jobs \
  -H 'Content-Type: application/json' \
  -d '{"seed_id": "vectorAdd"}'

# 4. Poll status
curl http://localhost:8000/jobs/<job_id>/status

# 5. Stream (SSE)
curl -N http://localhost:8000/jobs/<job_id>/stream

# 6. Get polished report + tar
curl http://localhost:8000/jobs/<job_id>/report
curl -o artifacts.tar.gz http://localhost:8000/jobs/<job_id>/artifacts
```

## Environment
- `ROCFORGE_MOCK=1` — use for local Windows/macOS development of reports, state machine, and UI wiring. Never use on the real MI300X.
- All heavy execution (hipify, hipcc, binaries, amd-smi) must be real on the target hardware.

## Key Directories (per job)
See `plan/ARCHITECTURE.md` for the exact layout that `WorkspaceManager` creates.

## Next (Phase 2)
Layer genuine agents (LangGraph or custom ReAct) that use the tool surface in `src/tools/rocm.py` + richer repair loops + memory. The external API contract stays largely the same.

## Important
Every number that ends up in a report or the UI must come from real `amd-smi` + hipEvent timing captured on an actual AMD Instinct MI300X. No simulation for the core claims.
