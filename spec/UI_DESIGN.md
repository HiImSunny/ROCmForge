# ROCmForge — Polished UI Design Spec (Ambitious, Non-Slop)

**Goal**: A beautiful, professional, "control room" style dashboard that makes judges say "wow, this feels premium and actually shows the power of MI300X".

We are **not** using plain Gradio. We are building a custom Next.js frontend (App Router) that talks to the FastAPI backend. This is feasible in ~1 day of focused AI-assisted work because:
- We have clear specs (agents, metrics, flows).
- We will ruthlessly follow `make-interfaces-feel-better` + `frontend-patterns` principles to avoid slop.
- Scope to the core "WOW" experience: Live Job View + Metrics + Agent Feed + Report.

## Design Language (Applied from make-interfaces-feel-better)

**Theme**: Dark tech / mission control.
- Background: #0a0c10 (deep slate)
- Surface: #111418 with subtle #1a1f26 borders
- Accent: AMD-inspired green-teal (#00d4aa) for success/metrics, warm orange for warnings
- Text: #f1f5f9 primary, #94a3b8 secondary
- Use `font-variant-numeric: tabular-nums` everywhere numbers update
- Headings: `text-wrap: balance`
- Body: `text-wrap: pretty`

**Principles we will enforce in every component**:
- Concentric radius (parent radius = child + padding)
- Optical alignment for icons
- Layered subtle shadows + borders for depth (never flat)
- Explicit transition properties (never `transition: all`)
- Good hit areas (min 44px)
- Micro motion that feels tactile but not distracting
- Data visualization that highlights real MI300X power (big % efficiency numbers, live sparklines)

## Overall Layout (Dashboard Feel)

**Top Nav (persistent)**:
- Logo + "ROCmForge" (with small "on MI300X" badge)
- Live instance status: "AMD Instinct MI300X • ROCm X.Y • $100 credits remaining"
- User actions: "New Job" (dropdown with seeds), "Replay Demo", "Docs"

**Main Area**:
- Left sidebar (collapsible): Job queue + recent runs
- Center: Primary view (switches between Live View / Report View / Landing)
- Right panel (when in Live View): Real-time GPU Metrics + Agent Activity

This creates a "command center" feeling — perfect for showing off agent swarm + hardware.

## Key Screens & Components

### 1. Landing / Job Creation (Beautiful Hero + Seeds)

Not a boring list.

- Large hero with subtle animated background (very light GPU utilization particles or grid — using canvas or Framer, not heavy).
- Headline: "Autonomous CUDA → ROCm on Real MI300X"
- Sub: "Multi-agent swarm ports, validates, benchmarks and optimizes — all on actual AMD hardware."

**Seed Cards** (3 columns, premium feel):
Each card:
- Title + short description
- Key metric preview (e.g. "Target: 85%+ of 5.3 TB/s HBM")
- "Run on MI300X" button (primary, with nice active state)
- Subtle "View previous run" link

Use compound components + good hover (lift + border accent + scale micro).

### 2. Live Job View — The WOW Screen

This is the money shot.

**Header**:
- Job ID + Seed name + Status (with nice pill + color)
- Big "Elapsed" timer + "Current Phase"

**Main Split**:
- Left 60%: **Swarm Activity Feed**
  - Beautiful terminal-style but polished (not default black terminal).
  - Use monospace for agent thoughts, but with syntax colors for "Thought:", "Action:", "Observation:".
  - Each agent has distinct subtle color (e.g. Porting = teal, Validator = purple, Profiler = orange).
  - Auto-scroll with "Follow" toggle.
  - When a patch is applied, show a small diff snippet that animates in.
  - Use Framer Motion for enter/exit of new lines.

- Right 40%: **Live GPU Metrics** (this screams "high-performance on real AMD")
  - 4 big metric cards in 2x2:
    - GPU Utilization %
    - Power (W) with current vs peak
    - Memory Bandwidth achieved (GB/s) + % of 5.3 TB/s
    - Temperature + Clocks
  - Each card has a live sparkline (small area chart, updating via SSE).
  - When benchmark phase is active, the cards "pulse" subtly and show "LIVE" badge.
  - Big centered number for the most important metric in the current phase (e.g. "Achieved BW: 4.61 TB/s (87%)").

**Bottom**:
- **Phase Timeline** (horizontal stepper, beautiful):
  Analysis → Porting (with live repair count) → Validating → Benchmarking → Optimizing → Reporting
  Active phase is highlighted with accent color + progress.

- File Progress (if relevant): Simple but nice list of files being processed with checkmarks/ spinners.

### 3. Report Viewer

When job completes, big success state with the shock metric.

Then a clean, readable report view:
- Use good typography (not default prose).
- Embedded beautiful metrics table (with color-coded efficiency % — green for high).
- "How the swarm decided" section with highlighted agent traces.
- One-click downloads for everything.

### 4. Demo Replay Mode

From landing, big "Watch Replay" buttons for each seed.
- When clicked, it loads a "completed" version of the Live View using cached data + fast re-benchmark (only metrics update live).
- This gives judges instant gratification while still showing real hardware numbers.

## Technical Stack for Frontend (Fast + High Quality)

- Next.js 15 (App Router) + TypeScript
- Tailwind + shadcn/ui (base components)
- Framer Motion (all animations — follow explicit transition patterns)
- TanStack Query (for jobs)
- Recharts or custom SVG + Framer for sparklines and charts (we will make them look custom, not library-default)
- SSE client for live updates from `/jobs/{id}/stream`

**Why this stack allows "1 day" ambitious UI**:
- shadcn gives beautiful base without design time.
- We will apply `make-interfaces-feel-better` rules explicitly while building each component.
- SSE + React is straightforward for live feed + metrics.
- We can generate most components quickly with the AI + the patterns we loaded.

## Anti-Slop Rules (We Will Follow These)

- No default library styles without heavy customization.
- Every interactive element has thoughtful active/hover/focus states.
- Numbers that change use `tabular-nums` and smooth transitions where appropriate.
- The agent feed must feel alive and intelligent, not like a log dump.
- GPU metrics must feel like they come from real powerful hardware (big numbers, live updates, context like "% of MI300X peak").
- Consistent spacing, no random padding.
- Good empty/loading states (especially for first-time judges).

## Implementation Order (for 1-day push)

1. Project setup + layout + theme + design tokens
2. Landing + beautiful seed cards
3. Live View skeleton + Agent Feed component (most important for agentic feel)
4. Live GPU Metrics + sparklines (most important for AMD performance feel)
5. Phase timeline + success states
6. Report viewer + replay mode
7. Polish pass using make-interfaces-feel-better checklist

We will review every major component against the principles before moving on.

This UI will make the project feel like a real tool, not a hackathon prototype. It will strongly support the "Application of Technology" and "Presentation" judging criteria.

---

Next: I will generate the full Next.js frontend structure + key components following this spec + the loaded skills.