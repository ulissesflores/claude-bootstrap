---
paths:
  - "**/*.py"
  - "**/*.rb"
  - "**/*.go"
  - "**/*.java"
  - "**/*.kt"
  - "**/*.ts"
  - "**/*.js"
---

# Backend / web-service conventions

- **Validate at the boundary.** Parse and validate every inbound request body / query / header
  before it reaches business logic; never trust client input. Reject unknown fields explicitly.
- **Typed, consistent errors.** Return a stable error shape with the right status code; never leak
  stack traces, SQL, or internal paths to the client. Log the detail server-side, not in the response.
- **Secrets stay out of code and VCS.** Read credentials from env / a secret manager; never hardcode
  them, never log them, never echo them into responses.
- **Parameterize every query.** No string-built SQL/NoSQL. Scope each query to the authenticated
  principal — authorization is per-request, not assumed from the route.
- **Thin handlers, testable services.** Keep route handlers thin; put business logic in a service
  layer that unit-tests without spinning up HTTP. Mutating endpoints are idempotent where it matters
  and return explicit status codes.
- **This tool never installs dependencies.** If a dependency is missing, state what to add and let a
  human run the install — do not run `pip install` / `npm install` / `bundle install` yourself.
