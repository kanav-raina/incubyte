# Backend — Technology & Structure

> What the backend is built with, how it is organized, and how to run, test,
> seed, and migrate it. The backend is built first because it is the contract
> the frontend consumes.

---

## 1. Repository layout

A monorepo with backend and frontend as sibling folders, sharing one git
history.

```
incubyte/
├── docs/            # requirements, design decisions, ai-usage
├── backend/         # this document
├── frontend/        # React SPA (built later)
└── README.md        # top-level run instructions
```

The backend is independent of the frontend: its own dependencies, tooling, and
tests, deployable on its own.

---

## 2. Technology choices

| Concern | Choice | Why |
|---|---|---|
| Language | **Python 3.12** | Matches the role (Python). |
| Web framework | **FastAPI** | Minimal boilerplate, async, Pydantic-native, auto-generated OpenAPI/Swagger docs at `/docs`. Ideal for the analytics endpoints. |
| Data validation | **Pydantic v2** | Request/response schemas, settings management, strong typing at the edges. |
| ORM | **SQLAlchemy 2.0** (typed) | Standard, testable, DB-agnostic so the same code runs on SQLite and Postgres. |
| Migrations | **Alembic** | Versioned schema changes; demonstrates engineering maturity. |
| Database | **SQLite** (dev/test) → **Postgres** (deployed) | SQLite = zero-setup, fast tests; Postgres for the deployed instance. |
| Server | **Uvicorn** | ASGI server for FastAPI. |
| Seeding | **Faker** | Deterministic fake data (seeded RNG) for 10,000 employees. |
| Tests | **pytest** + **httpx** | Fast, deterministic; in-memory SQLite; `httpx`/TestClient for API tests. |
| Lint/format | **Ruff** | One fast tool for linting + formatting. |
| Dependency mgmt | **uv** (pyproject.toml) | Fast, reproducible installs; single lockfile. |

---

## 3. Project structure

```
backend/
├── app/
│   ├── main.py            # FastAPI app factory, router registration, CORS
│   ├── config.py          # Settings (env-driven) via pydantic-settings
│   ├── database.py        # Engine, SessionLocal, Base, get_db dependency
│   │
│   ├── models/            # SQLAlchemy ORM entities
│   │   ├── employee.py
│   │   ├── compensation.py
│   │   ├── country.py
│   │   └── department.py
│   │
│   ├── schemas/           # Pydantic request/response models
│   │   ├── employee.py
│   │   └── analytics.py
│   │
│   ├── repositories/      # Data access (queries) — isolates SQL
│   │   ├── employee_repo.py
│   │   └── analytics_repo.py
│   │
│   ├── services/          # Business logic — the testable core
│   │   ├── employee_service.py
│   │   └── analytics_service.py
│   │
│   ├── api/
│   │   ├── deps.py        # Shared dependencies (db session, pagination)
│   │   └── routes/
│   │       ├── employees.py
│   │       ├── analytics.py
│   │       └── meta.py    # health, reference data (countries, departments)
│   │
│   └── core/              # Cross-cutting helpers
│       ├── money.py       # Integer minor-unit money + currency conversion
│       ├── pagination.py
│       └── errors.py      # Error handlers / exception types
│
├── alembic/               # Migration environment
│   └── versions/
├── seed/
│   └── seed.py            # Generates 10,000 employees deterministically
├── tests/
│   ├── conftest.py        # Fixtures: in-memory DB, test client
│   ├── test_money.py
│   ├── test_analytics_service.py
│   └── test_employees_api.py
├── pyproject.toml
├── alembic.ini
├── .env.example
└── README.md
```

### Why this layering

Requests flow **routes → services → repositories → DB**:

- **routes** handle HTTP only (validation, status codes, serialization).
- **services** hold business logic (analytics math, compensation rules) and are
  unit-tested without the web server.
- **repositories** isolate SQLAlchemy queries, so SQL stays in one place and is
  easy to optimize.
- **core** holds pure, heavily-tested utilities (money, pagination).

This keeps the valuable logic decoupled from FastAPI and trivially testable.

---

## 4. Data model (summary)

Full reasoning is in `docs/design-decisions.md`. Essentials:

```
Country(code, name, currency, fx_rate_to_base)
Department(id, name)
Employee(id, name, email, country_fk, department_fk, role, level,
         hire_date, status, manager_id?)
Compensation(id, employee_fk, base_salary[int minor units], currency,
             effective_from, effective_to)   # current = effective_to IS NULL
```

Key rules:
- **Money is stored as integers in minor units** (cents). Never floats.
- **Salaries stored in native currency**; normalized to a base currency for
  cross-country comparison using `Country.fx_rate_to_base`.

---

## 5. API surface (planned)

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check. |
| GET | `/api/employees` | List with search/filter (country, dept, level) + pagination. |
| POST | `/api/employees` | Create an employee + initial compensation. |
| GET | `/api/employees/{id}` | Employee detail incl. current salary. |
| PATCH | `/api/employees/{id}` | Update employee / salary. |
| DELETE | `/api/employees/{id}` | Deactivate (soft delete). |
| GET | `/api/analytics/summary` | Headcount, total payroll, avg, **median** (base currency). |
| GET | `/api/analytics/by-country` | Aggregates per country, normalized. |
| GET | `/api/analytics/distribution` | Percentiles (p25/p50/p75/p90), comp bands by level. |
| GET | `/api/meta/countries`, `/api/meta/departments` | Reference data for filters. |

Interactive docs are auto-served at **`/docs`** (Swagger) and **`/redoc`** —
this doubles as a free, accurate API artifact.

**Analytics are computed in SQL** (GROUP BY / AVG / percentile), never by
loading rows into Python.

---

## 6. Configuration

Environment-driven via `pydantic-settings`, with a committed `.env.example`:

```
DATABASE_URL=sqlite:///./app.db      # postgresql+psycopg://... in deploy
BASE_CURRENCY=USD
CORS_ORIGINS=http://localhost:5173
```

No secrets are committed; `.env` is gitignored.

---

## 7. Testing strategy

- **Fast & deterministic:** in-memory SQLite (`sqlite:///:memory:`), seeded RNG.
- **Test-first** for the core: money/currency math and percentile/median
  calculations are written red → green → refactor.
- **Layers covered:**
  - `core/money.py` — unit tests for conversion and rounding edge cases.
  - `services/analytics_service.py` — unit tests for the aggregation logic.
  - API routes — a focused set of integration tests via TestClient.
- **Run:** `uv run pytest` (with `--cov` for coverage locally).

---

## 8. Seeding 10,000 employees

`seed/seed.py`:
- Deterministic (fixed Faker/random seed) so runs are reproducible.
- Spreads employees across several countries (with FX rates), departments,
  roles, and levels with realistic salary ranges per level/country.
- Uses **batched bulk inserts**, not 10k individual ORM adds, for speed.
- Run: `uv run python -m seed.seed`.

---

## 9. Running locally

```bash
cd backend
uv sync                       # install deps
cp .env.example .env
uv run alembic upgrade head   # create schema
uv run python -m seed.seed    # seed 10k employees
uv run uvicorn app.main:app --reload   # http://localhost:8000/docs
```

---

## 10. Deployment

- **Postgres** managed instance (Render/Railway/Fly).
- `DATABASE_URL` switched to the Postgres DSN; same SQLAlchemy code path.
- Run `alembic upgrade head` then the seed script on first deploy.
- Frontend deployed separately (Vercel/Netlify) and pointed at the API URL via
  an env var; backend CORS allows that origin.

---

## 11. Build order (incremental commits)

1. Backend scaffold (FastAPI app, config, db session, health route).
2. Models + first Alembic migration.
3. `core/money.py` test-first.
4. Seed script (10k employees).
5. Employee endpoints + tests.
6. Analytics service + endpoints, test-first.
7. Polish (error handling, pagination, OpenAPI metadata).

Then the frontend is built against the now-stable API.
