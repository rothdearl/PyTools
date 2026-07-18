# Changelog

All notable changes to this project are documented here. Entries accumulate under **Unreleased** and are promoted to a
versioned section when a release is cut.

---

## Unreleased

- `project`: Bumped version to 1.4.13.
- `project`: Corrected GitHub repository URLs — changed `Pyr-CLI` to `pyr-cli` to match the actual repository name casing.
- `config`: Added `.github/copilot-instructions.md` and a `.github/prompts/` prompt set mirroring the existing Claude skills so GitHub Copilot can be used alongside Claude Code.
- `docs`: Added an "AI Assistant Configuration" section to `README.md` documenting the dual Claude/Copilot setup and where each tool's project guidance is stored.
- `config`: Updated `.gitignore` to allow `.github/**` so Copilot configuration files are tracked in git.

---

## 1.4.12 — 2026-04-10

- `skills`: Added the `performance` skill for reviewing modules for practical, rubric-compliant performance improvements.
- `patterns`: Replaced `all(genexpr)` with an explicit early-return loop in `matches_all_patterns` to avoid a generator allocation on every line call.
- `progress_bar`: Added missing `@override` to `_render_final`.
- `spinner`: Added missing `@override` to `__post_init__` and `_render_final`.
- `text_program`: Added missing `@override` to `execute`.
- `seek`: Added `mtime_threshold` instance attribute; hoisted mtime option conversion from per-path logic into `initialize_runtime_state` to avoid repeated argument access per path.
- `seek`: Renamed `path_matches_filters` to `check_path_filters` — the method calls `print_error()` on `PermissionError`, which disqualifies it as a pure predicate.
- `seek`: Expanded `check_path_filters`, `print_path`, and `print_paths` docstrings with missing behavioral contracts.
- `glue`, `order`, `scan`, `seek`, `show`, `slice`, `subs`, `tally`, `track`: Fixed multi-line docstrings where the summary was placed on its own line rather than on the opening `"""` line.
- `here`: Added `assert isinstance(data, dict)` narrowing hint after `json.get_body()` — guaranteed by `allowed_types=(dict,)`, required to satisfy the type checker.
- `test_ini`: Replaced `print` with `reporters.suppress` as the `on_error` callback in `load_config` test calls.
- `scan`: Hoisted `apply_style` as a pre-loop local in `collect_matches`, replacing a compound boolean expression re-evaluated per match.
- `seek`: Tightened the `path_matches_patterns` docstring — "each match all provided patterns" removes the redundancy between the parameter names and "name and path".
- `skills`: Tightened the `performance` skill — replaced the blanket "repeated attribute traversal" rule with separate guidance for deep chains (3+ levels) and loop-invariant logic expressions; added a "What Not to Flag" entry prohibiting shallow attribute hoisting.

---

## 1.4.11 — 2026-04-08

- `env`: Improved docstrings for `get_env_str` and `get_required_env_str` to more accurately describe trim behavior.
- `docs`: Updated multi-line docstrings across `pyrcli.cli` and `pyrcli.cli.progress` to conform to PEP 257 — summary line now starts on the same line as the opening `"""`.
- `client`: Removed redundant `accept` default documentation from `delete`, `get`, `post`, and `put`; simplified `set_timeout` docstring.
- `config`: Added `.claude/settings.json` to configure Claude Code tool permissions for the project.
- `config`: Added `git diff --staged` allow rules to `.claude/settings.json` to suppress permission prompts from the changelog skill.
- `rubric`: Simplified the title of `code_evaluation_rubric.md` from "Python Code Evaluation Rubric and Design Guidelines" to "Python Code Evaluation Rubric".
- `render`: Changed `#:` comment on `_MatchRange` to `#` — Sphinx-style attribute docs have no effect on private symbols.
- `dupe`: Changed `#:` comment on `_LineGroups` to `#` — Sphinx-style attribute docs have no effect on private symbols.
- `order`: Changed `#:` comments on `_DateSortSegment` and `_NumericSortSegment` to `#` — Sphinx-style attribute docs have no effect on private symbols.
- `CLAUDE.md`: Revised import policy to follow the Google Python Style Guide — utility modules imported as modules; classes, type aliases, and constants imported by name.
- `rubric`: Revised import policy section to distinguish utility module imports from direct name imports for types and constants, with a usage-based evaluator heuristic.
- `__about__`: Updated `_get_version` docstring to document the ``"0+unknown"`` fallback when the package is not installed.
- `emit`: Fixed `--stdin-after` description ("read from standard input" replacing "process standard input") and moved `--no-newline` after the processing options.
- `glue`: Clarified `--number` as "number all lines", `--no-blank` as "suppress all blank lines", and added missing article to `--show-ends` description.
- `num`: Clarified `--no-blank` as "suppress all blank lines".
- `order`: Clarified `--no-blank` as "suppress all blank lines".
- `scan`: Fixed `--stdin-files` description to match project convention ("read FILES from standard input (one per line)").
- `seek`: Updated epilog to match project convention ("search the current directory when no DIRECTORIES are specified").
- `show`: Clarified `--line-numbers` as "number all lines".

---

## 1.4.10 — 2026-03-27

- `skills`: Added the `audit-docs` skill for verifying that README.md and CLAUDE.md are consistent with the project.
- `skills`: Added the `docstring` skill for reviewing and generating docstrings in isolation.
- `skills`: Added the `evaluate` skill for evaluating modules against the project's coding standards.
- `skills`: Added the `help-text` skill for evaluating and generating argparse help text against the help text rubric.
- `skills`: Added the `release-docs` skill for generating structured release notes at release time.
- `skills`: Added the `type-hints` skill for reviewing type annotation usage against the project's rubric.
- `CLAUDE.md`: Updated references to correctly point to the rubric files in `docs/`.
- `docs`: Reformatted `code_evaluation_rubric.md` to be faithful to the original rubric content.
- `skills`: Added the `changelog` skill for generating commit messages and changelog entries from staged changes.
- `skills`: Renamed the `type-hints` skill to `typing` to better align with Python's own vocabulary for the domain.
- `skills`: Updated the `changelog` skill to append entries to CHANGELOG.md under the Unreleased section.
- `skills`: Updated the `release-docs` skill to read from CHANGELOG.md and reset the Unreleased section after a release.
- `docs`: Added CHANGELOG.md with the unreleased accumulation structure, seeded with entries from the current cycle.
- `CLAUDE.md`: Added a note to the Versioning section documenting the CHANGELOG.md unreleased accumulation workflow.
- `show`: Changed `Sequence[str]` to `Collection[str]` in `get_line_range` and `print_lines` — neither method uses indexing or ordering, only `len()` and iteration.
- `track`: Changed `Sequence[str]` to `Collection[str]` in `print_lines` — the method uses only `len()` and iteration.
- `dupe`: Changed `Sequence[str]` to `Collection[str]` in the inner type of `print_line_groups` — each group is accessed only via `len()` and iteration.
- `types`: Changed `CompiledPatterns` from `Sequence[re.Pattern[str]]` to `Collection[re.Pattern[str]]` — callers use only boolean checks and iteration, not indexing or ordering.
- `text_program`: Changed `post_execute` parameter from `Sequence[str]` to `Collection[str]` — overrides require only `len()` and iteration.
- `docs`: Updated `post_execute` signature in README.md to reflect the type change.
- `docs`: Corrected the `pyrcli.cli.http` module listing in README.md — renamed `responses` to `json`.
- `docs`: Corrected the `initialize_runtime_state` section in README.md — renamed `print_color` to `use_color`.
- `env`: Added `get_env_str` and `get_required_env_str` for reading environment variables with optional whitespace trimming.
- `tests`: Added `test_env.py` with full coverage of the env module.
