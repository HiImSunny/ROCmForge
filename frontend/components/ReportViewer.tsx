"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { getReport, getArtifactsUrl } from "@/lib/api";
import { toast } from "sonner";

interface ReportViewerProps {
  jobId: string;
  // Optional pre-fetched data for replay / when parent already has it
  initialMarkdown?: string;
}

export function ReportViewer({ jobId, initialMarkdown }: ReportViewerProps) {
  const [markdown, setMarkdown] = useState<string | null>(initialMarkdown || null);
  const [loading, setLoading] = useState(!initialMarkdown);

  useEffect(() => {
    if (initialMarkdown) {
      setMarkdown(initialMarkdown);
      return;
    }

    const fetchReport = async () => {
      setLoading(true);
      try {
        const { markdown: md } = await getReport(jobId);
        setMarkdown(md);
      } catch (e) {
        toast.error("Could not load report from backend. Using fallback.");
        // Fallback to a minimal nice message
        setMarkdown(`# ROCmForge Migration Report — ${jobId}\n\nReport is being generated or backend is not reachable.\n\nPlease use the Download button or check the backend logs.`);
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [jobId, initialMarkdown]);

  const handleDownload = () => {
    if (markdown) {
      const blob = new Blob([markdown], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `migration_report_${jobId}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
    // Also open artifacts
    window.open(getArtifactsUrl(jobId), "_blank");
  };

  if (loading) {
    return (
      <div className="surface p-8 max-w-3xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-6 w-1/3 bg-surface-2 rounded" />
          <div className="h-10 w-2/3 bg-surface-2 rounded" />
          <div className="h-4 w-full bg-surface-2 rounded" />
          <div className="h-4 w-5/6 bg-surface-2 rounded" />
        </div>
      </div>
    );
  }

  const isFailureReport = markdown?.includes('**FAILED**') || markdown?.toLowerCase().includes('execution failed') || markdown?.toLowerCase().includes('hipcc failed');

  return (
    <div className="surface p-8 max-w-3xl mx-auto">
      <div className="mb-8">
        {isFailureReport ? (
          <>
            <div className="uppercase tracking-[2px] text-xs text-danger mb-2">DIAGNOSTIC REPORT — PARTIAL / FAILED RUN</div>
            <h2 className="text-4xl font-semibold tracking-tighter text-danger">Report for job {jobId}</h2>
            <div className="text-text-secondary mt-1">Contains failure details + migration guidance (see Migration Notes section)</div>
          </>
        ) : (
          <>
            <div className="uppercase tracking-[2px] text-xs text-accent mb-2">Migration Complete</div>
            <h2 className="text-4xl font-semibold tracking-tighter">Report for job {jobId}</h2>
            <div className="text-text-secondary mt-1">Real MI300X • Captured on hardware</div>
          </>
        )}
      </div>

      {/* Render the real (or fallback) markdown report beautifully */}
      <div className="prose prose-invert prose-sm max-w-none bg-surface-2 p-6 rounded-xl border border-border text-text-secondary leading-relaxed">
        {markdown ? (
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                return (
                  <code className={`${className} bg-surface px-1 py-0.5 rounded font-mono text-xs`} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {markdown}
          </ReactMarkdown>
        ) : (
          "No report content available yet."
        )}
      </div>

      <div className="mt-8 pt-6 border-t border-border flex gap-3">
        <button 
          onClick={handleDownload}
          className="button flex-1 h-11 rounded-xl bg-accent text-background font-medium"
        >
          Download Full Report (MD) + Artifacts Tar
        </button>
        <button 
          onClick={() => {
            if (markdown) {
              navigator.clipboard.writeText(markdown);
              toast.success("Report markdown copied to clipboard");
            }
          }}
          className="button flex-1 h-11 rounded-xl border border-border"
        >
          Copy Report to Clipboard
        </button>
      </div>
    </div>
  );
}
