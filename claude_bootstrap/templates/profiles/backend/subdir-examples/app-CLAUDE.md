# CLAUDE.md — `app/`

> Loaded automatically when Claude works on files under `app/`. Does not bloat the root `CLAUDE.md`. See [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) for the subdirectory `CLAUDE.md` mechanism.

## Backend / service conventions

- **Boundary first**: validate request bodies, query params, and headers at the edge of each handler. Reject unknown fields; don't let unvalidated input reach the service layer.
- **Thin handlers**: route handlers parse/authorize/delegate. Business logic lives in a service/use-case layer that unit-tests without HTTP.
- **Errors**: return a consistent typed error shape + correct status code. Never leak stack traces, SQL, or internal paths to the client — log detail server-side.
- **Data access**: parameterize every query; scope each to the authenticated principal. No string-built SQL.

## What NOT to do here

- ❌ Hardcode secrets / connection strings — read them from env or a secret manager
- ❌ Log or return secrets, tokens, or full exception detail to the client
- ❌ Run a dependency install (`pip install` / `npm install` / `bundle install`) — name what's missing and defer to a human

## Renaming this file or removing it

Subdirectory `CLAUDE.md` files are optional. If your service lives somewhere else (or doesn't follow these conventions), delete this file or replace it with your own. The bootstrap added it as a starting point — it's not load-bearing.
