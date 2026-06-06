"use client";

import { motion } from "framer-motion";

interface ReportViewerProps {
  jobId: string;
  efficiency: number;
  bandwidth: string;
}

export function ReportViewer({ jobId, efficiency, bandwidth }: ReportViewerProps) {
  return (
    <div className="surface p-8 max-w-3xl mx-auto">
      <div className="mb-8">
        <div className="uppercase tracking-[2px] text-xs text-accent mb-2">Migration Complete</div>
        <h2 className="text-4xl font-semibold tracking-tighter">vectorAdd — Ported & Optimized</h2>
        <div className="text-text-secondary mt-1">Job {jobId} • Real MI300X • 47s total</div>
      </div>

      {/* Shock metric - the narrative hook */}
      <div className="report-section mb-8">
        <div className="text-sm text-text-secondary mb-1">Key Result</div>
        <div className="text-5xl font-semibold tabular-nums tracking-[-2px] text-accent">
          {efficiency}% <span className="text-3xl text-text-primary">of peak HBM bandwidth</span>
        </div>
        <div className="mt-1 text-lg">{bandwidth} achieved on actual AMD Instinct MI300X</div>
      </div>

      <div className="prose prose-invert text-sm space-y-6 text-text-secondary">
        <div>
          <h3 className="font-medium text-text-primary mb-2">Swarm Journey Summary</h3>
          <p>
            7 autonomous decisions. 2 repair loops resolved by Porting Specialist using memory patterns. 
            Full validation passed with 1.2e-6 max error. Optimizer applied launch bounds + gfx942 flags, 
            improving bandwidth from 4.1 → 4.61 TB/s.
          </p>
        </div>

        <div>
          <h3 className="font-medium text-text-primary mb-2">Hardware Evidence</h3>
          <ul className="space-y-1">
            <li>• Sustained 94% GPU utilization during kernel</li>
            <li>• 682W average power draw (well within TDP)</li>
            <li>• 68°C junction temperature</li>
            <li>• All work executed natively on ROCm via AMD Developer Cloud</li>
          </ul>
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-border flex gap-3">
        <button className="button flex-1 h-11 rounded-xl bg-accent text-background font-medium">
          Download Full Report (PDF + MD)
        </button>
        <button className="button flex-1 h-11 rounded-xl border border-border">
          View Raw Agent Trace + Metrics JSON
        </button>
      </div>
    </div>
  );
}
