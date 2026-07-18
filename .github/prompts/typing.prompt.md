# typing

Review type annotations in Python modules against project typing standards.

## Rubric

Use the typing guidance in `docs/code_evaluation_rubric.md`.

## Review areas

1. Collection parameter abstraction level (`Iterable`/`Collection`/`Sequence`/`MutableSequence`/concrete types)
2. Return-type concreteness where ownership/allocation matters
3. Local annotation noise vs justified annotations
4. Type alias opportunities for complex nested types (PEP 695 `type` syntax)
5. Modern syntax usage (built-in generics, `X | Y`, `Self`, `override`)
6. `__all__` without type annotations

## Output

Per module:

1. Brief assessment
2. Findings in source order
3. Summary table

| Module | Location | Issue | Action |
|--------|----------|-------|--------|

Include only genuine issues.
