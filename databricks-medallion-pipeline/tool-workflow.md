# Tool Workflow (Part A)

## Primary AI tool used

Cursor (Agent for multi-file implementation; Ask for explanations). Supporting local files: gitignored plan/playbook/progress at repo root.

## How I provide project context to the tool

- `.cursorrules` for standing constraints
- `@` references to requirements, design, data model, DQ strategy, and layer specs
- Phase-scoped chats so context stays relevant
- Details: [tool-specific/cursor-workflow/project-context.md](tool-specific/cursor-workflow/project-context.md)

## How I use AI for requirement analysis

- Draft structure from the assignment PDF / plan
- Edit until language matches my understanding and real scope
- Keep honest clarifications only (no fake open questions)

## How I use AI for pipeline design (Bronze / Silver / Gold)

- Ask for three consistent artifacts: design notes, data model, DQ strategy
- Enforce flag-don’t-delete and layer boundaries in the prompt
- Reject designs that clean in Bronze or drop bad rows in Silver

## How I use AI for code generation (Python / PySpark / SQL)

- Specific prompts with schemas, exact DQ counts, and file paths
- Prefer CE-friendly Delta + Spark SQL patterns
- Generate one layer at a time against the design pack

## How I validate AI-generated code and logic

- Compare output to `@data-model.md` / `@data-quality-strategy.md`
- Run generators/tests locally where possible
- Spot-check counts (intentional issues, Gold sums) before accepting
- Record accepted / changed / rejected in `ai-prompts/`

## How I use AI for testing and validation

- Ask for asserts that intentional issue counts match the assignment
- Later: DQ tests that Silver rules detect seeded problems
- Light pipeline/integration checklist for Bronze → Silver → Gold relationships

## How I use AI for debugging (issues, root causes)

- Paste symptom + expected vs actual
- Require root cause and minimal fix (not broad rewrites)
- Capture in `debugging-notes.md` and `ai-prompts/debugging.md`

## How I use AI for data quality checks

- Implement checks as separate modules + orchestrator
- Always flag, never silent delete
- Demand a % passed metrics report and proof seeded issues are caught

## What I avoid sharing unnecessarily with AI tools

- Real customer PII
- Production credentials, API keys, tokens, private URLs with secrets
- Proprietary company data unrelated to this synthetic exercise

## How I would reuse this workflow in a real production pipeline

- Keep a short design/spec + rules file in-repo before codegen
- Phase prompts (ingest → DQ → marts → tests)
- Mandatory human review of DQ semantics and join filters
- Log prompt decisions for auditability; never paste secrets into the tool

## Lessons learned

- What worked:
  - Phase-scoped prompts against a written design pack (flag-don’t-delete, exact issue counts)
  - Local pandas tests for seeded inventory, then CE SQL counts for Silver = Bronze
  - Logging accept / change / reject in `ai-prompts/` so the story is auditable
- What did not work:
  - Trusting classic Spark helpers (`rdd`, `_jvm`, `dbutils.fs.ls`) on Community Edition Spark Connect
  - Assuming FileStore paths when CSVs were in `/Workspace/Users/{user}/...`
  - Local CSV tests passing while Spark `IntegerType` nulled FKs written as `5764.0`
- What I would change next time:
  - Pin CE / Spark Connect constraints in `.cursorrules` before first ingest
  - Spot-check raw CSV IDs and Spark null-FK counts before Silver
  - One documented data path; keep real CE stack traces in `debugging-notes.md`
