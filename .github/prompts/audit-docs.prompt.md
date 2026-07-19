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
7. Verify AI assistant mapping consistency in `README.md`:
   - Each documented workflow appears as both `.claude/skills/<workflow>/SKILL.md` and
     `.github/prompts/<workflow>.prompt.md`.
   - Every workflow in `.claude/skills/` has a matching prompt in `.github/prompts/`, and vice versa.
   - Claude/Copilot command names in mapping and catalog tables match workflow names and corresponding files.
   - Referenced configuration sources are accurate (`CLAUDE.md`, `.claude/skills/*/SKILL.md`,
     `.github/copilot-instructions.md`, `.github/prompts/*.prompt.md`).

## Output

Report pass/findings per category, then provide a summary table:

| Document | Section / Location | Issue | Recommended Action |
|----------|--------------------|-------|--------------------|

Include only real issues.
