"""Pydantic models for Job state, metrics, and artifacts.

Aligned with spec/METRICS_AND_REPORT_SCHEMA.md and plan/ARCHITECTURE.md.
State is the single source of truth (persisted as state.json per job).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class JobPhase(str, Enum):
    """Execution phases matching the UI PhaseTimeline + architecture."""
    QUEUED = "Queued"
    ANALYSIS = "Analysis"
    PORTING = "Porting"
    VALIDATING = "Validating"
    BENCHMARKING = "Benchmarking"
    OPTIMIZING = "Optimizing"
    REPORTING = "Reporting"
    COMPLETED = "Completed"
    FAILED = "Failed"


class JobStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SeedId(str, Enum):
    VECTOR_ADD = "vectorAdd"
    TILED_MATMUL = "tiledMatmul"
    REDUCTION = "reduction"


class AgentMessage(BaseModel):
    """Structured message for the live agent feed (Phase 1 uses baseline steps as messages)."""
    id: int
    agent: str
    timestamp: str
    type: Literal["thought", "action", "observation"]
    content: str


class RawMetrics(BaseModel):
    """Raw values captured from amd-smi / rocm-smi (or mock in dev)."""
    gpu_utilization_percent: float = 0.0
    power_watts_avg: float = 0.0
    power_watts_peak: float = 0.0
    temperature_c: float = 0.0
    memory_used_mb: float = 0.0
    clock_sclk_mhz: float = 0.0
    clock_mclk_mhz: float = 0.0


class DerivedMetrics(BaseModel):
    """Derived efficiency numbers per the schema (real MI300X peaks)."""
    achieved_bw_gbs: Optional[float] = None
    theoretical_peak_gbs: float = 5300.0  # MI300X HBM3 reference — verify on instance
    efficiency_percent: Optional[float] = None

    achieved_tflops: Optional[float] = None
    theoretical_peak_tflops: float = 163.4  # FP32 reference — verify
    efficiency_tflops_percent: Optional[float] = None

    kernel_time_ms: float = 0.0
    bytes_moved: Optional[float] = None
    flops: Optional[float] = None


class JobMetrics(BaseModel):
    """Full metrics payload for a job (raw + derived + timeseries for sparklines)."""
    raw: RawMetrics = Field(default_factory=RawMetrics)
    derived: DerivedMetrics = Field(default_factory=DerivedMetrics)
    timeseries: list[dict[str, Any]] = Field(default_factory=list)  # [{t, util, power, temp, ...}]
    captured_at: datetime = Field(default_factory=datetime.utcnow)


class JobState(BaseModel):
    """Complete job record. Immutable updates preferred (create new or careful patch)."""
    job_id: str = Field(default_factory=lambda: f"job_{uuid4().hex[:12]}")
    seed_id: SeedId
    phase: JobPhase = JobPhase.QUEUED
    status: JobStatus = JobStatus.RUNNING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Execution trace (visible "agentic" even in baseline)
    messages: list[AgentMessage] = Field(default_factory=list)
    completed_phases: list[JobPhase] = Field(default_factory=list)

    # Results
    metrics: JobMetrics = Field(default_factory=JobMetrics)
    report_md_path: Optional[str] = None
    artifacts_tar_path: Optional[str] = None
    hip_out_dir: Optional[str] = None

    # Porting details (for report + replay)
    hipify_command: Optional[str] = None
    hipcc_command: Optional[str] = None
    repair_loops: int = 0

    # Validation
    validation_passed: Optional[bool] = None
    max_abs_diff: Optional[float] = None
    tolerance: float = 1e-5

    error: Optional[str] = None

    # Where the workspace lives on disk (absolute path on the instance)
    workspace_dir: Optional[str] = None


class CreateJobRequest(BaseModel):
    seed_id: SeedId
    # Future: allow limited source upload for non-seed cases
    # source_zip_b64: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    seed_id: SeedId
    phase: JobPhase
    status: JobStatus
    messages: list[AgentMessage]
    metrics: JobMetrics
    completed_phases: list[JobPhase]


class HealthResponse(BaseModel):
    status: str = "ok"
    rocm_available: bool
    gpu_name: Optional[str] = None
    rocm_version: Optional[str] = None
    vllm_reachable: bool = False  # Phase 2+
    timestamp: datetime = Field(default_factory=datetime.utcnow)
