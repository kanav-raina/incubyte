# Salary Management — Backend

FastAPI backend for managing employee salary data and answering org-wide pay
questions. See `../docs/backend.md` for the full design.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python 3.12 and dependencies)

## Setup

```bash
cd backend
uv sync                       # creates .venv and installs deps (fetches Python 3.12)
cp .env.example .env          # adjust if needed
uv run alembic upgrade head   # create the schema
uv run python -m seed.seed    # seed 10,000 employees (deterministic)
```

## Run

```bash
uv run uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/health

## Test

```bash
uv run pytest
```

## Lint / format

```bash
uv run ruff check .
uv run ruff format .
```
