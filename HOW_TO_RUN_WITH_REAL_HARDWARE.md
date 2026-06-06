# How to run ROCmForge with real AMD MI300X (plug-and-play)

## 1. On your development machine (this repo)

Everything below the "backend + frontend wiring" can be developed and tested locally using mock mode.

```bash
# Terminal 1 - Backend (mock)
cd "D:\Code Project\Python Coding\Lablab.ai Hackathon\AMD Developer Hackathon ACT II"
$env:ROCFORGE_MOCK='1'
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Then in the UI you can submit seeds. It will try to talk to localhost:8000. If the backend is not running it falls back to local mock.

## 2. On the real MI300X instance (the important part)

After you launch the instance via AMD Developer Cloud credits:

```bash
# 1. Get the code on the instance (git or scp the whole folder)
git clone <your-repo> rocmforge
cd rocmforge

# 2. (Recommended) Use Docker Compose (easiest + production signal)
# This is the preferred way on the MI300X instance.

docker compose up -d --build

# Then check:
curl http://localhost:8000/health

# 3. (Alternative — single container, no compose)
docker build -f Dockerfile.backend -t rocmforge-backend .
docker run -d \
  --name rocmforge \
  --device=/dev/kfd --device=/dev/dri --group-add video \
  --shm-size 16g \
  -p 8000:8000 \
  -e ROCFORGE_MOCK=0 \
  rocmforge-backend

# 4. (Pure Python, if you have full ROCm in the host environment)
pip install -r requirements.txt
ROCFORGE_MOCK=0 python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 3. Point the frontend at the real backend

In the frontend you can set:

```bash
# In frontend/.env.local (or when building for production)
NEXT_PUBLIC_API_URL=http://<your-mi300x-public-ip-or-domain>:8000
```

Then rebuild/start the Next.js app (or serve the static build in front of the backend).

## 5. Verify it is really using ROCm (Day 0 + first real run)

On the instance (after `docker compose up` or direct Python):

```bash
# Day 0 hardware verification (mandatory first step)
python scripts/day0_verify.py

# Full end-to-end baseline on real MI300X (the important one)
ROCFORGE_MOCK=0 python scripts/test_baseline.py vectorAdd

# Or via API / demo
curl -X POST "http://localhost:8000/demo/seed?seed_id=vectorAdd"
curl "http://localhost:8000/jobs/<job_id>/status"
curl "http://localhost:8000/jobs/<job_id>/report"
```

You should see **real** `amd-smi` output, real hipcc/hipify logs, and real performance numbers (e.g. high % of 5.3 TB/s) in the generated `migration_report.md`.

## 6. For judges (90-second verification)

Use the dedicated `JUDGING.md` file at the repo root. It contains:

- Exact copy-paste commands for both mock (immediate) and real MI300X.
- Health check, demo/seed, demo/replay.
- What success looks like.
- Links to evidence locations.

Also see `track/SUBMISSION_CHECKLIST.md`.

---

This setup was intentionally designed so that the only thing that changes between "local beautiful demo" and "real MI300X submission evidence" is:
- Setting `ROCFORGE_MOCK=0`
- Pointing the frontend at the real backend URL
- Running on hardware that has hipify + hipcc + amd-smi in PATH (via `docker compose` or direct)

**New production artifacts** (added for Phase 1 readiness):
- `docker-compose.yml` — one-command `docker compose up -d --build`
- `JUDGING.md` — the 90-second judge verification bible

No code changes should be needed in the core pipeline once the real hardware is available.

After your first successful real run on MI300X, update `track/DAY0_HARDWARE_VERIFICATION.md` + `track/DAILY_LOG.md` with the actual numbers and screenshots.
