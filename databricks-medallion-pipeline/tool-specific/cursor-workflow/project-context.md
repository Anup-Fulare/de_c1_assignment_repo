# How project context is provided to Cursor

## Persistent context sources

1. **Local plan (gitignored):** `ASSIGNMENT_PLAN.md` at git repo root — used to sequence work; not submitted.
2. **Project rules:** `databricks-medallion-pipeline/.cursorrules` — medallion boundaries, no secrets/PII, flag-don’t-delete DQ, document AI decisions.
3. **Design pack:** `@requirements-analysis.md`, `@design-notes.md`, `@data-model.md`, `@data-quality-strategy.md` — build-against specs.
5. **Submitted evidence:** `ai-prompts/*.md` — real prompt history as work happens.

## How I attach context in practice

- Prefer Agent mode for multi-file changes; Ask mode for explanations only.
- Reference files with `@` instead of pasting large blobs repeatedly.
- One phase per chat when context gets large (data gen → Bronze → Silver → Gold).
- After each accepted change: short note in the matching `ai-prompts/` file (accepted / changed / rejected).

## What I do not put in Cursor context

- Real customer PII, production credentials, API keys, tokens
- Anything outside synthetic assignment data
