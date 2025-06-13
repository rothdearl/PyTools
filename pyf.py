#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pyf.py
Author: Roth Earl
Version: 1.0.0
Description: A program to separate lines into fields.
License: GNU GPLv3
"""

import argparse
import os
import re
import sys
from typing import Final, TextIO, final


@final
class Colors:
    """
    Class for managing color constants.
    """
    COLON: Final[str] = "\x1b[96m"  # Bright cyan
    COUNT: Final[str] = "\x1b[92m"  # Bright green
    FILE_NAME: Final[str] = "\x1b[95m"  # Bright magenta
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
class FieldInfo:
    """
    Class for managing field constants.
    """
    DEFAULT_PATTERN: Final[str] = r"\s+"  # All whitespace.
    field_index_end: int = 0
    field_index_start: int = 0
    pattern: str = None
    quote: str = None
    separator: str = None


@final
class Program:
    """
    Class for managing program constants.
    """
    NAME: Final[str] = "pyf"
    VERSION: Final[str] = "1.0.0"
    args: argparse.Namespace = None
    has_errors: bool = False


def main() -> None:
    """
    A program to separate lines into fields.
    :return: None
    """
    parse_arguments()
    set_field_info_values()

    # Ensure Colors.on is only True if --color=on and the output is to the terminal.
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Set --no-file-header to True if there are no files and --xargs=False.
    if not Program.args.files and not Program.args.xargs:
        Program.args.no_file_header = True

    # Check if the input is being redirected.
    if not sys.stdin.isatty():
        if Program.args.xargs:  # --xargs
            separate_lines_from_files(sys.stdin)
        else:
            if standard_input := sys.stdin.readlines():
                print_file_header(file="")
                separate_lines(standard_input)

        if Program.args.files:  # Process any additional files.
            separate_lines_from_files(Program.args.files)
    elif Program.args.files:
        separate_lines_from_files(Program.args.files)
    else:
        separate_lines_from_input()


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description="separate lines in FILES into fields",
                                     epilog="with no FILES, read standard input")
    quote_group = parser.add_mutually_exclusive_group()

    parser.add_argument("files", help="files to separate lines", metavar="FILES", nargs="*")
    parser.add_argument("-b", "--no-blank", action="store_true", help="suppress blank lines")
    parser.add_argument("-c", "--count", action="store_true", help="prefix output with field count")
    parser.add_argument("-f", "--field-start", help="print at field N", metavar="N", nargs=1, type=int)
    parser.add_argument("-H", "--no-file-header", action="store_true", help="suppress the file name header on output")
    parser.add_argument("-n", "--fields", help="print only N fields", metavar="N", nargs=1, type=int)
    parser.add_argument("-p", "--pattern", help="find fields that match PATTERN", nargs=1)
    parser.add_argument("-s", "--separator", help="separate each field with α", metavar="α", nargs=1)
    quote_group.add_argument("-D", "--double-quote", action="store_true", help="print double quotes around fields")
    quote_group.add_argument("-S", "--single-quote", action="store_true", help="print single quotes around fields")
    parser.add_argument("--color", choices=("on", "off"), default="on",
                        help="print the counts and file headers in color")
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


def set_field_info_values() -> None:
    """
    Sets the values to use for separating lines.
    :return: None
    """
    field_start = 1 if not Program.args.field_start else Program.args.field_start[0]  # --field-start
    fields = sys.maxsize if not Program.args.fields else Program.args.fields[0]  # --fields

    # Validate the field values.
    if field_start < 1:
        print_error_message(f"field start ({field_start}) cannot be less than 1", raise_system_exit=True)

    if fields < 1:
        print_error_message(f"fields ({fields}) cannot be less than 1", raise_system_exit=True)

    # Store the field values.
    FieldInfo.field_index_end = field_start - 1 + fields
    FieldInfo.field_index_start = field_start - 1
    FieldInfo.pattern = FieldInfo.DEFAULT_PATTERN if not Program.args.pattern else Program.args.pattern[0]  # --pattern
    FieldInfo.quote = "\"" if Program.args.double_quote else "'" if Program.args.single_quote else ""  # --double-quote or --single-quote
    FieldInfo.separator = "\t" if not Program.args.separator else Program.args.separator[0]  # --separator


def separate_lines(lines: TextIO | list[str]) -> None:
    """
    Separates the lines into fields.
    :param lines: The lines.
    :return: None
    """
    for line in lines:
        fields = split_fields(line, FieldInfo.pattern)

        if Program.args.no_blank and not fields:  # --no-blank
            continue

        if Program.args.count:  # --count
            count = len(fields)
            width = 4

            if Colors.on:
                count_str = f"{Colors.COUNT}{count:>{width}}{Colors.COLON}:{Colors.RESET}"
            else:
                count_str = f"{count:>{width}}:"

            print(count_str, end="")

        for index, field in enumerate(fields):
            print_end = FieldInfo.separator if index < len(fields) - 1 else ""

            print(f"{FieldInfo.quote}{field}{FieldInfo.quote}", end=print_end)

        print()


def separate_lines_from_files(files: TextIO | list[str]) -> None:
    """
    Separates lines into fields from files.
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
                    separate_lines(text)
        except FileNotFoundError:
            print_error_message(f"{file if file else "\"\""}: no such file or directory")
        except PermissionError:
            print_error_message(f"{file}: permission denied")
        except OSError:
            print_error_message(f"{file}: unable to read file")
        except UnicodeDecodeError:
            print_error_message(f"{file}: unable to decode file")


def separate_lines_from_input() -> None:
    """
    Separates lines into fields from standard input until EOF is entered.
    :return: None
    """
    eof = False
    lines = []

    while not eof:
        try:
            lines.append(input())
        except EOFError:
            eof = True

    separate_lines(lines)


def split_fields(line: str, field_pattern: str) -> list[str]:
    """
    Splits the line into a list of fields.
    :param line: The line.
    :param field_pattern: The pattern for splitting fields.
    :return: A list of fields.
    """
    fields = []

    # Strip leading and trailing whitespace.
    line = line.strip()

    # Split line into fields.
    try:
        for field in re.split(field_pattern, line):
            if field:
                fields.append(field)
    except re.error:
        print_error_message(f"invalid regex pattern: {field_pattern}", raise_system_exit=True)

    return fields[FieldInfo.field_index_start:FieldInfo.field_index_end]


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
