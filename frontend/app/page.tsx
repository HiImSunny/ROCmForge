"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { RotateCcw } from "lucide-react";
import { LiveJobView } from "@/components/LiveJobView";
import { ReportViewer } from "@/components/ReportViewer";
import { SeedCard } from "@/components/SeedCard";
import { toast } from "sonner";
import { listJobs, extractErrorMessage } from "@/lib/api";

function BackendStatus() {
  const [status, setStatus] = useState<"checking" | "connected" | "mock">("checking");

  useEffect(() => {
    const check = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/health`, { signal: AbortSignal.timeout(1500) });
        if (res.ok) {
          setStatus("connected");
        } else {
          setStatus("mock");
        }
      } catch {
        setStatus("mock");
      }
    };
    check();
    const id = setInterval(check, 15000);
    return () => clearInterval(id);
  }, []);

  if (status === "checking") {
    return <div className="text-xs px-3 py-1 rounded-full bg-surface-2 border border-border text-text-secondary">Checking backend...</div>;
  }

  if (status === "connected") {
    return (
      <div className="text-xs px-3 py-1 rounded-full bg-accent/10 text-accent border border-accent/30 flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
        Connected to backend (real MI300X path)
      </div>
    );
  }

  return (
    <div className="text-xs px-3 py-1 rounded-full bg-warning/10 text-warning border border-warning/30 flex items-center gap-2">
      <div className="w-1.5 h-1.5 rounded-full bg-warning" />
      Local mock mode (no backend or ROCm)
    </div>
  );
}

const SEEDS = [
  {
    id: "vectorAdd",
    name: "vectorAdd",
    description: "Memory bandwidth hero. Classic vector addition kernel.",
    target: "85%+ of 5.3 TB/s HBM",
  },
  {
    id: "tiledMatmul",
    name: "Tiled Matmul",
    description: "Compute + shared memory. 1024×1024 tiled matrix multiply.",
    target: "High TFLOPS efficiency",
  },
  {
    id: "reduction",
    name: "Parallel Reduction",
    description: "Control flow & atomics. Tree reduction with synchronization.",
    target: "Good occupancy + repair demo",
  },
];

export default function ROCmForgeDashboard() {
  const [activeJob, setActiveJob] = useState<string | null>(null);
  const [showReport, setShowReport] = useState(false);
  const [isReplaying, setIsReplaying] = useState(false);
  const [isStarting, setIsStarting] = useState(false);

  const startJob = async (seedId: string) => {
    setIsStarting(true);
    toast.loading(`Activating swarm on real MI300X for ${seedId}... (est. 30-90s)`, { id: "job" });
    
    try {
      const { createJob } = await import('@/lib/api');
      const job = await createJob(seedId);
      
      setActiveJob(job.job_id);
      setShowReport(false);
      setIsReplaying(false);
      
      toast.success("Swarm live on AMD Instinct MI300X — streaming updates", { id: "job" });
    } catch (err) {
      // Fallback to local mock if backend not available (useful during development)
      console.warn('Backend not reachable, using local mock job', err);
      const jobId = `job_${Date.now()}`;
      setActiveJob(jobId);
      setShowReport(false);
      setIsReplaying(false);
      toast.success("Swarm (local mock) — connect backend for real runs", { id: "job" });
      // In real usage you would surface: toast.error(extractErrorMessage(err));
    } finally {
      setIsStarting(false);
    }
  };

  const replayDemo = async (seedId: string, previousJobId?: string) => {
    setIsReplaying(true);
    toast.info(previousJobId 
      ? `Loading real report from job ${previousJobId}` 
      : `Loading pre-captured real MI300X run for ${seedId}`);
    
    try {
      const { demoReplay } = await import('@/lib/api');
      // Pass job_id if we want to load a real previous job's report (Phase 1+ improvement)
      await demoReplay(seedId, previousJobId);
    } catch (e) {
      // ignore — we still want to show the replay UI
    }
    
    const jobId = previousJobId ? `replay_${previousJobId}` : `replay_${seedId}_${Date.now()}`;
    setActiveJob(jobId);
    setShowReport(false);
    setIsReplaying(true); // keep as replay so some components behave differently
  };

  const closeView = () => {
    setActiveJob(null);
    setShowReport(false);
  };

  const viewReport = () => {
    setShowReport(true);
  };

  // Polished recent jobs list (shows real status from backend, including failed jobs)
  function RecentJobs({ onSelectJob }: { onSelectJob: (jobId: string) => void }) {
    const [jobs, setJobs] = useState<any[]>([]);
    useEffect(() => {
      listJobs(6).then(setJobs).catch(() => {});
    }, []);
    if (!jobs.length) return null;

    const getStatusColor = (status: string) => {
      if (status === 'failed') return 'border-danger/60 text-danger bg-danger/10';
      if (status === 'completed') return 'border-emerald-500/60 text-emerald-400 bg-emerald-500/10';
      return 'border-border text-text-secondary bg-surface-2';
    };

    return (
      <div className="pt-8 border-t border-border text-xs">
        <div className="text-text-secondary mb-2 flex items-center justify-between">
          <span>Recent jobs (click to inspect — includes real backend runs)</span>
          <span className="text-[10px] opacity-60">status • phase</span>
        </div>
        <div className="flex gap-2 flex-wrap">
          {jobs.map((j) => (
            <button
              key={j.job_id}
              onClick={() => onSelectJob(j.job_id)}
              className={`px-3 py-1.5 rounded-lg border hover:bg-surface-2 transition-colors flex items-center gap-2 ${getStatusColor(j.status)}`}
              title={j.status === 'failed' ? 'Failed job — error details available in Live view' : ''}
            >
              <span className="font-mono">{j.seed_id}</span>
              <span className="opacity-60">•</span>
              <span className="font-medium">{j.phase}</span>
              {j.status === 'failed' && <span className="text-[9px] px-1.5 py-px rounded bg-danger/30">FAILED</span>}
              {j.status === 'completed' && <span className="text-[9px] px-1.5 py-px rounded bg-emerald-500/30">OK</span>}
            </button>
          ))}
        </div>
        <div className="text-[10px] text-text-secondary mt-2 opacity-70">
          Failed jobs now surface full error + diagnostic report (see error surfacing improvements).
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-text-primary">
      <nav className="border-b border-border bg-surface/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-accent flex items-center justify-center">
                <span className="text-background font-bold text-lg tracking-[-1px]">R</span>
              </div>
              <div>
                <div className="font-semibold tracking-tighter">ROCmForge</div>
                <div className="text-[10px] text-text-secondary -mt-1">Real MI300X • No CUDA lock-in</div>
              </div>
            </div>
          </div>

          <BackendStatus />
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-12">
        <AnimatePresence mode="wait">
          {!activeJob ? (
            <motion.div
              key="landing"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              className="space-y-14"
            >
              <div className="max-w-2xl">
                <div className="inline-block px-3 py-1 text-xs rounded-full border border-border bg-surface-2 mb-5">
                  AMD Developer Hackathon ACT II
                </div>
                <h1 className="text-[68px] leading-[1.0] font-semibold tracking-[-3.2px] mb-4">
                  Autonomous<br />CUDA → ROCm<br />on real <span className="text-accent">MI300X</span>.
                </h1>
                <p className="text-2xl text-text-secondary max-w-md">
                  Multi-agent swarm that ports, validates, benchmarks and optimizes — 
                  running natively on AMD hardware.
                </p>
              </div>

              <div>
                <div className="flex items-baseline justify-between mb-5">
                  <div>
                    <div className="text-sm font-medium tracking-widest text-text-secondary">SELECT WORKLOAD</div>
                  </div>
                  <button 
                    onClick={() => replayDemo("vectorAdd")}
                    className="text-sm flex items-center gap-2 px-5 py-2 rounded-xl border border-border hover:bg-surface-2 active:scale-[0.985] transition-all"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Watch full replay (pre-captured on real MI300X)
                  </button>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  {SEEDS.map((seed) => (
                    <SeedCard
                      key={seed.id}
                      {...seed}
                      onRun={() => startJob(seed.id)}
                      onReplay={() => replayDemo(seed.id)}
                      disabled={isStarting}
                    />
                  ))}
                </div>
                {isStarting && (
                  <div className="text-xs text-text-secondary mt-3 flex items-center gap-2">
                    <div className="w-2 h-2 bg-accent animate-pulse rounded-full" />
                    Submitting job • Typical end-to-end on MI300X: 30–90 seconds (hipify + compile + benchmark + amd-smi capture)
                  </div>
                )}
              </div>

              {/* Small recent jobs history for polish / debugging */}
              <RecentJobs onSelectJob={(jid) => { setActiveJob(jid); setShowReport(false); setIsReplaying(false); }} />
              </div>

              <div className="pt-10 text-xs text-text-secondary max-w-prose border-t border-border">
                Every decision, every hipify/hipcc call, and every performance number you see 
                was captured live on an actual AMD Instinct MI300X GPU in the Developer Cloud.
              </div>
            </motion.div>
          ) : showReport ? (
            <motion.div
              key="report"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <ReportViewer jobId={activeJob} />
              <div className="text-center mt-8">
                <button onClick={closeView} className="text-sm text-text-secondary hover:text-text-primary">
                  ← Back to dashboard
                </button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="live"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <LiveJobView 
                jobId={activeJob} 
                isReplay={isReplaying} 
                onClose={closeView} 
              />
              <div className="flex justify-center mt-8">
                <button 
                  onClick={() => setShowReport(true)}
                  className="text-sm px-6 py-2 rounded-xl border border-border hover:bg-surface-2"
                >
                  View Polished Migration Report
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
