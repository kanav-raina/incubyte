#!/bin/sh
set -e

# Apply migrations, then seed once if the database is empty.
alembic upgrade head

COUNT=$(python -c "from app.database import SessionLocal; from app.models import Employee; s = SessionLocal(); print(s.query(Employee).count()); s.close()")
if [ "$COUNT" -eq 0 ]; then
  echo "Seeding database with 10,000 employees..."
  python -m seed.seed
else
  echo "Database already has $COUNT employees; skipping seed."
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
