# ROCmForge — Deployment & AMD Developer Cloud Guide

## Target Environment
- **Primary**: AMD Developer Cloud (MI300X instance) using the $100 credits provided for the hackathon.
- Everything (vLLM agent brains + HIP compilation + benchmarking + profiling) must run **natively on the MI300X** to showcase real ROCm performance.
- The instance should support Docker with device passthrough (`/dev/kfd`, `/dev/dri`).

## Recommended Launch Path (Fastest for 5 Days)

1. **Sign up / Claim Credits**
   - Go through the official "Sign up with AMD" flow on the hackathon page.
   - Get approved for AMD AI Developer Program and receive cloud credits.

2. **Launch Instance**
   - Use a **vLLM Quick Start image** or official ROCm base image that already has:
     - ROCm (hipcc, hipify-clang, amd-smi/rocm-smi)
     - Python + torch with ROCm support
     - Easy Docker + device support
   - Request **1x MI300X** (192 GB VRAM is the hero feature).
   - Instance size: enough host RAM/CPU for comfortable Docker + vLLM (typically 64 GB+ RAM recommended).

3. **First-Time Verification (Day 0 — Non-Negotiable)**
   Run the commands from `track/DAY0_HARDWARE_VERIFICATION.md`:
   - `amd-smi` shows the MI300X.
   - `hipcc --version` and `hipify-clang --help`.
   - Python torch ROCm works.
   - One manual seed port + benchmark + metrics capture succeeds.

4. **Docker-Based Deployment (Recommended)**
   Use a `docker-compose.yml` so the whole system (vLLM + app) is reproducible.

   Example skeleton (refine with exact working flags on your instance):

   ```yaml
   version: "3.8"

   services:
     vllm-brain:
       image: rocm/vllm:latest   # or the exact image that worked in Day 0
       container_name: rocmforge-vllm
       devices:
         - /dev/kfd
         - /dev/dri
       group_add:
         - video
       ipc: host
       shm_size: 16gb
       environment:
         - HSA_OVERRIDE_GFX_VERSION=11.0.0   # sometimes needed
       command: >
         vllm serve Qwen/Qwen2.5-Coder-32B-Instruct
         --port 8000
         --gpu-memory-utilization 0.82
         --tensor-parallel-size 1
         --max-model-len 16384
       ports:
         - "8000:8000"
       restart: unless-stopped

     rocmforge-app:
       build:
         context: .
         dockerfile: Dockerfile
       container_name: rocmforge-app
       depends_on:
         - vllm-brain
       devices:
         - /dev/kfd
         - /dev/dri
       group_add:
         - video
       ipc: host
       shm_size: 8gb
       environment:
         - VLLM_BASE_URL=http://vllm-brain:8000/v1
         - ROCmFORGE_JOB_DIR=/jobs
       ports:
         - "7860:7860"   # Gradio
         - "8001:8001"   # FastAPI (if separate)
       volumes:
         - ./jobs:/jobs
         - ./seeds:/app/seeds:ro
       restart: unless-stopped
   ```

   **Key device flags** (must work):
   - `--device=/dev/kfd --device=/dev/dri --group-add=video`

5. **Dockerfile Sketch (for the app)**
   ```dockerfile
   FROM rocm/dev-ubuntu-22.04:latest   # or a lighter base that worked

   # Install Python deps, FastAPI, Gradio, etc.
   RUN pip install fastapi uvicorn gradio pydantic httpx

   WORKDIR /app
   COPY . .

   # Make sure hipcc/hipify are in PATH (usually already are in ROCm images)
   ENV PATH="/opt/rocm/bin:${PATH}"

   CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
   ```

   For Gradio, you can run it directly in the same container or as a separate service.

6. **Health Checks (Must Be Rich)**
   ```bash
   curl -f http://localhost:8001/health
   # Expected JSON example:
   # {
   #   "status": "healthy",
   #   "gpu": "AMD Instinct MI300X (gfx942)",
   #   "rocm_version": "...",
   #   "vllm_reachable": true,
   #   "vllm_model": "Qwen/Qwen2.5-Coder-32B-Instruct"
   # }
   ```

## One-Click-ish Launch Script (Highly Recommended)

Create a small `launch_on_amd_cloud.sh` (or equivalent) that:
- Checks `amd-smi`
- Brings up docker compose
- Waits for vLLM to be ready
- Prints the Gradio URL + health URL
- Optionally seeds one demo job

This makes the "deployment evidence" bulletproof for judges.

## AMD Developer Cloud Specific Tips (From Research & Previous Winners)

- Use the exact image recommended in the hackathon resources or the vLLM quick-start if it includes ROCm + Docker support.
- Watch for device permission issues — the `--group-add video` and proper user inside container are critical.
- 192 GB is generous — you can comfortably run a 32B-class coder model with good context while still having headroom for HIP workloads.
- Capture `amd-smi` output early and often. Judges love seeing the actual hardware name and sustained high utilization/power numbers.
- Credits are limited — prefer one MI300X instance and optimize usage (demo/replay modes are your friend).

## Local / Alternative Deployment (for Development & Judges)

- For pure development on a machine with ROCm: same docker-compose works if the host has ROCm installed.
- For judges who cannot spin a full instance immediately: the **demo/replay** paths + pre-captured artifacts + a "replay mode" that works with minimal or no GPU (using cached metrics + traces) are mandatory.
- Document both "full real hardware" and "demo/replay" clearly in README and JUDGING.md.

## Monitoring & Observability on the Instance

- Run `amd-smi` or `rocm-smi` in a side terminal or background sampler during benchmarks.
- The app itself should expose the live metrics via the SSE stream and the final report JSON.
- Log all hipify / hipcc commands with full flags — this becomes part of the "reproducible" evidence.

## Security / Production Notes (Lightweight for Hackathon)

- Job directories are isolated per UUID.
- No arbitrary user code execution from the internet (only seeds + limited simple uploads).
- All tool calls inside the swarm are sandboxed to the job dir + timeouts.
- vLLM is exposed only internally (between containers) or with proper auth if you open it.
- Follow basic container security (non-root user inside containers where possible, read-only mounts for seeds, etc.).

See the main `Dockerfile` and `docker-compose.yml` in the repo root for the exact versions that worked on your MI300X instance during Day 0 verification.

**Golden Rule**: If it doesn't run cleanly with `docker compose up` on a fresh AMD Developer Cloud MI300X instance (or the demo/replay equivalent), it is not ready for submission. 

Update this file with the exact working commands, image names, and launch steps from your actual Day 0 / Day 4 runs. This becomes one of the strongest pieces of "we actually did this on real AMD hardware" evidence.