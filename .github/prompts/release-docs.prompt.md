# release-docs

Generate release notes from `CHANGELOG.md` (`## Unreleased`) using Pyr-CLI conventions.

## Required sections

Produce all sections in this order:

1. Overview
2. Highlights
3. Changes
4. Internal Improvements
5. Documentation
6. Compatibility

## Rules

- Keep tone factual and concise.
- Name affected modules/symbols explicitly.
- For breaking changes, provide migration guidance.
- Do not invent significance for trivial releases.

## Output target

Write final content to `RELEASE.md` in the repository root.

After release notes are finalized, update `CHANGELOG.md` by:

1. Promoting `## Unreleased` to a versioned heading.
2. Adding a new empty `## Unreleased` section above it.
