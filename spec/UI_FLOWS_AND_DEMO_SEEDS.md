# ROCmForge — UI Flows & Demo Seeds

## Demo Seeds (Self-Contained, High-Impact)

**Rule**: Every seed must be small, self-contained, compile cleanly with hipcc after port, have an easy CPU reference for validation, and showcase different strengths (memory BW, compute, simple control flow).

### Seed 1: vectorAdd (Memory Bandwidth Hero)
- Classic CUDA sample.
- Shows memory movement (read + write).
- Easy to measure achieved BW vs 5.3 TB/s peak.
- Minimal host code.

### Seed 2: Tiled Matrix Multiplication (Compute + Shared Memory)
- Tiled matmul (e.g., 1024x1024 or 2048x2048).
- Uses shared memory, __syncthreads.
- Good for showing compute TFLOPS and occupancy.
- Nice before/after numbers if optimizer adjusts launch bounds or flags.

### Seed 3: Reduction / Parallel Sum (Control Flow + Atomics)
- Tree reduction or simple atomicAdd version.
- Tests synchronization and atomic patterns (common porting pain points).
- Good for repair loop demonstration.

**Seed Files Location** (in repo):
```
seeds/
  vectorAdd/
    vectorAdd.cu
    vectorAdd_cpu_ref.py   # or simple numpy
    expected_behavior.txt
  tiled_matmul/
    ...
  reduction/
    ...
```

Each seed dir also contains a small `run_verification.py` that the Validator can call (CPU vs HIP output comparison with tolerance).

## UI Flows (Gradio Recommended)

### Flow 1: Landing / Job List (Fast Overview)
- Big hero: "ROCmForge — Autonomous CUDA → ROCm on Real MI300X"
- Prominent "Try a Seed" section with 3 cards (vectorAdd, Tiled Matmul, Reduction).
- Each card: short description + "Run on MI300X" button + "View previous run" (if any).
- Recent jobs table (job_id, seed, status, key metric like "87% BW", time ago).
- Health banner at top: "Running on AMD Instinct MI300X via ROCm (credits active)" + link to /health.

### Flow 2: Submit & Watch Live (The WOW Flow)
1. User clicks a seed card or "Custom simple upload" (limited to .cu + .cuh, size cap).
2. Submit button → job created.
3. Redirect to /jobs/{id} live view.
4. **Live View Components** (update via SSE / polling):
   - Status pill + overall progress.
   - **Agent Activity Feed** (most important for "genuine agentic"):
     - Real-time scrolling list: [Agent Name] [timestamp] Thought / Action / Observation
     - Example: "HIP Porting Specialist — 14:32:11 — hipify succeeded on 4/5 files. hipcc failed: unknown identifier 'cudaLaunchKernel'. Reading kernel source at vectorAdd.cu:42..."
     - Color coded by agent.
   - **Live Metrics Dashboard** (the AMD depth):
     - Big cards: Current GPU Util %, Power (W), Temp (°C)
     - Sparklines or simple line charts (utilization and power over the last 30-60s of benchmark).
     - When benchmark phase active: "Achieved BW so far: 4.2 TB/s (79% of peak)"
   - File Diff / Progress viewer (optional but nice): shows which files were hipified, patched, compiled.
   - Phase timeline (Analysis → Porting → Validating → Benchmarking → Optimizing → Reporting).
5. When completed:
   - Big success banner with the shock metric (e.g., "vectorAdd ported autonomously in 47s on real MI300X — 87% of theoretical bandwidth").
   - Prominent download buttons: Full Report (MD), Artifacts (tar), Metrics JSON, Agent Trace.
   - "Replay this run" button (uses the fast demo/replay path).

### Flow 3: Demo / Replay Mode (Judge-Friendly, Low Friction)
- Dedicated section or big buttons on landing: "Replay vectorAdd (no wait, pre-captured on MI300X)".
- Clicking it:
  - Immediately shows a "completed" live view (or fast-forward animation of the agent feed + metrics).
  - Uses cached artifacts + re-runs only the benchmark + metrics capture part (fast, stable, low credit usage).
  - Still shows real numbers from previous real MI300X execution.
- This is the primary path for JUDGING.md 90-second verification.

### Flow 4: Report Viewer
- Clean rendered Markdown view of migration_report.md.
- Embedded key metrics table (with % efficiency highlighted).
- "View raw JSON metrics" and "Download everything" links.
- "How the swarm decided" section pulling key agent traces.

### Flow 5: Health & Instance Info (Transparency)
- /health page or banner:
  - ROCm version, MI300X detected, vLLM model loaded.
  - Current credits / instance note (for the hackathon).
  - "All heavy workloads (agent brains + HIP execution) ran on this exact MI300X".

## Technical Implementation Notes for UI (5-Day Velocity)

- **Gradio** is strongly recommended:
  - Blocks for layout.
  - gr.Chatbot or gr.HTML + custom JS for the agent feed (or simple gr.Dataframe that appends).
  - gr.Plot or gr.LinePlot for sparklines (or just text updating cards + a small matplotlib figure if needed).
  - gr.DownloadButton for artifacts.
  - Easy SSE support via gr.Blocks and background threads or queue.
- If not Gradio: FastAPI + Jinja2 templates + HTMX or simple JS for live updates (more work).
- State: The backend already has /jobs/{id}/stream (SSE). UI just consumes it.
- Demo seeds must be 100% reproducible with one click and work even if the main vLLM instance is under load.

## Demo Mode Technical Contract (Critical)

- `POST /api/demo/seed?seed=vectorAdd` → returns a job_id that is either pre-computed or very fast to prepare.
- `POST /api/demo/replay?job_id=xxx` → triggers a fast re-execution of only the benchmark + profiler phase (re-uses the already ported sources). Returns updated metrics but keeps the same agent trace.
- Both must be stable, fast (< 30-60s end-to-end for replay), and produce numbers that match (or are very close to) what was shown in the original real run.
- This allows judges to verify "it actually runs on MI300X" without waiting for full autonomy every time.

## Accessibility & Polish (Nice-to-Have but Valuable for Judges)
- Clear loading states.
- Copy buttons for all important commands (hipify, hipcc, amd-smi captures).
- "What this number means" tooltips on efficiency % (e.g., "87% of the MI300X's 5.3 TB/s HBM3 bandwidth").
- Mobile-friendly enough (hackathons often viewed on phones too).

This UI + seed design directly delivers the "WOW moment" (live agents thinking + real hardware metrics updating) while making verification trivial for judges — exactly the presentation patterns that win lablab.ai events.