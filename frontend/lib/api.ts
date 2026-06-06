// frontend/lib/api.ts
// Simple API client for ROCmForge backend.
// Configure with NEXT_PUBLIC_API_URL (defaults to http://localhost:8000 for local dev)

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CreateJobResponse {
  job_id: string;
  seed_id: string;
  phase: string;
  status: string;
  messages: Array<{
    id: number;
    agent: string;
    timestamp: string;
    type: 'thought' | 'action' | 'observation';
    content: string;
  }>;
  metrics: any;
  completed_phases: string[];
  duration_seconds?: number | null;
  error?: string | null;   // populated on hipify/hipcc/run failures for UI banners
}

// Simple retry with exponential backoff (good for unstable cloud instance connections)
async function fetchWithRetry(url: string, options: RequestInit = {}, retries = 3): Promise<Response> {
  let lastError: Error | null = null;

  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(url, options);
      if (res.ok || i === retries - 1) return res; // return even on last error
      // Only retry on network / 5xx
      if (res.status < 500) return res;
    } catch (err) {
      lastError = err as Error;
    }
    // Exponential backoff: 300ms, 600ms, 1200ms...
    const delay = 300 * Math.pow(2, i);
    await new Promise((r) => setTimeout(r, delay));
  }
  throw lastError || new Error('Failed after retries');
}

export async function createJob(seedId: string): Promise<CreateJobResponse> {
  const res = await fetchWithRetry(`${API_BASE}/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ seed_id: seedId }),
  });
  if (!res.ok) throw new Error(`Failed to create job: ${res.statusText}`);
  return res.json();
}

export async function getJobStatus(jobId: string): Promise<CreateJobResponse> {
  const res = await fetchWithRetry(`${API_BASE}/jobs/${jobId}/status`);
  if (!res.ok) throw new Error(`Failed to get job status`);
  return res.json();
}

export async function getReport(jobId: string): Promise<{ job_id: string; markdown: string }> {
  const res = await fetchWithRetry(`${API_BASE}/jobs/${jobId}/report`);
  if (!res.ok) throw new Error(`Failed to get report`);
  return res.json();
}

export function getArtifactsUrl(jobId: string): string {
  return `${API_BASE}/jobs/${jobId}/artifacts`;
}

export function getStreamUrl(jobId: string): string {
  return `${API_BASE}/jobs/${jobId}/stream`;
}

// Demo endpoints (useful for judges even before full wiring)
export async function demoReplay(seedId: string) {
  const res = await fetchWithRetry(`${API_BASE}/demo/replay?seed_id=${seedId}`, { method: 'POST' });
  return res.json();
}

export async function listJobs(limit = 10) {
  const res = await fetchWithRetry(`${API_BASE}/jobs?limit=${limit}`);
  if (!res.ok) return [];
  return res.json();
}

// For better error display in UI
export function extractErrorMessage(error: any): string {
  if (error?.message) return error.message;
  return 'Unknown error occurred. Check backend logs.';
}
