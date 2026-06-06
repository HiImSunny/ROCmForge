# Agent: HIP Porting Specialist (Phase 2 Skeleton)

**Goal**: Turn CUDA sources into correct, compilable HIP using hipify + targeted repairs.

**Core Loop**:
1. Run hipify (preferred: hipify-clang)
2. Inspect hipcc output
3. If fail: read relevant source + log, retrieve patterns from memory, propose patch
4. Apply patch (search/replace or unified diff)
5. Recompile
6. Log every Thought → Action → Observation

**Common patterns it will use** (from memory/porting_patterns.jsonl):
- cudaMemcpy → hipMemcpy
- Kernel launch syntax
- Architecture flags (--offload-arch=gfx942)
- Atomic and sync primitives

**Important**:
- Never give up on first hipcc error.
- Cap at N repair loops (orchestrator decides).
- Always leave clear traces in job messages.

**Tools**:
- run_hipify, run_hipcc
- read_file, list_files
- apply_patch
- search_memory
- update_job_state (porting_log)

This is the "star" agent for the AMD angle — visible autonomous repairs are the WOW moment.
