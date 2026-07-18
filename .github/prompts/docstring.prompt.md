# docstring

Review or generate Python docstrings for modules, classes, or functions.

## Standards

- Module and class docstrings use indicative mood.
- Function docstrings use imperative mood.
- Prefer one-line docstrings when sufficient.
- Use bullets only for non-obvious behavior guarantees.
- Document behavior/contract, not implementation details.
- Use "Calls" (not "Invokes") when describing function calls.

## Review mode output

List findings in source order and provide corrected docstrings inline, then include:

| Location | Issue | Corrected Docstring |
|----------|-------|---------------------|

Include only real issues.

## Generate mode output

Provide proposed docstrings grouped by module.
