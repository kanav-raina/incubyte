# Salary Management — Frontend

React + Vite + TypeScript single-page app for the HR manager: an analytics
dashboard and an employee directory with create/edit/deactivate.

## Stack

- React + Vite + TypeScript
- [Mantine](https://mantine.dev/) (components, form, notifications)
- [TanStack Query](https://tanstack.com/query) for server state
- React Router
- [Recharts](https://recharts.org/) for charts
- Vitest + Testing Library

## Develop

The backend must be running on port 8000 (see `../backend`). The Vite dev
server proxies `/api` to it.

```bash
npm install
npm run dev        # http://localhost:5173
```

## Test, build, lint

```bash
npm test           # Vitest component tests
npm run build      # type-check + production build
npm run lint
```

## Configuration

- Dev: `/api` is proxied to `http://localhost:8000` (see `vite.config.ts`).
- Prod: set `VITE_API_URL` to the deployed backend's base URL.
