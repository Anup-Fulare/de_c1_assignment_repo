# Cursor rules and instructions used

## Files

- Primary rules: `databricks-medallion-pipeline/.cursorrules`
- Walkthrough discipline: local `ASSIGNMENT_PROMPTS.md` + `ASSIGNMENT_PROMPT_PROGRESS.md` (gitignored)

## What `.cursorrules` enforces

- Medallion separation: Bronze raw / Silver flag-only / Gold analytics / Dashboard on Gold
- No secrets, tokens, or real customer PII — synthetic data only
- Readable, commented Python / PySpark / SQL; CE-friendly simplicity
- Match filenames and schemas from plan / design docs
- Document meaningful Cursor exchanges in `ai-prompts/` (do not invent history later)

## How I use the rules

- Keep `.cursorrules` in the project so Agent runs inherit constraints
- When suggesting a shortcut that deletes bad rows or mixes layers, reject and restate the rule
- Point Cursor at `@.cursorrules` + `@design-notes.md` for implementation prompts
- Update prompt logs with why a suggestion was rejected when it violated rules
