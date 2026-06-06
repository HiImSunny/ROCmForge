"use client";

import { useEffect, useState } from "react";
import { AgentFeed } from "./AgentFeed";
import { MetricsDashboard } from "./MetricsDashboard";
import { PhaseTimeline } from "./PhaseTimeline";
import { getJobStatus, getReport, getArtifactsUrl } from "@/lib/api";
import { toast } from "sonner";

interface LiveJobViewProps {
  jobId: string;
  isReplay: boolean;
  onClose: () => void;
}

interface JobData {
  seed_id: string;
  phase: string;
  status: string;
  messages: any[];
  metrics: any;
  completed_phases: string[];
}

export function LiveJobView({ jobId, isReplay, onClose }: LiveJobViewProps) {
  const [jobData, setJobData] = useState<JobData | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);

  // Poll status + listen to SSE for live updates
  useEffect(() => {
    if (isReplay) return;

    let es: EventSource | null = null;
    let pollInterval: any = null;

    const fetchStatus = async () => {
      try {
        const data = await getJobStatus(jobId);
        setJobData({
          seed_id: data.seed_id,
          phase: data.phase,
          status: data.status,
          messages: data.messages,
          metrics: data.metrics,
          completed_phases: data.completed_phases,
        });
      } catch (e) {
        // keep previous data
      }
    };

    // Initial fetch
    fetchStatus();

    // Try real SSE (improved backend sends "update" events with full snapshot)
    try {
      es = new EventSource(getStreamUrlFromJobId(jobId));
      es.addEventListener('update', (event) => {
        try {
          const data = JSON.parse(event.data);
          setJobData({
            seed_id: data.seed_id,
            phase: data.phase,
            status: data.status,
            messages: data.messages,
            metrics: data.metrics,
            completed_phases: data.completed_phases,
          });
        } catch {}
      });
      es.addEventListener('done', () => {
        fetchStatus(); // final sync
      });
      es.onerror = () => {
        if (es) es.close();
        es = null;
      };
    } catch {}

    // Fallback polling every 1.2s
    pollInterval = setInterval(fetchStatus, 1200);

    return () => {
      if (es) es.close();
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [jobId, isReplay]);

  const currentPhase = (jobData?.phase || "Benchmarking") as any;
  const completedPhases = jobData?.completed_phases || ["Analysis", "Porting", "Validating"];
  const seedName = jobData?.seed_id || "vectorAdd";

  const handleDownload = async () => {
    if (isReplay) {
      toast.info("Replay mode — artifacts would be served from pre-captured run on real MI300X");
      return;
    }
    setLoadingReport(true);
    try {
      const { markdown } = await getReport(jobId);
      // Simple download of the markdown report
      const blob = new Blob([markdown], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `migration_report_${jobId}.md`;
      a.click();
      URL.revokeObjectURL(url);

      // Also trigger artifacts tar in new tab
      window.open(getArtifactsUrl(jobId), "_blank");
    } catch (e) {
      toast.error("Could not download report (backend may still be working or not connected)");
    } finally {
      setLoadingReport(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="px-3 py-1 rounded-full bg-accent/10 text-accent text-xs font-medium tracking-wide">
              {isReplay ? "REPLAY" : "LIVE"} • REAL MI300X
            </div>
            <div className="font-mono text-sm text-text-secondary">{jobId}</div>
          </div>
          <h2 className="text-3xl font-semibold tracking-tighter mt-1">{seedName} seed</h2>
          <p className="text-text-secondary text-sm mt-1">Autonomous port + benchmark on AMD Instinct MI300X</p>
        </div>

        <button 
          onClick={onClose}
          className="button px-5 py-2 text-sm border border-border rounded-xl hover:bg-surface-2 transition-colors"
        >
          Exit View
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Agent Feed - the "genuine agentic" proof */}
        <div className="xl:col-span-7">
          <AgentFeed jobId={jobId} isReplay={isReplay} realMessages={jobData?.messages} />
        </div>

        {/* Metrics - the "real high-performance on AMD" proof */}
        <div className="xl:col-span-5">
          <MetricsDashboard jobId={jobId} isReplay={isReplay} realMetrics={jobData?.metrics} />
        </div>
      </div>

      {/* Phase Timeline - visual proof of swarm progress */}
      <PhaseTimeline 
        currentPhase={currentPhase} 
        completedPhases={completedPhases as any} 
      />

      {/* Bottom actions */}
      <div className="flex gap-3 pt-2">
        <button 
          onClick={handleDownload}
          disabled={loadingReport}
          className="flex-1 h-12 rounded-2xl bg-accent text-background font-medium flex items-center justify-center gap-2 active:scale-[0.985] transition-transform disabled:opacity-60"
        >
          {loadingReport ? "Preparing..." : "Download Migration Report + Artifacts"}
        </button>
        <button 
          onClick={() => {
            if (jobData?.metrics) {
              const json = JSON.stringify(jobData.metrics, null, 2);
              const blob = new Blob([json], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `metrics_${jobId}.json`;
              a.click();
              URL.revokeObjectURL(url);
            } else {
              toast.info("No metrics yet");
            }
          }}
          className="h-12 px-8 rounded-2xl border border-border font-medium flex items-center justify-center gap-2 hover:bg-surface-2 transition-colors"
        >
          View Raw Metrics JSON
        </button>
      </div>
    </div>
  );
}

// Helper to build stream url (we import from lib/api in real usage, but keep simple here)
function getStreamUrlFromJobId(jobId: string) {
  const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return `${base}/jobs/${jobId}/stream`;
}

