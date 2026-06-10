# Salary Management

Web-based salary management for an organization with ~10,000 employees across
multiple countries. Lets an HR manager manage employee salary data and answer
org-wide questions about how the org pays people (totals, medians, by-country
comparisons in a common currency, and pay distribution by level).

Built as an assessment; see `docs/` for the thinking behind it.

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
docs/        Requirements, design decisions, backend notes
backend/     FastAPI API, data model, analytics, seed, tests
frontend/    React SPA (dashboard + employees)
```

## Quick start (backend)

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
