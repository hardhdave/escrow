# Escrow Dex API

Production-oriented FastAPI scaffold for an escrow-based freelance platform.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
uvicorn app.main:app --reload
```

## Frontend

A top-level Next.js frontend lives in [`frontend`](./frontend).

```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` to your FastAPI base URL, for example `http://127.0.0.1:8001/v1`.

## Suggested local setup

- Backend: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8001`
- Frontend: `npm run dev` inside `frontend`
