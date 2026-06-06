"""ROCmForge — Autonomous CUDA → ROCm agent swarm on real MI300X.

Phase 1: Non-agent baseline pipeline (hipify → hipcc → validate → benchmark + amd-smi → report).
Everything that matters executes natively on AMD Instinct MI300X via ROCm.
"""
__version__ = "0.1.0-phase1"
