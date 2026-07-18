# Pyr-CLI Copilot Instructions

Use these instructions when generating or editing code in this repository.

## Project scope

Pyr-CLI is a toolkit of small, composable Unix-style CLI programs built on a shared Python framework.

- `pyrcli.cli` contains shared framework modules.
- `pyrcli.commands` contains one command module per program.
- Optional packages: `pyrcli.cli.http` and `pyrcli.cli.progress`.

## Core design principles

- Clarity over cleverness.
- Explicit behavior over implicit defaults.
- Single responsibility for modules, classes, and functions.
- Pure logic separated from I/O boundaries.
- Deterministic behavior unless I/O, environment, or time makes that impossible.

## Python and typing

- Target Python 3.12+ syntax.
- Use built-in generics (`list[str]`) and modern unions (`X | Y`).
- Use the weakest accurate collection type for parameters (`Iterable`, `Collection`, `Sequence`, `MutableSequence`).
- Use concrete return types when ownership/allocation semantics matter.
- Avoid noisy local annotations unless type inference is unclear or surprising.

## Imports

- Import utility modules as modules and call functions via module prefix.
- Import classes, type aliases, and `Final` constants directly by name.
- Access mutable shared module state through module attributes, not direct variable imports.

## CLI framework expectations

All commands should inherit from `CLIProgram` or `TextProgram` and follow the standard lifecycle:

1. Parse arguments
2. Option lifecycle (`check_option_dependencies`, `validate_option_ranges`, `normalize_options`, `initialize_runtime_state`)
3. Execute
4. `post_execute` for `TextProgram`
5. `exit_if_errors`

## Documentation and help text

- Module/class docstrings: indicative mood.
- Function docstrings: imperative mood.
- Document behavior guarantees, not implementation details.
- Use "Calls" (not "Invokes") when describing function calls.
- Help text should follow `docs/help_text_rubric.md` (action-first, concise, POSIX-aligned phrasing).

## Authoritative references

When uncertain, follow these documents in order:

1. `docs/code_evaluation_rubric.md`
2. `docs/help_text_rubric.md`
3. `CLAUDE.md` (project context and conventions)
