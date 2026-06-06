# ROCmForge — Research Notes: ROCm, hipify, vLLM on AMD, amd-smi / Profiling (2026)

This is a living research scratchpad. Add gotchas, exact commands that worked on the MI300X instance, version numbers, and links during Day 0+.

## 1. AMD Developer Cloud + MI300X Instance Setup (Day 0 Priority)

**Recommended image / starting point**:
- vLLM Quick Start image (often has ROCm + vLLM pre-installed) or official ROCm base + install what you need.
- Launch with proper device passthrough:
  ```
  docker run --device=/dev/kfd --device=/dev/dri --group-add video --shm-size 16G ...
  ```

**Verification commands that must succeed**:
```bash
amd-smi --version || rocm-smi --version
amd-smi   # or rocm-smi -a
hipcc --version
hipify-clang --help || hipify-perl --help
python -c "import torch; print(torch.version.hip); print(torch.cuda.get_device_name(0))"
```

**MI300X key specs to cite in reports** (use actual numbers from `amd-smi` or official docs on the instance):
- HBM3 bandwidth: ~5.3 TB/s (theoretical peak)
- Compute peaks (examples — verify on hardware):
  - FP32: ~163+ TFLOPS
  - FP16 / BF16 matrix: 1000+ TFLOPS range
  - FP8: even higher
- Always report % of theoretical under the exact conditions you ran (data type, launch config, etc.).

**Pro tip from previous winners**: Capture `amd-smi` (or `rocm-smi --json`) output + screenshots during the actual benchmark kernel execution, not just idle. Show sustained high utilization + power draw.

## 2. hipify (CUDA → HIP)

**Preferred tool**: `hipify-clang` (more accurate than the Perl version in many cases).

Basic usage:
```bash
hipify-clang --cuda-path=/usr/local/cuda-12.x -o hip_out/ cuda_src/vectorAdd.cu
```

Common post-hipify manual / LLM-assisted fixes (build a memory of these):
- `cudaMemcpy` variants → `hipMemcpy`
- Kernel launch syntax (`<<< >>>`) is mostly handled by hipcc, but sometimes needs `__launch_bounds__` hints.
- cu* library calls (cublas, cudnn, etc.) → hip equivalents or roc* libs (or stub for demo).
- `__syncthreads()` usually fine.
- Atomic operations often need `hip` prefixed versions or careful checking.

**Repair loop strategy** (core of the Porting Specialist agent):
1. Run hipify.
2. Run hipcc and capture full stderr/stdout.
3. Parse error for file + line + message.
4. Read the exact source snippet around the error.
5. Generate minimal targeted patch (search-replace or unified diff).
6. Apply, re-hipcc, repeat (cap at 5 loops for seeds).

**Known good patterns to preload in memory**:
- Many simple vector kernels port with almost zero changes after hipify.
- Shared memory + atomics usually need small syntax adjustments.
- Always test with the exact arch flag: `--offload-arch=gfx942` (or whatever the MI300X reports).

## 3. Compilation & Running on ROCm (hipcc)

Example compile for MI300X:
```bash
hipcc -O3 --offload-arch=gfx942 -o vectorAdd_hip vectorAdd.hip.cpp
./vectorAdd_hip
```

Useful flags for performance:
- `-O3`
- `--offload-arch=gfx942`
- `-munsafe-fp-atomics` (when appropriate)
- Launch bounds hints in kernel definition for better occupancy.

**Validation for seeds**:
- Provide a CPU reference (pure Python or numpy/torch on host).
- Run both and compare with reasonable tolerance (e.g. 1e-5 rel/abs depending on the kernel).
- Log max difference and whether it passed.

## 4. vLLM on ROCm (for Agent Brains)

**Why it matters for the story**: The agent "thinking" (tool calling decisions) also runs on the same MI300X hardware as the HIP workloads. This is a powerful narrative ("the swarm that ports CUDA is itself powered by the target hardware").

Quick start (adjust model to one that fits well in 192 GB with room for KV cache + workloads):
```bash
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct --port 8000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.85 \
  # other ROCm-friendly flags
```

OpenAI-compatible endpoint for the agents:
- Base URL: http://localhost:8000/v1
- Use tool calling / structured outputs where the model supports it.

**Model choice tips for 5 days**:
- Strong coding / reasoning model (Qwen2.5-Coder class or equivalent available in 2026).
- Keep context reasonable (8k-32k) to avoid blowing up latency/cost during many repair loops.
- The 192 GB VRAM is the hero feature — it lets you run a capable model with less aggressive quantization than on smaller GPUs.

## 5. Profiling & Metrics (The "Show AMD Love" Evidence)

**Primary tool**: `amd-smi` (modern) or `rocm-smi` (compat).

Live / JSON capture examples:
```bash
amd-smi metric --json > metrics_snapshot.json
amd-smi monitor -d 0 --json  # or similar for continuous
```

What to capture and report:
- Utilization (compute, memory)
- Power (W)
- Temperature
- Clocks (sclk, mclk)
- Memory used / total
- During the actual kernel execution (not just before/after)

**Derived efficiency calculations** (put in report + UI):
- Memory BW achieved = (bytes moved) / time
- % of peak = (achieved / 5.3e12) * 100
- Similar for compute (choose the right peak based on data type used in the kernel)
- Always state the exact conditions and the theoretical number source.

**Optional but impressive**: rocprof
```bash
rocprof --stats ./your_hip_binary
```
Parse kernel durations, occupancy hints, etc. Even basic stats look professional.

**Power/thermals story**: Showing sustained high but safe power draw (e.g. 600-800W range on MI300X during hot kernels) + good efficiency % is very convincing for "real high-performance workload".

## 6. Docker & Deployment on AMD Cloud

Example docker-compose skeleton (refine on the actual instance):
```yaml
services:
  vllm-brain:
    image: rocm/vllm or your custom
    devices:
      - /dev/kfd
      - /dev/dri
    group_add:
      - video
    shm_size: 16gb
    command: vllm serve ... --port 8000

  rocmforge-app:
    build: .
    devices:
      - /dev/kfd
      - /dev/dri
    group_add:
      - video
    environment:
      - VLLM_BASE_URL=http://vllm-brain:8000/v1
    ports:
      - "8001:8001"
    depends_on:
      - vllm-brain
```

**Health check example**:
```bash
curl -f http://localhost:8001/health | jq
# Should return GPU status + vLLM reachable + ROCm version
```

**Launch command on AMD cloud** (document exact one that worked):
- Usually something like the docker run with the device flags above.
- Make sure the instance has enough RAM + the GPU is visible inside containers.

## 7. Common Gotchas & Anti-Patterns (Add as you discover)

- hipify sometimes leaves `cuda*` symbols — agents must catch and fix.
- Different ROCm versions have slightly different hipify behavior — always note the version (`hipcc --version`).
- vLLM on ROCm can be sensitive to exact torch + ROCm combo — use the recommended quick-start image when possible.
- amd-smi vs rocm-smi: newer systems prefer amd-smi; have fallback parsing for both.
- Numerical validation tolerance: be explicit and conservative for the seeds you choose.
- Resource limits: 192 GB is huge, but don't assume infinite KV cache + multiple heavy jobs at once.

## 8. Useful References (Update with exact links that worked)

- AMD ROCm docs (hipify, hipcc, profiling)
- vLLM ROCm installation / serving guide (the one used on the instance)
- AMD Developer Cloud getting started (exact image names and launch steps)
- Previous AMD hackathon winning projects that showed good metrics (CogniCore, etc. — note what they highlighted)

---

**How to use this file**:
- During Day 0 hardware verification: paste every successful command + output + version numbers.
- As you implement agents: add exact error messages + the fix that worked.
- Before submission: clean up into a "commands that actually worked on MI300X" appendix in the final report or README.

This research note is what turns "we used AMD" into "here is the exact proof we ran real high-performance workloads and agent reasoning natively on MI300X via ROCm."

Add to it constantly. It will become gold for the final submission assets.