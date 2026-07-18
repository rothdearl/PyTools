# help-text

Evaluate or generate argparse help text for Pyr-CLI commands.

## Rubric

Use `docs/help_text_rubric.md` as the authoritative standard.

## Review checklist

- Program description is concise and task-focused.
- Long options use kebab-case.
- Metavariables are uppercase and clear.
- Option descriptions use action-first infinitive mood.
- Defaults/constraints/interactions are documented consistently.
- Mutually exclusive options use parallel phrasing.
- Option ordering follows workflow and dependency order.
- argparse formatting conventions are preserved.

## Output (review mode)

List findings in option declaration order, include corrected text, then:

| Component | Issue | Corrected Text |
|-----------|-------|----------------|

Include only genuine issues.

## Output (generate mode)

Provide proposed help text by option/component.
