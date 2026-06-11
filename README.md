# Salary Management

Web-based salary management for an organization with ~10,000 employees across
multiple countries. Lets an HR manager manage employee salary data and answer
org-wide questions about how the org pays people (totals, medians, by-country
comparisons in a common currency, and pay distribution by level).

Built as an assessment; see `docs/` for the thinking behind it.

## Demo

📹 **[Watch the demo video](https://drive.google.com/file/d/1LRM6vdeSp18t5Q_QI0gui4brJKCz9xvr/view)** — a short walkthrough of the app.

## Run it

One command brings up the whole stack (backend + frontend) with Docker:

```bash
docker compose up --build
```

Then open http://localhost:5173 (app) and http://localhost:8000/docs (API).
See [Quick start](#quick-start-docker--runs-everything) for details.

## Status

- **Backend — complete.** FastAPI + SQLAlchemy, employee CRUD, reference data,
  full analytics (summary, by-country, by-department, distribution), a
  deterministic 10,000-employee seed, Alembic migrations, and 52 passing tests.
- **Frontend — complete.** React + Vite + TypeScript SPA with Mantine: an
  analytics dashboard (summary cards, pay-by-country and comp-band charts,
  percentiles) and an employees view with search, filters, pagination, and
  create/edit/deactivate. Vitest component tests.

## Repository layout

```
docs/                 Requirements, design decisions, backend notes
backend/              FastAPI API, data model, analytics, seed, tests
frontend/             React SPA (dashboard + employees)
docker-compose.yml    Runs the full stack
```

## Quick start (Docker — runs everything)

Requires Docker. From the repo root:

```bash
docker compose up --build
```

- App: http://localhost:5173
- API docs: http://localhost:8000/docs

The backend container applies migrations and seeds 10,000 employees on first
start; the frontend is served by nginx, which proxies `/api` to the backend.

## Quick start (backend, local)

Requires [uv](https://docs.astral.sh/uv/).

```bash
cd backend
uv sync                       # install deps (fetches Python 3.12)
cp .env.example .env
uv run alembic upgrade head   # create schema
uv run python -m seed.seed    # seed 10,000 employees
uv run uvicorn app.main:app --reload
```

Then open the interactive API docs at http://localhost:8000/docs.

Run the tests:

```bash
cd backend
uv run pytest
```

## Quick start (frontend)

With the backend running on port 8000:

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173 (proxies /api to the backend)
npm test         # component tests
```

## Documentation

- [`docs/requirements.md`](docs/requirements.md) — one-page requirements, scope, and deliberate cuts
- [`docs/design-decisions.md`](docs/design-decisions.md) — design, architecture, AI workflow, trade-offs
- [`docs/backend.md`](docs/backend.md) — backend technology and structure
- [`docs/ai-usage.md`](docs/ai-usage.md) — how AI tooling was used and kept correct
