"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface AgentMessage {
  id: number;
  agent: string;
  timestamp: string;
  type: "thought" | "action" | "observation";
  content: string;
}

const MOCK_AGENT_LOGS: AgentMessage[] = [
  { id: 1, agent: "Orchestrator", timestamp: "14:32:04", type: "thought", content: "Received vectorAdd seed. Creating execution plan..." },
  { id: 2, agent: "Analyzer", timestamp: "14:32:06", type: "action", content: "Scanning cuda_src/vectorAdd.cu — detected 1 kernel, simple memcpy pattern." },
  { id: 3, agent: "Porting Specialist", timestamp: "14:32:08", type: "action", content: "Running hipify-clang..." },
  { id: 4, agent: "Porting Specialist", timestamp: "14:32:11", type: "observation", content: "hipify succeeded on 4/5 files. hipcc failed: unknown identifier 'cudaLaunchKernel'." },
  { id: 5, agent: "Porting Specialist", timestamp: "14:32:13", type: "thought", content: "Common pattern. Applying targeted fix from memory (launch bounds + hipLaunchKernel)." },
  { id: 6, agent: "Porting Specialist", timestamp: "14:32:15", type: "action", content: "Applied patch. Re-compiling..." },
  { id: 7, agent: "Porting Specialist", timestamp: "14:32:17", type: "observation", content: "hipcc succeeded cleanly on gfx942." },
];

export function AgentFeed({ 
  jobId, 
  isReplay, 
  realMessages 
}: { 
  jobId: string; 
  isReplay: boolean; 
  realMessages?: AgentMessage[];
}) {
  const [messages, setMessages] = useState<AgentMessage[]>(isReplay ? MOCK_AGENT_LOGS : []);
  const feedRef = useRef<HTMLDivElement>(null);

  // Use real messages from backend when available
  useEffect(() => {
    if (realMessages && realMessages.length > 0) {
      setMessages(realMessages);
      return;
    }
    if (isReplay) return;

    // Fallback local simulation if no real data yet
    const interval = setInterval(() => {
      if (messages.length < MOCK_AGENT_LOGS.length) {
        setMessages(prev => [...prev, MOCK_AGENT_LOGS[prev.length]]);
      }
    }, 650);

    return () => clearInterval(interval);
  }, [realMessages, isReplay, messages.length]);

  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [messages]);

  const getAgentColor = (agent: string) => {
    if (agent.includes("Porting")) return "agent-porting";
    if (agent.includes("Validator")) return "agent-validator";
    if (agent.includes("Profiler")) return "agent-profiler";
    return "text-text-secondary";
  };

  return (
    <div className="surface p-6 h-[520px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="font-medium">Swarm Activity</div>
          <div className="text-xs text-text-secondary">Live agent decisions on MI300X</div>
        </div>
        <div className="text-xs px-2 py-0.5 rounded bg-surface-2 border border-border tabular-nums">
          {messages.length} decisions
        </div>
      </div>

      <div 
        ref={feedRef}
        className="agent-feed flex-1 overflow-auto pr-2 space-y-1.5 text-[13px] leading-relaxed"
      >
        <AnimatePresence>
          {messages.map((msg, index) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.03 }}
              className="flex gap-3 group"
            >
              <div className="w-[72px] shrink-0 font-mono text-[11px] text-text-secondary pt-0.5 tabular-nums">
                {msg.timestamp}
              </div>
              <div className="flex-1 min-w-0">
                <span className={`font-medium ${getAgentColor(msg.agent)}`}>{msg.agent}</span>
                <span className="text-text-secondary"> — </span>
                <span className={
                  (msg.content.toLowerCase().includes('fail') || msg.content.toLowerCase().includes('error')) 
                    ? 'text-danger/90 font-medium' 
                    : msg.type === "thought" ? "agent-thought" : 
                      msg.type === "action" ? "agent-action" : "agent-observation"
                }>
                  {msg.content}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {messages.length === 0 && (
          <div className="text-text-secondary text-sm pt-8">Waiting for swarm to activate...</div>
        )}
      </div>
    </div>
  );
}
