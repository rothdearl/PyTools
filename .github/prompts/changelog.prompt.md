# changelog

Generate a commit message and changelog entries for staged or described changes.

## Commit message rules

- One plain-English sentence.
- No conventional-commit prefix.
- Mention modules/symbols when localized.
- Keep wording proportional to change size.

## Changelog entry rules

- Append entries under `## Unreleased` in `CHANGELOG.md`.
- Format: `<module-or-component>: <what changed and why>.`
- One entry per logical change.
- Include rationale when non-obvious for callers.

## Output format

Provide:

1. `Commit message`
2. `Changelog entries`

Then apply entries to `CHANGELOG.md` without reformatting existing lines.
