# performance

Review Python modules for practical performance improvements that preserve readability.

## Context

Assume Pyr-CLI commands are usually I/O-bound. Prefer changes that reduce meaningful I/O or obvious repeated CPU work in hot paths.

## Focus areas

1. Unnecessary buffering vs streaming
2. Redundant loop work
3. Regex compilation inside loops
4. Costly membership checks in loops
5. Incremental string building in large loops
6. Missed early exits
7. Recomputed display/padding lengths

## What to avoid

- Clever rewrites with poor readability trade-offs
- Large algorithmic redesigns without clear need
- Suggestions that conflict with project rubric conventions

## Output

For each finding, label impact:

- `High`
- `Low`
- `Not recommended`

Then summarize:

| Module | Location | Finding | Impact | Action |
|--------|----------|---------|--------|--------|
