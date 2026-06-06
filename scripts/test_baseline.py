#!/usr/bin/env python3
"""
ROCmForge Phase 1 — Baseline Pipeline Test Runner (MOCK mode safe)

Usage:
    # Local development (mock)
    python scripts/test_baseline.py vectorAdd

    # On real MI300X instance (after Day 0 verification)
    ROCFORGE_MOCK=0 python scripts/test_baseline.py vectorAdd

This runs the complete non-agent baseline end-to-end:
- Creates isolated workspace
- Copies seed
- hipify → hipcc (or mock)
- Executes + captures metrics
- Validates
- Generates migration_report.md + artifacts tar
- Prints the report and key numbers

Perfect for quickly validating the foundation before/after moving to real hardware.
"""

import os
import sys
from pathlib import Path

# Ensure we can import src when running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models.job import JobState, SeedId
from src.workspace.manager import WorkspaceManager
from src.baseline.pipeline import run_baseline

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_baseline.py <seed_id>")
        print("Available seeds: vectorAdd, tiledMatmul, reduction")
        sys.exit(1)

    seed_arg = sys.argv[1]
    try:
        seed_id = SeedId(seed_arg)
    except ValueError:
        print(f"Invalid seed: {seed_arg}")
        print("Valid: vectorAdd, tiledMatmul, reduction")
        sys.exit(1)

    mock = os.environ.get("ROCFORGE_MOCK", "1") == "1"
    print("=" * 72)
    print("ROCmForge Phase 1 Baseline Test")
    print(f"Seed: {seed_id.value}")
    print(f"Mode: {'MOCK (local dev)' if mock else 'REAL (MI300X)'}")
    print("=" * 72)

    job = JobState(seed_id=seed_id)
    ws = WorkspaceManager(base_dir=Path("./jobs"))

    seeds_root = Path(__file__).resolve().parents[1] / "seeds"

    print("\n[1/3] Running full baseline pipeline...")
    final_job = run_baseline(job, ws, seeds_root)

    print("\n[2/3] Pipeline finished.")
    print(f"  Status: {final_job.status}")
    print(f"  Final phase: {final_job.phase}")
    print(f"  Messages logged: {len(final_job.messages)}")
    print(f"  Workspace: {final_job.workspace_dir}")

    # Show last few messages (the "agent feed" style)
    print("\n--- Last activity ---")
    for msg in final_job.messages[-5:]:
        print(f"  [{msg.timestamp}] {msg.agent}: {msg.content[:80]}")

    # Show derived metrics
    d = final_job.metrics.derived
    print("\n--- Key Metrics ---")
    if d.achieved_bw_gbs:
        print(f"  Achieved BW: {d.achieved_bw_gbs:.2f} GB/s  |  Efficiency: {d.efficiency_percent}% of {d.theoretical_peak_gbs} GB/s")
    if d.achieved_tflops:
        print(f"  Achieved TFLOPS: {d.achieved_tflops:.2f}  |  Efficiency: {d.efficiency_tflops_percent}%")
    print(f"  Kernel time: {d.kernel_time_ms:.2f} ms")
    print(f"  Validation passed: {final_job.validation_passed}")

    # Print the report
    print("\n[3/3] Generated Migration Report:")
    if final_job.report_md_path and Path(final_job.report_md_path).exists():
        report = Path(final_job.report_md_path).read_text(encoding="utf-8")
        print("-" * 72)
        print(report)
        print("-" * 72)
    else:
        print("  (Report path not set)")

    if final_job.artifacts_tar_path:
        print(f"\nArtifacts tar ready: {final_job.artifacts_tar_path}")

    print("\n✅ Baseline test complete.")
    print("   Next on real hardware: set ROCFORGE_MOCK=0 and run on the MI300X instance.")
    print("=" * 72)


if __name__ == "__main__":
    main()
