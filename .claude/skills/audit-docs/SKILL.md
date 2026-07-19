---
name: audit-docs
description: Verify that README.md and CLAUDE.md are consistent with the actual state of the project — checking file references, package and module names, command names, and symbol names. Use when asked to audit or verify the documentation.
---

This skill is activated when the user asks to audit, check, or verify the documentation, or asks whether `README.md` or
`CLAUDE.md` are up to date.

---

## Process

Work through each verification category in order. For each check, read the relevant documents and then inspect the
filesystem or codebase to confirm the claim.

### 1. Read the documents

Read all four files before beginning any checks:

- `README.md`
- `CLAUDE.md`
- `docs/code_evaluation_rubric.md`
- `docs/help_text_rubric.md`

### 2. Verify file references

Collect every file path mentioned in `README.md` and `CLAUDE.md` — in backticks, as links, or in code blocks. For each
path, confirm the file exists on the filesystem.

Pay special attention to:

- References to rubric files under `docs/`
- Any other paths cited as authoritative references

### 3. Verify package structure

`CLAUDE.md` describes the package structure under **Project Overview**. For each package listed (`pyrcli.cli`,
`pyrcli.cli.http`, `pyrcli.cli.progress`, `pyrcli.commands`), confirm the corresponding directory exists under
`pyrcli/`.

### 4. Verify framework module names

`CLAUDE.md` lists framework modules in the **Key framework modules** table. For each module filename listed, confirm the
file exists under `pyrcli/cli/`. Flag any module in the table that does not exist, and flag any module present under
`pyrcli/cli/` (excluding `__init__.py` and private `_`-prefixed files) that is absent from the table.

### 5. Verify command names

If `README.md` lists or describes individual commands by name, confirm each has a corresponding module in
`pyrcli/commands/`. Flag commands mentioned in documentation that have no matching file.

### 6. Verify symbol names

`CLAUDE.md` names specific classes, methods, functions, and attributes by name. For each, grep the codebase to confirm
it exists. Key symbols to check:

**Classes:**

- `CLIProgram` — `pyrcli/cli/cli_program.py`
- `TextProgram` — `pyrcli/cli/text_program.py`
- `ErrorReporter` — `pyrcli/cli/reporters.py`
- `InputFile` — `pyrcli/cli/io.py`

**Lifecycle methods** (on `CLIProgram` / `TextProgram`):

- `check_option_dependencies`
- `validate_option_ranges`
- `normalize_options`
- `initialize_runtime_state`
- `execute`
- `post_execute`
- `exit_if_errors`
- `handle_redirected_input`
- `handle_terminal_input`
- `process_input_file`
- `build_arguments`
- `print_error`

**`render` module functions:**

- `render.style`
- `render.style_matches`
- `render.bold`
- `render.dim`
- `render.reverse_video`

**`reporters` module:**

- `reporters.raises`
- `reporters.suppress`

**Attributes:**

- `self.args`
- `self.use_color`
- `self.encoding`
- `self.has_errors`
- `self.version`

### 7. Verify rubric cross-references

Style and philosophy claims in `CLAUDE.md` should defer to the rubrics in `docs/` rather than duplicating them at
length. Check that:

- `CLAUDE.md` references `docs/code_evaluation_rubric.md` as the authoritative design rubric.
- `CLAUDE.md` references `docs/help_text_rubric.md` as the authoritative help text rubric.
- Neither README.md nor CLAUDE.md contains extended style or philosophy content that contradicts the rubrics.

### 8. Verify AI assistant mapping consistency

If `README.md` includes an **AI Assistant Configuration** section, verify the Claude Code and GitHub Copilot mapping is
still correct.

Check all of the following:

- Every workflow listed in the mapping has both:
    - `.claude/skills/<workflow>/SKILL.md`
    - `.github/prompts/<workflow>.prompt.md`
- Every `SKILL.md` under `.claude/skills/` has a matching Copilot prompt file under `.github/prompts/` (by workflow
  name), and vice versa.
- Command names shown in mapping/catalog tables (for example, `/audit-docs`) match the workflow names and corresponding
  skill/prompt files.
- Referenced configuration sources are accurate:
    - Claude: `CLAUDE.md` and `.claude/skills/*/SKILL.md`
    - Copilot: `.github/copilot-instructions.md` and `.github/prompts/*.prompt.md`

---

## Output Format

### Per-category results

For each of the eight categories above, report:

- **Pass** — if everything checks out (one line is sufficient).
- **Findings** — a list of specific discrepancies if any are found.

### Summary table

At the end, produce a single summary table of all findings:

| Document | Section / Location | Issue | Recommended Action |
|----------|--------------------|-------|--------------------|
|          |                    |       |                    |

Only include rows for genuine issues. Do not pad with non-issues.

### Tone

- Direct and factual. Report what is wrong and what the correct state should be.
- Do not speculate about why something drifted — just state the discrepancy.
- If a finding is ambiguous (e.g., a symbol was renamed vs. removed), say so and suggest the user verify.
