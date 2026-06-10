# AI Usage

How AI tooling was used to build this project, and — just as importantly — how
its output was kept correct and how decisions stayed with the engineer. This is
a candid record, not a highlight reel.

## Tooling

- **Claude Code** (agentic CLI) as the primary assistant: reading/writing files,
  running the test suite, the seed script, migrations, and the dev servers, and
  making incremental commits.
- The assistant ran commands and proposed code; the engineer directed the
  approach, made the design calls, and reviewed every change before it was
  committed.

## How AI was used, phase by phase

**1. Framing the problem.** Before any code, AI helped draft and pressure-test
the requirements and scope cuts (`docs/requirements.md`) and the architecture
and trade-offs (`docs/design-decisions.md`). These were committed first so the
git history opens with product thinking, not code.

**2. Stack and structure.** AI helped lay out the backend structure
(`routes → services → repositories`) and the monorepo split. The choices
(FastAPI + SQLAlchemy, SQLite→Postgres, React + Vite + Mantine) were decided by
the engineer and recorded in the docs.

**3. Test-first core (TDD).** The two pieces of logic where correctness matters
most were written test-first, as visible red → green commit pairs:
- money handling (integer minor units, half-up rounding, FX normalization)
- analytics (totals, average, median, percentiles, comp bands)

The failing tests were written and committed first, then the implementation to
make them pass. This is the main mechanism that kept AI-generated logic honest.

**4. Mechanical scaffolding.** AI generated the boilerplate that is low-risk and
tedious: Pydantic schemas, CRUD endpoints, the Vite/Mantine scaffold, and the
typed API client — all reviewed before committing.

**5. Verification on real data.** Beyond unit tests, the analytics were run
against the full 10,000-row seed and the numbers were sanity-checked (median
below mean → right-skewed pay; US/UK highest, India/Brazil lowest; comp bands
monotonic by level; JPY normalized correctly). The full stack was verified by
running both servers and confirming the Vite proxy returned live data.

## How AI output was kept correct

- **Tests are the gate.** Money and percentile maths were pinned by tests with
  hand-computed expected values before the implementation existed. Nothing
  shipped because "it ran" — it shipped because the tests said so.
- **Small, reviewable steps.** Work proceeded in narrow increments (one feature
  or one layer at a time) so each diff was small enough to read line by line.
- **Run it, don't trust it.** Migrations were applied and rolled back, the seed
  was executed, `alembic check` confirmed no model/migration drift, and the API
  was exercised end to end.
- **Lint and types.** Ruff (backend) and `tsc` + Vitest (frontend) ran on each
  change; warnings were fixed rather than ignored.
- **The engineer owns the decisions.** Data model, scope cuts, the
  in-SQL-aggregation approach, the nearest-rank percentile choice, and the
  effective-dated salary design were deliberate human calls; AI implemented and
  challenged them, it did not make them.

## Examples of the kinds of prompts used

These are representative of the intent behind the prompts, not verbatim logs:

- "Write failing tests for a money module: integer minor units, half-up
  rounding, and FX conversion across currencies with different decimal places."
- "Implement analytics so all aggregation happens in SQL — don't load 10k rows
  into Python to compute medians."
- "Add employee CRUD across routes → services → repositories; salary changes
  should be effective-dated, not overwrite history."
- "Build the dashboard: summary cards, pay-by-country chart, percentiles, and
  comp bands by level, normalized to the base currency."

## What AI was deliberately *not* used for

- Choosing the architecture, data model, or scope — those were reasoned about
  first and documented.
- Accepting generated numbers at face value — analytics were validated against
  computed expectations and real seed data.
- Hiding the collaboration — this document and the commit history are the record
  of how the solution actually evolved.
