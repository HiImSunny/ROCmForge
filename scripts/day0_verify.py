#!/usr/bin/env python3
"""Day 0 Hardware Verification helper for ROCmForge.

Run this on the actual AMD MI300X instance (after claiming credits and launching).

It automates as many checks as possible from track/DAY0_HARDWARE_VERIFICATION.md
and prints copy-paste friendly output + suggested next commands.

Usage (on the instance):
    python scripts/day0_verify.py
    # or
    ROCFORGE_MOCK=0 python scripts/day0_verify.py

Then manually fill screenshots / paste key blocks into track/DAY0_HARDWARE_VERIFICATION.md.
"""

import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def shutil_which(name: str) -> bool:
    from shutil import which
    return which(name) is not None


def main() -> None:
    print("=" * 70)
    print("ROCmForge — Day 0 MI300X Verification")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working dir: {Path.cwd()}")
    print(f"MOCK mode: {os.environ.get('ROCFORGE_MOCK', '0')}")
    print()

    # 1. ROCm visibility
    print("1. amd-smi / rocm-smi")
    rc, out, err = run(["amd-smi", "--version"] if shutil_which("amd-smi") else ["rocm-smi", "--version"])
    print("   version:", out or err)
    rc, out, err = run(["amd-smi"] if shutil_which("amd-smi") else ["rocm-smi", "-a"])
    print("   output (first 20 lines):")
    for line in (out or err).splitlines()[:20]:
        print("   ", line)
    print()

    # 2. hipify + hipcc
    print("2. hipify & hipcc")
    for tool in (["hipify-clang", "--help"], ["hipcc", "--version"]):
        rc, out, err = run(tool)
        print(f"   {' '.join(tool[:1])}: rc={rc}")
        if out:
            print("   ", out.splitlines()[0][:100])
    print()

    # 3. Torch + HIP
    print("3. PyTorch ROCm")
    code = """
import torch
print('PyTorch:', torch.__version__)
print('HIP:', torch.version.hip)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('Device 0:', torch.cuda.get_device_name(0))
    print('Count:', torch.cuda.device_count())
"""
    rc, out, err = run([sys.executable, "-c", code])
    print(out or err)
    print()

    # 4. One manual seed (vectorAdd) — best effort
    print("4. Manual vectorAdd seed (quick smoke)")
    seeds = Path("seeds/vectorAdd.cu")
    if not seeds.exists():
        print("   seeds/vectorAdd.cu not found in this checkout. git pull or copy it.")
    else:
        print("   Found seed. To run full manual port + metrics capture:")
        print("     mkdir -p /tmp/day0 && cp seeds/vectorAdd.cu /tmp/day0/")
        print("     cd /tmp/day0")
        print("     hipify-clang vectorAdd.cu -o .")
        print("     hipcc -O3 --offload-arch=gfx942 -o vectorAdd_hip *.hip.cpp")
        print("     amd-smi metric --json > before.json")
        print("     ./vectorAdd_hip")
        print("     amd-smi metric --json > during.json")
        print("   Then paste key amd-smi lines + timing into track/DAY0_HARDWARE_VERIFICATION.md")
    print()

    print("=" * 70)
    print("Next: Fill track/DAY0_HARDWARE_VERIFICATION.md with real output + screenshots.")
    print("Then start Phase 1: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000")
    print("=" * 70)



if __name__ == "__main__":
    main()
