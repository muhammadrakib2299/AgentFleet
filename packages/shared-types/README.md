# packages/shared-types

TypeScript types generated from the API's OpenAPI schema — the single
source of truth for the api ↔ web contract.

Generation (wired into CI in Phase 1, once the API surface stabilizes):

```bash
# API must be running locally
npx openapi-typescript http://localhost:8000/openapi.json -o src/api.d.ts
```

Until then, `apps/web/src/lib/api.ts` keeps hand-written types that mirror
the Pydantic response models.
