# audit-docs

Audit project documentation for accuracy against the current codebase.

## Scope

Review:

- `README.md`
- `CLAUDE.md`
- `docs/code_evaluation_rubric.md`
- `docs/help_text_rubric.md`

## Checks

1. Verify file references exist.
2. Verify package structure references match actual directories.
3. Verify framework module names are accurate.
4. Verify command names map to modules under `pyrcli/commands/`.
5. Verify key symbols named in `CLAUDE.md` still exist.
6. Verify rubric cross-references are accurate and non-contradictory.

## Output

Report pass/findings per category, then provide a summary table:

| Document | Section / Location | Issue | Recommended Action |
|----------|--------------------|-------|--------------------|

Include only real issues.
