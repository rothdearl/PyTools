# evaluate

Evaluate one or more Python modules against Pyr-CLI coding standards.

## Rubric

Use `docs/code_evaluation_rubric.md` as the authoritative standard.

## Evaluate

- Module cohesion and naming
- Class/function naming quality
- Docstring correctness (mood and contract clarity)
- Comment quality (intent vs restatement)
- Type annotation quality
- Import policy adherence
- `pass` vs `...` semantic usage
- Namespace redundancy

## Output

For each module:

1. Brief overall assessment
2. Findings in source order
3. Summary table

| Module | Location | Issue | Action |
|--------|----------|-------|--------|

Include only genuine issues.
