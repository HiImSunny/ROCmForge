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

# 2. (Recommended) Use Docker with proper device passthrough
docker build -f Dockerfile.backend -t rocmforge-backend .

docker run -d \
  --name rocmforge \
  --device=/dev/kfd --device=/dev/dri --group-add video \
  --shm-size 16g \
  -p 8000:8000 \
  -e ROCFORGE_MOCK=0 \
  rocmforge-backend

# 3. (Alternative without Docker - if you have the full ROCm env)
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

## 4. Verify it is really using ROCm

Run on the instance:
```bash
python scripts/day0_verify.py
python scripts/test_baseline.py vectorAdd
```

You should see real `amd-smi`, real `hipcc --version`, and real performance numbers in the generated reports.

## 5. For judges (demo mode)

Even if the full swarm is heavy, the `/demo/seed` and `/demo/replay` endpoints + pre-captured reports under `jobs/` allow fast verification.

See `track/SUBMISSION_CHECKLIST.md` and `JUDGING.md` (to be created) for the <90s copy-paste path.

---

This setup was intentionally designed so that the only thing that changes between "local beautiful demo" and "real MI300X submission evidence" is:
- Setting `ROCFORGE_MOCK=0`
- Pointing the frontend at the real backend URL
- Running on hardware that has hipify + hipcc + amd-smi in PATH

No code changes should be needed in the core pipeline once the real hardware is available.
