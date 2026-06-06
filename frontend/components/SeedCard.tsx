"use client";

import { motion } from "framer-motion";
import { Play, RotateCcw } from "lucide-react";

interface SeedCardProps {
  id: string;
  name: string;
  description: string;
  target: string;
  onRun: () => void;
  onReplay: () => void;
  disabled?: boolean;
}

export function SeedCard({ name, description, target, onRun, onReplay, disabled = false }: SeedCardProps) {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="group surface p-6 flex flex-col"
    >
      <div className="flex-1">
        <div className="font-semibold text-lg tracking-tight mb-1.5">{name}</div>
        <p className="text-text-secondary text-sm leading-relaxed mb-4">
          {description}
        </p>
        <div className="text-xs text-accent font-medium tabular-nums">{target}</div>
      </div>

      <div className="flex gap-2 mt-6">
        <button
          onClick={onRun}
          disabled={disabled}
          className="button flex-1 flex items-center justify-center gap-2 bg-accent text-background py-2.5 rounded-xl font-medium text-sm active:scale-[0.985] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="w-4 h-4" />
          Run on MI300X
        </button>
        <button
          onClick={onReplay}
          disabled={disabled}
          className="button px-4 border border-border rounded-xl text-sm flex items-center justify-center hover:bg-surface-2 transition-colors disabled:opacity-50"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}
