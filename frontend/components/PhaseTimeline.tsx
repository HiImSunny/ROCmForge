"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";

const PHASES = [
  "Analysis",
  "Porting",
  "Validating",
  "Benchmarking",
  "Optimizing",
  "Reporting",
] as const;

type Phase = typeof PHASES[number];

interface PhaseTimelineProps {
  currentPhase: Phase;
  completedPhases: Phase[];
  status?: string;
}

export function PhaseTimeline({ currentPhase, completedPhases, status }: PhaseTimelineProps) {
  // Normalize possible backend phase names
  const normalize = (p: string) => {
    const map: Record<string, string> = {
      'Queued': 'Analysis',
      'Analysis': 'Analysis',
      'Porting': 'Porting',
      'Validating': 'Validating',
      'Benchmarking': 'Benchmarking',
      'Optimizing': 'Optimizing',
      'Reporting': 'Reporting',
      'Completed': 'Reporting',
    };
    return map[p] || p;
  };

  const normCurrent = normalize(currentPhase as any) as any;
  const normCompleted = completedPhases.map(normalize) as any;
  const isFailed = status === 'failed';

  return (
    <div className="surface p-5">
      <div className="text-xs font-medium text-text-secondary mb-4 tracking-[0.5px] uppercase flex items-center justify-between">
        <span>Swarm Execution Timeline</span>
        {isFailed && <span className="text-danger text-[10px] font-mono">STOPPED ON FAILURE</span>}
      </div>

      <div className="flex items-start justify-between relative">
        {PHASES.map((phase, index) => {
          const isActive = phase === currentPhase;
          const isCompleted = completedPhases.includes(phase);
          const isPast = PHASES.indexOf(phase) < PHASES.indexOf(currentPhase);

          return (
            <div key={phase} className="phase-step flex flex-col items-center flex-1">
              <div 
                className={`phase-dot mb-2 text-[10px] font-mono ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isActive && isFailed ? 'failed' : ''}`}
              >
                {isCompleted ? <Check className="w-3 h-3" /> : (index + 1).toString().padStart(2, '0')}
              </div>

              <div className={`text-[11px] font-medium text-center leading-tight max-w-[72px] ${isActive || isCompleted ? 'text-text-primary' : 'text-text-secondary'}`}>
                {phase}
              </div>

              {/* Subtle label for active */}
              {isActive && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-[10px] text-accent mt-0.5 font-mono"
                >
                  LIVE
                </motion.div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
