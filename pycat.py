#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pycat.py
Author: Roth Earl
Version: 1.0.1
Description: A program to concatenate files to standard output.
License: GNU GPLv3
"""

import argparse
import os
import sys
from typing import Final, TextIO, final


@final
class Colors:
    """
    Class for managing color constants.
    """
    EOL: Final[str] = "\x1b[94m"  # Bright blue
    NUMBER: Final[str] = "\x1b[92m"  # Bright green
    RESET: Final[str] = "\x1b[0m"
    WHITESPACE: Final[str] = "\x1b[96m"  # Bright cyan
    on: bool = False


@final
class ExitCodes:
    """
    Class for managing exit code constants.
    """
    ERROR: Final[int] = 1
    KEYBOARD_INTERRUPT: Final[int] = 130


@final
class LineInfo:
    """
    Class for managing line constants.
    """
    number: int = 0
    repeated_blank_lines: int = 0


@final
class Program:
    """
    Class for managing program constants.
    """
    NAME: Final[str] = "pycat"
    VERSION: Final[str] = "1.0.1"
    args: argparse.Namespace = None
    has_errors: bool = False


@final
class Whitespace:
    """
    Class for managing whitespace constants.
    """
    EOL: Final[str] = "$"
    SPACE: Final[str] = "~"
    TAB: Final[str] = ">···"


def main() -> None:
    """
    A program to concatenate files to standard output.
    :return: None
    """
    parse_arguments()

    # Ensure Colors.on is only True if --color=on and the output is to the terminal.
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Check if the input is being redirected.
    if not sys.stdin.isatty():
        if Program.args.xargs:  # --xargs
            print_lines_from_files(sys.stdin.readlines())
        else:
            print_lines(sys.stdin, has_newlines=True)

        if Program.args.files:  # Process any additional files.
            print_lines_from_files(Program.args.files)
    elif Program.args.files:
        print_lines_from_files(Program.args.files)
    else:
        print_lines_from_input()


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description="concatenate FILES to standard output",
                                     epilog="with no FILES, read standard input")
    blank = parser.add_mutually_exclusive_group()
    number = parser.add_mutually_exclusive_group()

    parser.add_argument("files", help="files to concatenate", metavar="FILES", nargs="*")
    number.add_argument("-b", "--number-nonblank", action="store_true", help="number nonblank output lines")
    parser.add_argument("-g", "--group", action="store_true", help="separate files with an empty line")
    number.add_argument("-n", "--number", action="store_true", help="number all output lines")
    parser.add_argument("-E", "--show-ends", action="store_true", help=f"display {Whitespace.EOL} at end of each line")
    blank.add_argument("-B", "--no-blank", action="store_true", help="suppress blank lines")
    blank.add_argument("-s", "--squeeze-blank", action="store_true", help="suppress repeated blank lines")
    parser.add_argument("-S", "--spaces", action="store_true", help=f"display spaces as {Whitespace.SPACE}")
    parser.add_argument("-T", "--tabs", action="store_true", help=f"display tab characters as {Whitespace.TAB}")
    parser.add_argument("--color", choices=("on", "off"), default="on",
                        help="display the spaces, tabs, end of line, and numbers in color")
    parser.add_argument("--iso", action="store_true", help="use iso-8859-1 instead of utf-8 when reading files")
    parser.add_argument("--xargs", action="store_true", help="read FILES from standard input")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {Program.VERSION}")

    # Parse the arguments.
    Program.args = parser.parse_args()


def print_error_message(error_message: str, *, raise_system_exit: bool = False) -> None:
    """
    Prints an error message.
    :param error_message: The error message.
    :param raise_system_exit: Whether to raise a SystemExit; default is False.
    :return: None
    :raises SystemExit: Request to exit from the interpreter if raise_system_exit = True.
    """
    Program.has_errors = True
    print(f"{Program.NAME}: {error_message}", file=sys.stderr)

    if raise_system_exit:
        raise SystemExit(ExitCodes.ERROR)


def print_lines(lines: TextIO | list[str], *, has_newlines: bool) -> None:
    """
    Prints the lines.
    :param lines: The lines.
    :param has_newlines: Whether the lines end with a newline character.
    :return: None
    """
    print_end = "" if has_newlines else "\n"
    print_number = False

    for line in lines:
        LineInfo.number += 1

        # --number or --number-nonblank
        if Program.args.number or Program.args.number_nonblank:
            print_number = True

        if not line or line == "\n":
            LineInfo.repeated_blank_lines += 1

            # --number-nonblank
            if Program.args.number_nonblank:
                LineInfo.number -= 1
                print_number = False

            # --no-blank
            if Program.args.no_blank and LineInfo.repeated_blank_lines:
                continue

            # --squeeze-blank
            if Program.args.squeeze_blank and LineInfo.repeated_blank_lines > 1:
                continue
        else:
            LineInfo.repeated_blank_lines = 0

        if Program.args.spaces:  # Option: --spaces
            if Colors.on:
                line = line.replace(" ", f"{Colors.WHITESPACE}{Whitespace.SPACE}{Colors.RESET}")
            else:
                line = line.replace(" ", Whitespace.SPACE)

        if Program.args.tabs:  # Option: --tabs
            if Colors.on:
                line = line.replace("\t", f"{Colors.WHITESPACE}{Whitespace.TAB}{Colors.RESET}")
            else:
                line = line.replace("\t", Whitespace.TAB)

        if Program.args.show_ends:  # Option: --show-ends
            end_index = -1 if line.endswith("\n") else len(line)
            newline = "\n" if end_index == -1 else ""

            if Colors.on:
                line = f"{line[:end_index]}{Colors.EOL}{Whitespace.EOL}{Colors.RESET}{newline}"
            else:
                line = f"{line[:end_index]}{Whitespace.EOL}{newline}"

        if print_number:
            width = 7

            if Colors.on:
                line = f"{Colors.NUMBER}{LineInfo.number:>{width}}{Colors.RESET} {line}"
            else:
                line = f"{LineInfo.number:>{width}} {line}"

        print(line, end=print_end)


def print_lines_from_files(files: list[str]) -> None:
    """
    Prints lines from files.
    :param files: The files.
    :return: None
    """
    encoding = "iso-8859-1" if Program.args.iso else "utf-8"  # --iso
    last_file_index = len(files) - 1

    for index, file in enumerate(files):
        file = file.rstrip("\n")

        try:
            if os.path.isdir(file):
                print_error_message(f"{file}: is a directory")
            else:
                with open(file, "r", encoding=encoding) as text:
                    print_lines(text, has_newlines=True)

                    if Program.args.group and index < last_file_index:  # --group
                        print()
        except FileNotFoundError:
            print_error_message(f"{file if file else "\"\""}: no such file or directory")
        except PermissionError:
            print_error_message(f"{file}: permission denied")
        except OSError:
            print_error_message(f"{file}: unable to read file")
        except UnicodeDecodeError:
            print_error_message(f"{file}: unable to decode file")


def print_lines_from_input() -> None:
    """
    Prints lines from standard input until EOF is entered.
    :return: None
    """
    eof = False

    while not eof:
        try:
            print_lines([input()], has_newlines=False)
        except EOFError:
            eof = True


if __name__ == "__main__":
    windows = os.name == "nt"

    try:
        # Fix ANSI escape sequences on Windows.
        if windows:
            from colorama import just_fix_windows_console

            just_fix_windows_console()

        # Prevent a broken pipe error (not supported on Windows).
        if not windows:
            from signal import SIG_DFL, SIGPIPE, signal

            signal(SIGPIPE, SIG_DFL)

        main()

        if Program.has_errors:
            raise SystemExit(ExitCodes.ERROR)
    except KeyboardInterrupt:
        print()  # Add a newline after Ctrl-C.
        raise SystemExit(ExitCodes.ERROR if windows else ExitCodes.KEYBOARD_INTERRUPT)
    except OSError:
        raise SystemExit(ExitCodes.ERROR)
