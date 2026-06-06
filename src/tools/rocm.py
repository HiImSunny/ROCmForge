"""ROCm tool wrappers (hipify, hipcc, amd-smi, binary execution).

Phase 1: These are thin subprocess wrappers + clear "real hardware only" behavior.
On non-ROCm machines (Windows dev, etc.) they raise or return mock data
controlled by ROCFORGE_MOCK=1 so the pipeline logic + report generation can be developed.

All real work (including vLLM later) must run on the MI300X instance.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Optional

from src.models.job import JobState, RawMetrics


MOCK = os.environ.get("ROCFORGE_MOCK", "0") == "1"


def _run(cmd: list[str], cwd: Optional[Path] = None, timeout: int = 300) -> tuple[int, str, str]:
    """Run a command, return (returncode, stdout, stderr)."""
    if MOCK:
        # Never actually shell out on mock
        return 0, f"[MOCK] would run: {' '.join(cmd)}", ""

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        return 124, "", f"Timeout after {timeout}s: {e}"


def is_rocm_available() -> bool:
    if MOCK:
        return True
    rc, _, _ = _run(["hipcc", "--version"])
    return rc == 0


def get_gpu_info() -> dict:
    """Best-effort GPU name + ROCm version from amd-smi or hipcc."""
    if MOCK:
        return {"name": "AMD Instinct MI300X (mock)", "rocm": "6.x-mock", "arch": "gfx942"}

    # Try amd-smi first (preferred in 2026)
    rc, out, _ = _run(["amd-smi", "--version"])
    if rc == 0:
        # Also capture a quick static view
        rc2, out2, _ = _run(["amd-smi"])
        return {"raw": out.strip() + "\n" + out2.strip()}

    rc, out, _ = _run(["hipcc", "--version"])
    return {"raw": out.strip() if rc == 0 else "unknown"}


def run_hipify(source_dir: Path, out_dir: Path, job_id: str) -> tuple[bool, str, str]:
    """Run hipify-clang (preferred) or hipify-perl on the .cu files in source_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)

    cu_files = list(source_dir.glob("*.cu")) + list(source_dir.glob("*.cuh"))
    if not cu_files:
        return False, "", "No .cu files found to hipify"

    # Prefer hipify-clang
    hipify_bin = "hipify-clang"
    cmd = [hipify_bin, "--cuda-path=/usr/local/cuda", "-o", str(out_dir)]
    cmd += [str(f) for f in cu_files]

    rc, stdout, stderr = _run(cmd, cwd=source_dir, timeout=120)
    success = rc == 0

    log = f"$ {' '.join(cmd)}\n{stdout}\n{stderr}"
    return success, log, stderr


def run_hipcc(hip_sources: list[Path], out_binary: Path, arch: str = "gfx942") -> tuple[bool, str, str]:
    """Compile with hipcc targeting the MI300X arch."""
    if not hip_sources:
        return False, "", "No HIP sources to compile"

    cmd = ["hipcc", "-O3", f"--offload-arch={arch}"]
    cmd += [str(p) for p in hip_sources]
    cmd += ["-o", str(out_binary)]

    rc, stdout, stderr = _run(cmd, timeout=180)
    success = rc == 0
    log = f"$ {' '.join(cmd)}\n{stdout}\n{stderr}"
    return success, log, stderr


def capture_amd_smi_snapshot() -> RawMetrics:
    """Capture a single amd-smi snapshot (json preferred)."""
    if MOCK:
        return RawMetrics(
            gpu_utilization_percent=92.0,
            power_watts_avg=680.0,
            power_watts_peak=710.0,
            temperature_c=67.0,
            memory_used_mb=42000.0,
            clock_sclk_mhz=2100.0,
            clock_mclk_mhz=5200.0,
        )

    # amd-smi metric --json or similar (adjust to what the instance actually supports)
    rc, out, _ = _run(["amd-smi", "metric", "--json"], timeout=10)
    if rc != 0 or not out.strip():
        # Fallback to plain amd-smi
        rc, out, _ = _run(["amd-smi"], timeout=10)

    # Extremely defensive parse — real implementation will improve on Day 0/1
    # For now return plausible defaults + raw in logs
    return RawMetrics()


def run_binary(binary: Path, args: list[str], timeout: int = 120) -> tuple[int, str, str, float]:
    """Execute the compiled HIP binary and return (rc, stdout, stderr, wall_time_s)."""
    start = time.time()

    if MOCK:
        # Produce realistic output for our known seeds so the report + metrics look good
        name = binary.name.lower()
        if "vectoradd" in name or "vector_add" in name:
            stdout = _mock_seed_output("vectorAdd")
        elif "matmul" in name or "tiled" in name:
            stdout = _mock_seed_output("tiledMatmul")
        elif "reduce" in name:
            stdout = _mock_seed_output("reduction")
        else:
            stdout = "seed completed successfully.\nKernel time: 1.23 ms\n"
        rc, stderr = 0, ""
        wall = 0.0123
    else:
        rc, stdout, stderr = _run([str(binary)] + args, timeout=timeout)
        wall = time.time() - start

    return rc, stdout, stderr, wall


def _mock_seed_output(seed_name: str) -> str:
    """Return realistic stdout that matches what our real seed binaries print.
    This makes mock runs produce good metrics and a convincing report.
    """
    if seed_name == "vectorAdd":
        return (
            "ROCmForge vectorAdd seed\n"
            "Elements: 268435456 (1024.00 MB per vector)\n"
            "Total data moved (read+write): 3.00 GB\n"
            "Result check: c[0]=0.1800 (exp 0.1800), c[n-1]=2.5100 (exp 2.5100)\n"
            "\n=== vectorAdd Timing ===\n"
            "Kernel time: 0.652 ms\n"
            "Achieved bandwidth: 4601.23 GB/s\n"
            "Theoretical MI300X HBM3 peak (reference): 5300 GB/s\n"
            "Efficiency (approx): 86.8%\n"
            "vectorAdd seed completed successfully.\n"
        )
    elif seed_name == "tiledMatmul":
        return (
            "ROCmForge tiledMatmul seed\n"
            "Matrix size: 1024x1024 (4.00 MB per matrix)\n"
            "FLOPs (2*M*N*K): 2.15 GFLOPs\n"
            "Sanity C[0,0] = 17.8500 (expected ~17.8500)\n"
            "\n=== Tiled Matmul Timing ===\n"
            "Kernel time: 1.874 ms\n"
            "Achieved: 1.15 TFLOPS\n"
            "Theoretical FP32 peak reference (MI300X): ~163 TFLOPS\n"
            "Efficiency (FP32 approx): 0.7%\n"
            "tiledMatmul seed completed successfully.\n"
        )
    elif seed_name == "reduction":
        return (
            "ROCmForge reduction seed\n"
            "Elements: 268435456\n"
            "Reduction result: 268435456 (expected 268435456)\n"
            "Kernel time: 0.418 ms\n"
            "Effective read BW: 642.00 GB/s\n"
            "reduction seed completed.\n"
        )
    return "seed completed successfully.\n"


def parse_binary_output_for_metrics(stdout: str) -> dict:
    """Very lightweight parser for the seed binaries' printed numbers.
    Seeds print lines like:
      Achieved bandwidth: 4610.23 GB/s
      Kernel time: 0.312 ms
    The baseline pipeline uses this + amd-smi for the final DerivedMetrics.
    """
    import re
    data: dict = {}
    if m := re.search(r"Achieved bandwidth:\s*([\d.]+)\s*GB/s", stdout):
        data["achieved_bw_gbs"] = float(m.group(1))
    if m := re.search(r"Kernel time:\s*([\d.]+)\s*ms", stdout):
        data["kernel_time_ms"] = float(m.group(1))
    if m := re.search(r"Achieved:\s*([\d.]+)\s*TFLOPS", stdout):
        data["achieved_tflops"] = float(m.group(1))
    if m := re.search(r"Reduction result:\s*([\d.]+)", stdout):
        data["reduction_result"] = float(m.group(1))
    return data
