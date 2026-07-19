# Pyr-CLI

## Overview

Pyr-CLI is a toolkit of small, composable CLI programs designed for deterministic pipelines. It provides single-purpose
commands that share a common invocation model and stable output contract. Each tool performs one well-defined operation,
favors explicit behavior over implicit defaults, and composes predictably in shell pipelines unless interacting with
external state.

The project is intentionally **pedantic but practical**: behavior is specified precisely where it affects correct usage,
and kept simple where it does not.

All Pyr-CLI commands report a single, project-wide version sourced from `pyproject.toml`.

---

## Design Philosophy

Pyr-CLI follows a small set of operational rules:

- **Single responsibility** — each program performs one operation on a text stream or structured input.
- **Pipeline first** — all tools read from `stdin` when no input file is provided and write results to `stdout`.
- **Deterministic by default** — identical input produces identical output unless the program explicitly depends on
  time, environment, or filesystem state.
- **Explicit side effects** — programs that touch the filesystem or external state document that behavior.
- **TTY-aware formatting** — ANSI rendering is applied only when output is a terminal; otherwise plain text is
  emitted.
- **Stable output contracts** — output shape and ordering are defined and suitable for downstream processing.

These constraints make the tools predictable, scriptable, and safe for composition.

---

## Dependencies

Pyr-CLI targets Python ≥ 3.12.

The following third-party packages are required at runtime:

- colorama
- python-dateutil
- requests

These dependencies must be available in the active Python environment before running any Pyr-CLI commands.

---

## Installation

Pyr-CLI is installed using `pip`.

> Some environments (such as embedded Python distributions) may require setuptools to be installed manually before
> building:

```bash
pip install --upgrade setuptools
````

### Development Install (Editable)

Create and activate a virtual environment, then install Pyr-CLI in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

This registers all Pyr-CLI commands as console scripts in the active environment.

### User Install

To install Pyr-CLI as a user-level CLI toolkit:

```bash
python3 -m pip install --user .
```

Ensure the user script directory is on your `PATH`.

---

## Command Model

All Pyr-CLI commands follow the same execution model:

1. **Input resolution**
    - Read from `stdin` if no path is provided
    - Otherwise, read from the specified file(s)
2. **Normalization**
    - Input is converted to a canonical internal representation so downstream logic does not depend on superficial
      differences (line endings, trailing whitespace, etc.)
3. **Core operation**
    - A pure transformation whenever possible
4. **Output**
    - Written to `stdout`
    - Errors written to `stderr`
    - Non-zero exit codes only for user or system errors

Unless otherwise stated, tools are **stream-safe** and do not buffer the entire input unnecessarily.

---

## Architecture

Pyr-CLI is layered to separate pure logic from side effects:

    Programs → CLI framework → Text/Pattern primitives → Rendering → I/O boundary

### CLI Framework

Provides:

- Program lifecycle
- Argument parsing
- Input routing
- Output discipline and exit codes

### Text and Pattern Layer

Pure, deterministic transformations used by multiple tools. These functions do not perform I/O.

### Rendering Layer

ANSI and formatting utilities. Rendering is applied only when writing to a TTY.

### I/O Boundary

All filesystem and terminal interaction is isolated here. This makes core logic testable and deterministic.

---

## Optional Packages

The CLI framework provides two optional sub-packages for commands that need them.

### `pyrcli.cli.http`

Provides HTTP request helpers for DELETE, GET, POST, and PUT operations, built on ``requests``. Includes utilities for
parsing and validating HTTP response bodies.

- ``client`` — HTTP request helpers with configurable timeout and optional status validation.
- ``json`` — Utilities for reading and validating JSON response bodies.
- ``upload`` — Multipart file upload helpers.

### `pyrcli.cli.progress`

Provides terminal progress indicators for commands that perform long-running operations.

- ``ProgressBar`` — For work with a known total.
- ``Spinner`` — For work with an unknown total.

---

## Output Conventions

- **stdout** — primary program output
- **stderr** — diagnostics and error messages
- **Exit codes**
    - `0` — success
    - `1` — no matches found (scan, seek) or user/system error
    - `2` — user/system error (scan, seek)
    - `>0` — user error, invalid input, or system failure (all other commands)

Unless a tool explicitly documents ordering semantics, output preserves the input order.

---

## Tools

Each tool performs one well-defined operation.

### `dupe`

A minimal, uniq-like command for filtering and reporting repeated lines.

### `emit`

A minimal, echo-like command for writing strings to standard output.

### `glue`

A minimal, cat-like command for concatenating files to standard output.

### `here`

A minimal command for displaying current IP-based location information.

### `num`

A minimal, nl-like command for numbering lines in files.

### `order`

A minimal, sort-like command for sorting and printing lines.

### `peek`

A minimal, head-like command for printing the first part of files.

### `scan`

A minimal, grep-like command for printing lines that match patterns.

### `seek`

A minimal, find-like command for searching for files in a directory hierarchy.

### `show`

A minimal command for displaying files with optional whitespace rendering.

### `slice`

A minimal, cut-like command that splits lines in files into fields.

### `subs`

A minimal command for replacing matching text in files.

### `tally`

A minimal, wc-like command for counting lines, words, and characters in files.

### `track`

A minimal, tail-like command for printing the last part of files and following new lines.

### `when`

A minimal calendar command for displaying months, quarters, or years with optional date and time.

> Each command documents its own flags and output shape via `--help`.

---

## Error Handling Contract

- Invalid user input results in a non-zero exit code and a concise diagnostic on `stderr`.
- Internal errors are not silently suppressed.
- Partial output is not emitted after a fatal error unless explicitly documented.

---

## Development Notes

The codebase targets modern Python and follows these principles:

- Clarity over cleverness
- Explicit semantic contracts
- Weakest correct type annotations for inputs
- Pure functions separated from I/O
- Structured docstrings describing guarantees, not implementation trivia

Contributions should preserve the single-responsibility design and the pipeline-safe execution model.

---

## AI Assistant Configuration

This repository supports both [Claude Code](https://claude.ai/code) and GitHub Copilot Chat, with aligned command
workflows.

### Assistant support

| Assistant      | Configuration Source                        | Command Source                |
|----------------|---------------------------------------------|-------------------------------|
| Claude Code    | `CLAUDE.md` and `.claude/skills/*/SKILL.md` | `.claude/skills/`             |
| GitHub Copilot | `.github/copilot-instructions.md`           | `.github/prompts/*.prompt.md` |

### Command mapping (Claude Code -> GitHub Copilot)

| Workflow     | Claude Command  | Copilot Command |
|--------------|-----------------|-----------------|
| Audit Docs   | `/audit-docs`   | `/audit-docs`   |
| Changelog    | `/changelog`    | `/changelog`    |
| Docstring    | `/docstring`    | `/docstring`    |
| Evaluate     | `/evaluate`     | `/evaluate`     |
| Help Text    | `/help-text`    | `/help-text`    |
| Performance  | `/performance`  | `/performance`  |
| Release Docs | `/release-docs` | `/release-docs` |
| Typing       | `/typing`       | `/typing`       |

### Shared command catalog

| Workflow     | Command         | Claude Skill Source                    | Copilot Prompt Source                    | Purpose                                                                               |
|--------------|-----------------|----------------------------------------|------------------------------------------|---------------------------------------------------------------------------------------|
| Audit Docs   | `/audit-docs`   | `.claude/skills/audit-docs/SKILL.md`   | `.github/prompts/audit-docs.prompt.md`   | Verify `README.md`, `CLAUDE.md`, and rubric docs against the current codebase.        |
| Changelog    | `/changelog`    | `.claude/skills/changelog/SKILL.md`    | `.github/prompts/changelog.prompt.md`    | Generate a commit message and `CHANGELOG.md` entries for staged or described changes. |
| Docstring    | `/docstring`    | `.claude/skills/docstring/SKILL.md`    | `.github/prompts/docstring.prompt.md`    | Review, generate, or fix Python docstrings for modules, classes, or functions.        |
| Evaluate     | `/evaluate`     | `.claude/skills/evaluate/SKILL.md`     | `.github/prompts/evaluate.prompt.md`     | Audit Python modules against the project code evaluation rubric.                      |
| Help Text    | `/help-text`    | `.claude/skills/help-text/SKILL.md`    | `.github/prompts/help-text.prompt.md`    | Evaluate or generate argparse help text using the project help-text rubric.           |
| Performance  | `/performance`  | `.claude/skills/performance/SKILL.md`  | `.github/prompts/performance.prompt.md`  | Review modules for practical, readability-preserving performance improvements.        |
| Release Docs | `/release-docs` | `.claude/skills/release-docs/SKILL.md` | `.github/prompts/release-docs.prompt.md` | Generate release notes from `CHANGELOG.md` and update release sections.               |
| Typing       | `/typing`       | `.claude/skills/typing/SKILL.md`       | `.github/prompts/typing.prompt.md`       | Review type annotation quality against project typing standards.                      |

---

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

You may redistribute and/or modify this software under the terms of the GPL-3.0.
A copy of the license is included in the `LICENSE` file and is also available
at: https://www.gnu.org/licenses/gpl-3.0.en.html

---

## Writing a New Command-Line Program

This project provides two abstract base classes that define a consistent lifecycle, error model, and I/O behavior for
all command-line tools:

- **CLIProgram** -- for general programs
- **TextProgram** -- for programs that read and process text streams

All new programs **must inherit from one of these classes**.

---

## Choosing a Base Class

### Use CLIProgram when

- The program does **not** read text files
- The program operates only on arguments, the network, the filesystem, etc.

### Use TextProgram when

- The program reads from files, standard input, or text streams
- The program needs consistent handling of encodings, file iteration, and UnicodeDecodeError reporting

---

## Required Structure

### Class Definition

``` python
class MyProgram(CLIProgram):  # or TextProgram
```

### Constructor

All programs **must** call `super().__init__` with:

- `name` — program name
- `error_exit_code` — exit code on failure (optional; defaults to `1`)

``` python
def __init__(self) -> None:
    super().__init__(name="myprog")
```

``` python
def __init__(self) -> None:
    super().__init__(name="myprog", error_exit_code=2)
```

---

## Required Methods

### From CLIProgram

Every program **must implement**:

#### `build_arguments(self) -> argparse.ArgumentParser`

Define all command-line options.

#### `execute(self) -> None`

Implement the program's core behavior.
This method is called **after** arguments are parsed, validated, normalized, and runtime state is initialized.

> **TextProgram** marks `execute` as `@final`. Do not override it. Use the lifecycle hooks described below instead.

---

## Option Validation Lifecycle

All argument validation and normalization **must** be organized across these hooks:

### `check_option_dependencies(self)`

Enforce relationships between options.

Examples:

- one option requires another
- mutually exclusive semantic constraints

### `validate_option_ranges(self)`

Validate numeric and logical ranges.

Examples:

- `--count-width >= 1`
- `--skip-fields >= 1`

### `normalize_options(self)`

Apply derived defaults and convert values to internal form.

Examples:

- convert one-based indices to zero-based
- sort and deduplicate field lists
- infer default flags

### `initialize_runtime_state(self)`

Prepare internal state derived from options.

Handled automatically in `CLIProgram`:

- `use_color` — disabled when stdout is not connected to a terminal

Handled additionally in `TextProgram`:

- `encoding` — set to `iso-8859-1` when `--latin1` is set, otherwise `utf-8`

---

### From TextProgram

Text-processing programs **must implement**:

#### `handle_redirected_input(self, input_lines: Iterable[str]) -> None`

Process input received from redirected standard input.

- `input_lines` is a non-empty iterable of lines from stdin; iterate over it directly.
- Called only when stdin is redirected and `--stdin-files` is not set.
- Do not read from `sys.stdin` directly.

#### `handle_terminal_input(self) -> None`

Read and process input interactively from the terminal.

- Called only when stdin is not redirected and no file arguments are provided.
- Responsible for prompting or reading from the terminal as needed.

#### `process_input_file(self, input_file: InputFile) -> None`

Process a single text stream.

- `input_file.file_name` — normalized file name
- `input_file.text_stream` — open `TextIO` stream
- May raise `UnicodeDecodeError` (handled by the base class)
- Do **not** open files manually; use the provided stream.

---

## TextProgram Execution Flow

`TextProgram.execute` is final and manages input routing automatically:

```
stdin redirected?
    yes:
        --stdin-files set?
            yes → read file names from stdin, process each file
            no  → invoke handle_redirected_input() with stdin
        process any additional file arguments
    no:
        file arguments provided?
            yes → process each file
            no  → invoke handle_terminal_input()

post_execute() is always called after input processing completes.
```

---

## Optional Hooks

### `post_execute(self, processed_files: Collection[str]) -> None`

Called after all input has been processed.

- `processed_files` — names of files successfully processed during execution.
- Use this hook for post-processing, reporting, or summary output.
- Default implementation does nothing.

---

## Program Lifecycle

The following diagram shows the full execution lifecycle for all programs, from argument parsing through exit code
resolution.

```
parse arguments
→ option lifecycle
    check_option_dependencies
    validate_option_ranges
    normalize_options
    initialize_runtime_state
→ execute
    (TextProgram manages input routing here)
→ post_execute (TextProgram only)
→ exit_if_errors
```

---

## Implementation Checklist

### For all programs

- Inherit from `CLIProgram` or `TextProgram`
- Call `super().__init__(name=...)`
- Implement `build_arguments`
- Implement `execute` (CLIProgram only; TextProgram marks this `@final`)
- Use validation hooks appropriately
- Use `print_error` / `print_error_and_exit`
- Use `run()` in the entry point

### For text programs

- Inherit from `TextProgram`
- Implement `handle_redirected_input`
- Implement `handle_terminal_input`
- Implement `process_input_file`
- Optionally implement `post_execute` for post-processing or summary output
- Do not manually open text files
- Do not override `execute`

---

## Design Principles

- Follow the standard lifecycle; do not bypass `run()`
- Separate dependency checks, range validation, normalization, and runtime initialization
- Comments should explain intent, not mechanics
- Functions should read clearly, behave predictably, and have documentation that matches reality

---

## Versioning (Project-Wide)

Pyr-CLI uses a **single, project-wide version number**. Individual command-line programs **must not** define or hardcode
their own version values.

### Source of Truth

- The canonical version is stored in `pyrcli.__about__.__version__`.
- The base class (`CLIProgram`) assigns this value to `self.version` during initialization.
- Command implementations **must treat** `self.version` as **read-only**.

### Usage in Programs

- Do not import `__version__` in individual program modules.
- Use the `self.version` attribute provided by the base class.
- This ensures all commands report a consistent Pyr-CLI version and eliminates per-program version duplication.
- Programs that expose a `--version` flag must implement it using `version=f"%(prog)s {self.version}`".

### Rationale

This design provides:

- A single source of truth for versioning
- Zero boilerplate in command implementations
- Consistent CLI behavior across all Pyr-CLI programs

---

## Minimal Examples

### Non-text program

``` python
"""Implements a program that demos using progress indicators."""

import argparse
import sys
import time
from typing import NoReturn, override

from pyrcli.cli import CLIProgram
from pyrcli.cli.progress import ProgressBar, Spinner


class CLIProgramDemo(CLIProgram):
    """Command implementation for demoing progress indicators."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="demo")

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="demo using progress indicators",
                                         prog=self.name)

        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    @override
    def execute(self) -> None:
        """Execute the command using the prepared runtime state."""
        files = ("file_1", "file_2", "file_3", "file_4", "file_5", "file_6", "file_7", "file_8")
        files_to_update = len(files)

        # Find files to update.
        with Spinner(output_stream=sys.stdout, message_position="left",
                     final_message=f"Found {files_to_update} files that require an update.") as spin:
            for _ in range(files_to_update * 2):
                spin.advance(message="Finding files to update")
                time.sleep(0.125)  # Simulate finding a file.

        # Download updates.
        with ProgressBar(total=files_to_update, output_stream=sys.stdout, clear_on_finish=True,
                         final_message="Updates downloaded.") as bar:
            bar.start(message="Connecting to server...")
            time.sleep(.5)  # Simulate connecting to a server.

            for file_index, _ in enumerate(files, start=1):
                time.sleep(.5)  # Simulate downloading a file.
                bar.advance(message=f"Downloaded {file_index:>2} of {files_to_update}")

        # Apply updates.
        with ProgressBar(total=files_to_update, output_stream=sys.stdout, clear_on_finish=True,
                         final_message="Updates applied.") as bar:
            bar.start(message="Applying updates to files...")
            time.sleep(.25)  # Simulate starting the update process.

            for file_index, _ in enumerate(files, start=1):
                time.sleep(.25)  # Simulate updating a file.
                bar.advance(message=f"Updated {file_index:>2} of {files_to_update}")

        # Perform any cleanup.
        with Spinner(output_stream=sys.stdout, message_position="left") as spin:
            for _ in range(files_to_update):
                spin.advance(message="Cleaning up")
                time.sleep(0.125)  # Simulate cleaning up.

        # Print summary.
        print(f"Downloaded and updated {files_to_update} files:")

        for file_index, file_name in enumerate(files, start=1):
            print(f"{file_index:>2}: {file_name}")


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return CLIProgramDemo().run()


if __name__ == "__main__":
    raise SystemExit(main())
```

---

### Text-processing program

``` python
"""Implements a program that prints files to standard output."""

import argparse
import sys
from collections.abc import Iterable
from typing import Final, NoReturn, override

from pyrcli.cli import TextProgram, text
from pyrcli.cli.ansi import ForegroundColors
from pyrcli.cli.io import InputFile


class _Styles:
    """Namespace for ANSI styling constants."""
    COLON: Final[str] = ForegroundColors.BRIGHT_CYAN
    FILE_NAME: Final[str] = ForegroundColors.BRIGHT_MAGENTA


class TextProgramDemo(TextProgram):
    """Command implementation for printing files to standard output."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="demo")

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="print FILES to standard output",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        parser.add_argument("-H", "--no-file-name", action="store_true", help="suppress file name prefixes")
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for file names (default: on)")
        parser.add_argument("--latin1", action="store_true", help="read FILES as latin-1 (default: utf-8)")
        parser.add_argument("--stdin-files", action="store_true", help="read FILES from standard input (one per line)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        self.print_file_header(file_name="")
        self.print_lines(input_lines)

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        self.print_lines(sys.stdin)

    @override
    def normalize_options(self) -> None:
        """Apply derived defaults and adjust option values for consistent internal use."""
        # Suppress file headers when standard input is the only source.
        if not self.args.files and not self.args.stdin_files:
            self.args.no_file_name = True

    def print_file_header(self, file_name: str) -> None:
        """Print the rendered file header for ``file_name``."""
        if self.should_print_file_header():
            print(self.format_file_header(file_name, file_name_style=_Styles.FILE_NAME, colon_style=_Styles.COLON))

    @staticmethod
    def print_lines(lines: Iterable[str]) -> None:
        """Print lines to standard output."""
        for line in text.iter_normalized_lines(lines):
            print(line)

    @override
    def process_input_file(self, input_file: InputFile) -> None:
        """Process the text stream from ``input_file``."""
        self.print_file_header(input_file.file_name)
        self.print_lines(input_file.text_stream)


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return TextProgramDemo().run()


if __name__ == "__main__":
    raise SystemExit(main())
```
