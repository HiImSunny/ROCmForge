# ROCmForge Frontend

Polished, non-slop custom Next.js dashboard for the ROCmForge multi-agent CUDA→ROCm system.

Built following:
- `make-interfaces-feel-better` principles for real polish
- `frontend-patterns` for maintainable, performant code
- Designed as a "mission control" for agent swarm + real MI300X hardware metrics

## Tech Stack (chosen for speed + quality in limited time)

- Next.js 15 (App Router) + TypeScript
- Tailwind CSS + shadcn/ui
- Framer Motion (deliberate, scoped animations)
- TanStack Query + SSE for live updates
- Recharts + custom components for data viz

## Running

(Backend FastAPI must be running on port 8001 with SSE at /jobs/{id}/stream)

```bash
npm install
npm run dev
```

Then visit http://localhost:3000

## Key Screens

See `spec/UI_DESIGN.md` for the full ambitious design spec.

## Anti-Slop Commitment

We explicitly apply the principles from the loaded skills on every component. No default library look, no random spacing, real attention to motion, typography, data visualization, and interaction details.

This frontend is meant to be one of the strongest parts of the submission — it should make the "genuine agentic + real high-performance on MI300X" story land hard with judges.