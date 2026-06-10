# Salary Management — Design, Architecture & Decisions

> A working document explaining how the system is built, why it is built that
> way, and where it could go next. Written to be read top-to-bottom in ~10
> minutes and to support a walkthrough during the technical discussion.

---

## 1. Context in one paragraph

ACME's HR team manages salary data for ~10,000 employees across multiple
countries, today in spreadsheets. The goal is a web-based tool that lets the HR
manager **manage employee salary data** and **answer questions about how the
org pays people** (totals, fairness, distribution by country/role/level). The
emphasis of this build is engineering judgment and product thinking over raw
feature count — a small, correct, well-tested system rather than a large
fragile one.

---

## 2. Design decisions

### 2.1 Treat "answering pay questions" as the core feature, not CRUD

CRUD over employees is table stakes. The differentiator the brief asks for is
the ability to *answer questions about how the org pays people*. So the design
centres on an **analytics/insights layer** (payroll totals, medians,
percentiles, pay-by-country, comp bands by level) rather than just a grid of
rows. Most of the engineering care and test coverage goes here.

### 2.2 Money is stored as integers in minor units

All monetary amounts are stored as **integers in the currency's minor unit**
(e.g. cents), never as floating-point. Floats silently lose precision and break
sums/averages over 10k rows. Formatting to a human-readable value happens only
at the edges (API response / UI). This is a small decision with outsized impact
on correctness and is directly unit-tested.

### 2.3 Compensation is modelled separately from the employee

Salary lives in its own `Compensation` table linked to `Employee`, with
`effective_from` / `effective_to` dates, rather than as a column on the
employee. This:

- keeps the employee record stable while pay changes over time,
- makes "current salary" a well-defined query (`effective_to IS NULL`),
- leaves the door open to salary history without a schema rewrite.

Whether the *UI* exposes history is a scope choice (see trade-offs); the *model*
supports it cheaply.

### 2.4 Currencies stored natively, normalized for comparison

Because employees span countries, each salary is stored in its **native
currency**. A `Country` carries an `fx_rate_to_base`, so org-wide comparisons
can be normalized to a single base currency on read. Native storage preserves
the source of truth; normalization is a presentation/analytics concern.

### 2.5 Aggregations are computed in the database, not in Python

All analytics (sums, averages, medians, percentiles, group-bys) are pushed into
**SQL**. We never load 10k rows into application memory to reduce them. This is
both a correctness and a scale decision and is the main reason the analytics
endpoints stay fast.

### 2.6 Single persona, thin auth

The only user is the HR manager. Rather than building full RBAC, auth is kept
intentionally thin (single-user / stubbed login). Engineering time is spent on
the data and analytics core where the value is. This is called out as a
deliberate cut, not an oversight.

### 2.7 Tests lead the implementation (TDD)

Core logic — money handling, currency normalization, percentile/median
calculations — is written test-first (red → green → refactor). Tests use an
in-memory SQLite database so they are fast and deterministic. The commit
history is intended to show this rhythm rather than feature-dump commits.

---

## 3. Architecture

### 3.1 Shape

A **separated backend API + single-page frontend**, rather than a single
full-stack framework.

```
┌─────────────────────┐        HTTPS / JSON        ┌──────────────────────────┐
│   React + Vite SPA   │  ───────────────────────▶ │     FastAPI backend       │
│  (Mantine + Recharts)│  ◀─────────────────────── │  (Pydantic + SQLAlchemy)  │
└─────────────────────┘                            └────────────┬─────────────┘
                                                                 │
                                                                 ▼
                                                   ┌──────────────────────────┐
                                                   │  SQLite (dev/test)        │
                                                   │  Postgres (deployed)      │
                                                   └──────────────────────────┘
```

### 3.2 Backend layering

```
api/         FastAPI routers — HTTP, validation, serialization only
services/    business logic — analytics, compensation rules (the testable core)
repositories/ (or db/)  data access via SQLAlchemy
models/      ORM entities
schemas/     Pydantic request/response models
seed/        10k-employee seed script
```

The service layer holds the logic worth testing and is independent of FastAPI,
so it can be unit-tested without spinning up the web server.

### 3.3 Data model (essentials)

```
Employee(id, name, email, country_fk, department_fk, role, level,
         hire_date, status, manager_id?)
Compensation(id, employee_fk, base_salary[int minor units], currency,
             effective_from, effective_to)
Country(code, name, currency, fx_rate_to_base)
Department(id, name)
```

### 3.4 Chosen stack and rationale

| Concern | Choice | Why |
|---|---|---|
| Backend | **FastAPI + Pydantic** | Matches the Python JD; minimal boilerplate; auto OpenAPI docs double as an artifact; ideal for analytics endpoints. |
| ORM / migrations | **SQLAlchemy 2.0 + Alembic** | Standard, testable; lets the same code run on SQLite and Postgres. |
| Database | **SQLite → Postgres** | SQLite for dev/tests (zero setup, fast); Postgres for the deployed instance (persistence, concurrency). |
| Frontend | **React + Vite + TypeScript** | Lightweight SPA against a separate API; type safety. |
| UI / charts | **Mantine + Recharts** | Ready-made tables, forms, and charts → a credible HR dashboard quickly. |
| Tests | **pytest**, **Vitest + RTL** | Fast, deterministic; in-memory DB for the backend. |

### 3.5 Handling 10,000 employees

- **Seeding:** batched bulk inserts (not 10k individual ORM adds) with
  deterministic fake data.
- **Listing:** server-side pagination + indexes on common filter columns
  (country, department, level).
- **Analytics:** SQL aggregation, so cost scales with groups, not rows.

10k rows is modest for a relational DB; the point is to *architect* as if scale
matters, not to claim 10k is hard.

---

## 4. AI workflows

AI tools were used intentionally as an accelerator, with the engineer staying
responsible for every decision and correctness check.

### 4.1 Where AI helped

- **Shaping the problem:** drafting and pressure-testing the requirements and
  scope cuts, surfacing edge cases (currency precision, median vs. average).
- **Scaffolding:** generating boilerplate (project structure, Pydantic schemas,
  CRUD endpoints) that is mechanical and low-risk.
- **Test generation:** proposing test cases for analytics math, then reviewing
  and tightening them.
- **Refactoring & review:** asking the model to critique structure and naming,
  and to suggest simplifications.

### 4.2 How AI output was kept honest

- **Tests are the gate.** AI-suggested logic only lands once it passes
  test-first specs I wrote or vetted — especially for money and percentile math.
- **Read before commit.** Generated code is reviewed line-by-line; nothing is
  committed because "it ran."
- **Small steps.** AI is used in narrow, verifiable increments rather than
  asking for the whole app at once, so output stays reviewable.
- **Decisions stay human.** Architecture, data model, and scope are my calls;
  AI is a sounding board and typist, not the architect.

### 4.3 Artifact

The actual prompts and how their output was validated are logged in
`docs/ai-usage.md` so the collaboration is transparent and reviewable.

---

## 5. Trade-offs considered

| Decision | Alternative | Why this choice |
|---|---|---|
| Separate API + SPA | Next.js full-stack monolith | JD is Python; keeping the backend independent makes it the focus and independently testable. Cost: two deploys. |
| SQLite (dev) / Postgres (prod) | Postgres everywhere | Faster local + test loop with SQLite; Postgres only where persistence matters. Cost: must avoid DB-specific SQL. |
| Thin/stubbed auth | Full RBAC | Single persona; spend time on the analytics core. Cost: not production-secure as-is. |
| Model salary history, expose current only | Single salary column | Future-proofs the model cheaply. Cost: slightly more query complexity now. |
| Static seeded FX rates | Live FX rate API | Deterministic and testable for the assessment. Cost: rates are not real-time. |
| 3–4 deep analytics views | Many shallow features | Depth + correctness demonstrate judgment better than breadth. Cost: fewer features on screen. |

Each cut is deliberate and documented in the requirements doc, not accidental.

---

## 6. Possible improvements

If this graduated toward production, the next steps, roughly in priority order:

1. **Real authentication & RBAC** — proper login, roles (HR / finance /
   manager / employee self-service), and an audit trail of who changed what.
2. **Full salary-history UX** — view and edit raises over time, effective-dated
   changes, and change reasons.
3. **Live currency rates** — pull FX from a rate provider with caching and a
   historical rate table for point-in-time accuracy.
4. **Richer pay-equity analytics** — gender/department pay-gap views, outlier
   detection, and comp-band breach alerts ("paid below band for level").
5. **Bulk import/export** — CSV/Excel import to ease migration off
   spreadsheets, plus export for reporting.
6. **Performance at larger scale** — caching of expensive aggregates,
   materialized views, and pagination/virtualization tuning beyond 10k.
7. **Observability & hardening** — structured logging, metrics, input
   validation hardening, and rate limiting.
8. **Stronger test depth** — property-based tests for money math and
   end-to-end (Playwright) coverage of the key HR workflows.

---

## 7. Summary

The system is deliberately small and sharply focused: a clean Python API with a
well-modelled salary domain, an analytics layer that actually answers the HR
manager's questions, and a thin UI to drive it — built test-first, with AI used
as a reviewable accelerator. The scope cuts are intentional and documented, and
the path to production is clear.
