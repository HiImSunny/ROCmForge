# ROCmForge — Day 0 Hardware Verification (Template)

**Goal**: Confirm that a real AMD Instinct MI300X instance is accessible via the hackathon credits, and that the core ROCm toolchain + vLLM-ROCm works for both agent brains and HIP workloads.

**Date**: [Fill when executed]  
**Instance ID / Name**: [From AMD Developer Cloud]  
**ROCm Version**: [Run `hipcc --version` or `amd-smi --version`]  
**MI300X Confirmation**: [Output of `amd-smi` or `rocm-smi` showing gfx942 / MI300X]

## Verification Checklist & Evidence

### 1. Basic ROCm / GPU Visibility
```bash
amd-smi          # or rocm-smi -a
amd-smi --version || rocm-smi --version
```
**Expected**: Shows MI300X / gfx942, memory (should be ~192 GB), temperature, power, utilization.

**Evidence captured**:
- Screenshot 1: amd-smi output
- Screenshot 2: rocm-smi (if different)
- Paste key lines here:
  ```
  [paste relevant output]
  ```

### 2. hipify & hipcc Toolchain
```bash
hipify-clang --help
hipcc --version
```
**Expected**: hipify-clang (preferred) or hipify-perl available; hipcc reports ROCm version and supports gfx942.

**Evidence**:
- Output of `hipcc --version`
- Any warnings or notes about the environment.

### 3. Python / Torch ROCm
```bash
python -c "
import torch
print('PyTorch version:', torch.__version__)
print('HIP version:', torch.version.hip)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('Device name:', torch.cuda.get_device_name(0))
    print('Device count:', torch.cuda.device_count())
"
```
**Expected**: torch with HIP support, device reports as MI300X.

### 4. vLLM-ROCm Quick Test (Agent Brains)
(If using a pre-installed vLLM image)

```bash
# Example serve command (adjust model to one that fits)
# vllm serve Qwen/Qwen2.5-Coder-32B-Instruct --port 8000 --gpu-memory-utilization 0.8

# Quick health / list models (OpenAI compatible)
curl http://localhost:8000/v1/models
```
**Evidence**:
- Model loaded successfully on MI300X.
- Rough memory usage observed via amd-smi during load.
- Note any tuning (tensor-parallel, quantization level used).

### 5. Manual End-to-End Seed Test (Most Important)
Choose one simple seed (e.g., vectorAdd or a minimal self-contained kernel).

Steps performed:
1. Copy CUDA source to a temp workspace.
2. Run hipify (note exact command + flags).
3. Run hipcc with proper arch (`--offload-arch=gfx942`).
4. Run the resulting binary with timing + verification.
5. Capture live metrics:
   ```bash
   amd-smi metric --json > /tmp/metrics_before.json
   # run the binary
   amd-smi metric --json > /tmp/metrics_during.json
   ```
6. Compute rough efficiency (use known MI300X peaks: ~5.3 TB/s HBM BW, FP32/TFLOPS numbers from docs or amd-smi).

**Evidence to capture**:
- Exact commands used.
- hipify output summary.
- hipcc compile success (or the errors that will be fed to agents later).
- Binary runtime + any verification output.
- amd-smi snapshots (before / during / after) — paste key utilization, power, temp, memory BW numbers.
- Calculated % of theoretical peak.
- Screenshots of:
  - Terminal during run.
  - amd-smi or rocm-smi dashboard while kernel is hot.
  - Final binary output.

**Result**: [Success / Partial / Issues found]
**Notes / Gotchas discovered**:
- [e.g., specific hipify mapping needed, memory flag, power limit behavior, etc.]

### 6. Docker / Container Device Passthrough Test (If Planning Docker)
```bash
docker run --rm --device=/dev/kfd --device=/dev/dri --group-add video rocm/dev-ubuntu-22.04:latest amd-smi
```
**Evidence**: Container sees the GPU correctly.

## Summary & Go / No-Go

**Overall Status**: [Phase 1 baseline code + seeds ready on dev machine. Awaiting user to claim credits + launch real MI300X instance, then run this verification + fill real numbers.]

**Key Numbers Captured** (for later use in reports):
- Peak memory BW observed: XXX GB/s (Y% of 5.3 TB/s)
- Sustained power during kernel: XXX W
- Utilization during kernel: XX%
- Any other impressive observations.

**Next Immediate Actions** (if green):
- Commit this file + all screenshots / json dumps to `track/`.
- Start Phase 1 baseline pipeline implementation.
- Begin populating `research/ROCm_hipify_vLLM_amd-smi_notes.md` with exact working commands.

**Screenshots / Artifacts Location** (relative to repo or absolute on instance):
- [List files or folders]

---

**This file becomes part of the submission evidence.**  
Judges and AMD team love seeing real hardware verification from day 0 with actual numbers and screenshots from the MI300X.

Fill it completely on the actual instance before heavy coding. Update with new discoveries as you go.