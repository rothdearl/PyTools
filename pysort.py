#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pysort.py
Author: Roth Earl
Version: 0.1.3
Description: A program to sort and print files to standard output.
License: GNU GPLv3
"""

import argparse
import os
import random
import re
import sys
from typing import Final, TextIO, final

from dateutil.parser import ParserError, parse


@final
class Colors:
    """
    Class for managing color constants.
    """
    COLON: Final[str] = "\x1b[96m"  # Bright cyan
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
    DATE_PATTERN: Final[str] = r"[\f\r\n\t\v]"  # All whitespace except spaces.
    DEFAULT_PATTERN: Final[str] = r"[ ]"  # All spaces.
    WORDS_PATTERN: Final[str] = r"\s+|\W+"  # All whitespace and non-words.
    skip_fields: int = 0


@final
class Program:
    """
    Class for managing program constants.
    """
    NAME: Final[str] = "pysort"
    VERSION: Final[str] = "0.1.3"
    args: argparse.Namespace = None
    has_errors: bool = False


def get_date_sort_key(line: str) -> str:
    """
    Returns the date sort key.
    :param line: The line.
    :return: The date sort key.
    """
    fields = get_fields(line, FieldInfo.DATE_PATTERN)

    try:
        if fields:
            date = str(parse(fields[0]))
        else:
            date = line
    except ParserError:
        date = line

    return date


def get_default_sort_key(line: str) -> list[str]:
    """
    Returns the default sort key.
    :param line: The line.
    :return: The default sort key.
    """
    return get_fields(line, FieldInfo.DEFAULT_PATTERN)


def get_dictionary_sort_key(line: str) -> list[str]:
    """
    Returns the dictionary sort key.
    :param line: The line.
    :return: The dictionary sort key.
    """
    return get_fields(line, FieldInfo.WORDS_PATTERN)


def get_fields(line: str, field_pattern: str, *, strip_number_separators: bool = False) -> list[str]:
    """
    Returns a list of fields from the line.
    :param line: The line.
    :param field_pattern: The pattern for getting fields.
    :param strip_number_separators: Whether to strip number separators (commas and decimals).
    :return: A list of fields from the line.
    """
    fields = []

    # Strip leading and trailing whitespace.
    line = line.strip()

    # Strip commas and decimals.
    if strip_number_separators:
        line = line.replace(",", "").replace(".", "")

    for index, field in enumerate(re.split(field_pattern, line)):
        if field and index >= FieldInfo.skip_fields:
            fields.append(field.casefold() if Program.args.ignore_case else field)  # --ignore-case

    return fields


def get_natural_sort_key(line: str) -> list[str]:
    """
    Returns the natural sort key.
    :param line: The line.
    :return: The natural sort key.
    """
    numbers_and_words = []

    for field in get_fields(line, FieldInfo.WORDS_PATTERN, strip_number_separators=True):
        # Zero-pad integers so they sort numerically.
        if field.isdigit():
            field = f"{field:0>20}"

        numbers_and_words.append(field)

    return numbers_and_words


def main() -> None:
    """
     A program to sort and print files to standard output.
    :return: None
    """
    parse_arguments()
    set_sort_info_values()

    # Ensure Colors.on is only True if --color=on and the output is to the terminal.
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Set --ignore-case to True if --dictionary-sort=True or --natural-sort=True.
    if Program.args.dictionary_sort or Program.args.natural_sort:
        Program.args.ignore_case = True

    # Set --no-file-header to True if there are no files and --xargs=False.
    if not Program.args.files and not Program.args.xargs:
        Program.args.no_file_header = True

    # Check if the input is being redirected.
    if not sys.stdin.isatty():
        if Program.args.xargs:  # --xargs
            sort_lines_from_files(sys.stdin)
        else:
            if standard_input := sys.stdin.readlines():
                print_file_header(file="")
                sort_lines(standard_input, has_newlines=True)

        if Program.args.files:  # Process any additional files.
            sort_lines_from_files(Program.args.files)
    elif Program.args.files:
        sort_lines_from_files(Program.args.files)
    else:
        sort_lines_from_input()


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description="sort and print FILES to standard output",
                                     epilog="with no FILES, read standard input")
    sort_group = parser.add_mutually_exclusive_group()

    parser.add_argument("files", help="files to sort and print", metavar="FILES", nargs="*")
    parser.add_argument("-b", "--no-blank", action="store_true", help="suppress blank lines")
    parser.add_argument("-f", "--skip-fields", help="avoid comparing the first N fields", metavar="N", nargs=1,
                        type=int)
    parser.add_argument("-H", "--no-file-header", action="store_true", help="suppress the file name header on output")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore differences in case when comparing")
    parser.add_argument("-r", "--reverse", action="store_true", help="reverse the result of comparisons")
    sort_group.add_argument("-d", "--dictionary-sort", action="store_true", help="compare lines lexicographically")
    sort_group.add_argument("-D", "--date-sort", action="store_true", help="compare dates from newest to oldest")
    sort_group.add_argument("-n", "--natural-sort", action="store_true",
                            help="compare words alphabetically and numbers numerically")
    sort_group.add_argument("-R", "--random-sort", action="store_true", help="randomize the result of comparisons")
    parser.add_argument("--color", choices=("on", "off"), default="on", help="print the file names in color")
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


def set_sort_info_values() -> None:
    """
    Sets the values to use for sorting lines.
    :return: None
    """
    FieldInfo.skip_fields = 0 if not Program.args.skip_fields else Program.args.skip_fields[0]  # --skip-fields

    # Validate the values.
    if FieldInfo.skip_fields < 0:
        print_error_message(f"skip fields ({FieldInfo.skip_fields}) cannot be less than 0", raise_system_exit=True)


def sort_lines(lines: list[str], *, has_newlines: bool) -> None:
    """
    Sorts the lines.
    :param lines: The lines.
    :param has_newlines: Whether the lines end with a newline character.
    :return: None
    """
    print_end = "" if has_newlines else "\n"

    # Sort lines.
    if Program.args.date_sort:  # --date-sort
        lines.sort(key=get_date_sort_key, reverse=Program.args.reverse)
    elif Program.args.dictionary_sort:  # --dictionary-sort
        lines.sort(key=get_dictionary_sort_key, reverse=Program.args.reverse)
    elif Program.args.natural_sort:  # --natural-sort
        lines.sort(key=get_natural_sort_key, reverse=Program.args.reverse)
    elif Program.args.random_sort:  # --random-sort
        random.shuffle(lines)
    else:
        lines.sort(key=get_default_sort_key, reverse=Program.args.reverse)

    # Print lines.
    for line in lines:
        can_print = False if Program.args.no_blank and not line.rstrip() else True  # --no-blank

        if can_print:
            print(line, end=print_end)


def sort_lines_from_files(files: TextIO | list[str]) -> None:
    """
    Sorts lines from files.
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
                    sort_lines(text.readlines(), has_newlines=True)
        except FileNotFoundError:
            print_error_message(f"{file if file else "\"\""}: no such file or directory")
        except PermissionError:
            print_error_message(f"{file}: permission denied")
        except OSError:
            print_error_message(f"{file}: unable to read file")
        except UnicodeDecodeError:
            print_error_message(f"{file}: unable to decode file")


def sort_lines_from_input() -> None:
    """
    Sorts lines from standard input until EOF is entered.
    :return: None
    """
    eof = False
    lines = []

    while not eof:
        try:
            lines.append(input())
        except EOFError:
            eof = True

    sort_lines(lines, has_newlines=False)


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
