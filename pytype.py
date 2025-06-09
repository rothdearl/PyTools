#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pytype.py
Author: Roth Earl
Version: 1.0.0
Description: A program to print the contents of files to standard output.
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
    COLON: Final[str] = "\x1b[96m"  # Bright cyan
    FILE_NAME: Final[str] = "\x1b[95m"  # Bright magenta
    LINE_NUMBER: Final[str] = "\x1b[92m"  # Bright green
    RESET: Final[str] = "\x1b[0m"
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
    line_start: int = 0
    lines: int = 0


@final
class Program:
    """
    Class for managing program constants.
    """
    NAME: Final[str] = "pytype"
    VERSION: Final[str] = "1.0.0"
    args: argparse.Namespace
    has_errors: bool = False


def main() -> None:
    """
    A program to print the contents of files to standard output.
    :return: None
    """
    parse_arguments()
    set_line_info_values()

    # Ensure color is only True if --color=on and the output is to the terminal.
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Set --no-file-header to True if there are no files.
    if not Program.args.files:
        Program.args.no_file_header = True

    # Check if the input is being redirected.
    if not sys.stdin.isatty():
        if Program.args.xargs:  # --xargs
            print_lines_from_files(sys.stdin)
        else:
            if standard_input := sys.stdin.readlines():
                print_file_header(file="")
                print_lines(standard_input, has_newlines=True)

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
    parser = argparse.ArgumentParser(allow_abbrev=False, description="print the contents of FILES to standard output",
                                     epilog="with no FILES, read standard input")

    parser.add_argument("files", help="files to print", metavar="FILES", nargs="*")
    parser.add_argument("-H", "--no-file-header", action="store_true", help="suppress the file name header on output")
    parser.add_argument("-l", "--line-number", action="store_true", help="print line number with output lines")
    parser.add_argument("-n", "--lines", help="print only N lines", metavar="N", nargs=1, type=int)
    parser.add_argument("-s", "--line-start", help="print at line n from the head or tail", metavar="±n", nargs=1,
                        type=int)
    parser.add_argument("--color", choices=("on", "off"), default="on",
                        help="print the file names and line numbers in color")
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


def print_file_header(file: str) -> None:
    """
    Prints the file name, or (standard input) if empty, with a colon.
    :param file: The file.
    :return: None
    """
    if not Program.args.no_file_header:  # --no-file-header
        file_name = os.path.relpath(file) if file else "(standard input)"

        if Colors.on:
            file_name = f"{Colors.FILE_NAME}{file_name}{Colors.COLON}:{Colors.RESET}"
        else:
            file_name = f"{file_name}:"

        print(file_name)


def print_lines(lines: list[str], *, has_newlines: bool) -> None:
    """
    Prints the lines.
    :param lines: The lines.
    :param has_newlines: Whether the lines end with a newline character.
    :return: None
    """
    line_number = 0
    line_start = len(lines) + LineInfo.line_start + 1 if LineInfo.line_start < 1 else LineInfo.line_start
    line_end = line_start + LineInfo.lines - 1
    print_end = "" if has_newlines else "\n"

    for line in lines:
        line_number += 1

        if line_start <= line_number <= line_end:
            if Program.args.line_number:  # --line-number
                width = 7

                if Colors.on:
                    line = f"{Colors.LINE_NUMBER}{line_number:>{width}}{Colors.COLON}:{Colors.RESET}{line}"
                else:
                    line = f"{line_number:>{width}}:{line}"

            print(line, end=print_end)


def print_lines_from_files(files: TextIO | list[str]) -> None:
    """
    Prints lines from files.
    :param files: The files.
    :return: None
    """
    encoding = "iso-8859-1" if Program.args.iso else "utf-8"  # --iso

    for file in files:
        file = file.rstrip("\n")

        try:
            if os.path.isdir(file):
                print_error_message(f"{file}: is a directory")
            else:
                with open(file, "r", encoding=encoding) as text:
                    print_file_header(file)
                    print_lines(text.readlines(), has_newlines=True)
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
    lines = []

    while not eof:
        try:
            lines.append(input())
        except EOFError:
            eof = True

    print_lines(lines, has_newlines=False)


def set_line_info_values() -> None:
    """
    Sets the values to use for printing lines.
    :return: None
    """
    LineInfo.line_start = 1 if not Program.args.line_start else Program.args.line_start[0]
    LineInfo.lines = sys.maxsize if not Program.args.lines else Program.args.lines[0]

    # Validate the values.
    if LineInfo.line_start == 0:
        print_error_message(f"line start ({LineInfo.line_start}) cannot be 0", raise_system_exit=True)

    if LineInfo.lines < 1:
        print_error_message(f"lines ({LineInfo.lines}) cannot be less than 1", raise_system_exit=True)


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
