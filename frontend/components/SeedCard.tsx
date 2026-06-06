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
}

export function SeedCard({ name, description, target, onRun, onReplay }: SeedCardProps) {
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
          className="button flex-1 flex items-center justify-center gap-2 bg-accent text-background py-2.5 rounded-xl font-medium text-sm active:scale-[0.985] transition-all"
        >
          <Play className="w-4 h-4" />
          Run on MI300X
        </button>
        <button
          onClick={onReplay}
          className="button px-4 border border-border rounded-xl text-sm flex items-center justify-center hover:bg-surface-2 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}
