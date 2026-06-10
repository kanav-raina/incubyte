# Salary Management — Requirements

> One-page requirements written before building. It defines the goal, who it is
> for, what is in scope, what is deliberately left out (and why), and how we
> will know it works.

---

## Goal

Give ACME's HR manager a web-based tool to **manage salary data for ~10,000
employees across multiple countries** and to **answer questions about how the
org pays people** — replacing the current spreadsheet-driven process.

## Who it is for

The **HR manager** is the single user persona. They need to view and maintain
employee salary records and get quick, trustworthy answers about org-wide pay
(totals, fairness, distribution by country / role / level).

## The problem with today's approach

Salary data lives in spreadsheets spread across countries and currencies. It is
tedious to maintain, error-prone, hard to keep consistent, and nearly
impossible to query for org-wide insight ("what do we spend per country?", "are
people in the same role paid fairly?"). The tool exists to make that data
manageable and *answerable*.

---

## Scope & features (what we will build)

1. **Employee directory**
   - View, search, and filter employees (by country, department, role, level).
   - Server-side pagination to handle 10,000 records smoothly.

2. **Employee & compensation management**
   - Create, view, update, and deactivate an employee.
   - Set / update an employee's current salary in their local currency.

3. **Pay insights (the core value)**
   - Org-wide totals: total payroll, headcount, average and **median** pay.
   - **Pay by country**, with amounts **normalized to a single base currency**
     so countries are comparable.
   - **Distribution**: percentiles (p25/p50/p75/p90) and comp ranges by level.
   - At least one **fairness** view (e.g. pay range by role/level to spot
     people paid outside the band).

4. **Seed data**
   - A script that generates **10,000 realistic employees** across multiple
     countries, departments, levels, and currencies — deterministic so results
     are reproducible.

5. **Quality & delivery**
   - Meaningful, fast, deterministic tests around the core logic.
   - Deployed, runnable software + a short demo video.

---

## Out of scope (deliberate, with reasoning)

| Left out | Why |
|---|---|
| **Authentication & RBAC** | Single HR-manager persona. A thin/stubbed login keeps focus on the data and analytics core, which is where the value and the interesting engineering are. |
| **Payroll processing, tax, payslips** | This is salary *management and reporting*, not payroll *execution*. Tax/withholding is a large, country-specific domain outside the brief. |
| **Approval workflows & audit logs** | Enterprise governance features; the brief explicitly values good judgment over complexity. Noted as a clear next step. |
| **Live currency exchange rates** | Rates are seeded as static values so results are deterministic and testable. A real system would integrate an FX provider. |
| **Full salary-history UX** | The data model supports effective-dated history, but the UI exposes *current* pay only, to keep the first version focused. History view is a fast follow. |
| **Employee self-service / multi-tenant** | Only the HR manager uses this; multiple orgs/users are not required. |
| **Bulk import/export (CSV/Excel)** | Valuable for real migration off spreadsheets, but the seed script covers the assessment's data needs. Listed as an improvement. |

These are **choices, not gaps** — each is a conscious trade to spend effort
where it demonstrates the most engineering and product value.

---

## Assumptions

- Each employee has one current salary; raises over time exist conceptually but
  are not edited through the UI in v1.
- Currency conversion uses static, seeded FX rates against one base currency.
- "Multiple countries" implies multiple currencies that must be reconciled for
  org-wide comparison.
- Data volume is ~10,000 employees; the design should stay responsive at that
  scale and not fall over well beyond it.

## Open questions (sent to the team)

These do not block starting — sensible defaults are used until answered:

1. Will anyone besides the HR manager use this (affects auth scope)?
2. Which specific pay questions matter most to the HR manager?
3. For cross-country comparison: normalize to one currency, show native, or both?
4. Is salary *history* needed, or is the current figure sufficient?
5. What is the must-have "done" bar vs. nice-to-have?

---

## Success criteria

The build is successful if the HR manager can:

- Find and edit any of the 10,000 employees quickly.
- See **trustworthy org-wide pay numbers** (totals, median, by-country in a
  common currency) without touching a spreadsheet.
- Answer at least one **fairness/distribution** question (e.g. "is anyone paid
  outside the range for their level?").

…and if the engineering stands up to inspection: clean structure, core logic
covered by fast deterministic tests, an incremental commit history, and
documented, intentional use of AI.
