#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pysort.py
Author: Roth Earl
Version: 1.0.0
Description: A program to sort and print files to standard output.
License: GNU GPLv3
"""

import argparse
import os
import random
import re
import sys
from typing import Final, TextIO, final


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
class Program:
    """
    Class for managing program constants.
    """
    NAME: Final[str] = "pysort"
    VERSION: Final[str] = "1.0.0"
    args: argparse.Namespace
    has_errors: bool = False


@final
class SortInfo:
    """
    Class for managing sort constants.
    """
    DIGIT_PATTERN: Final[str] = r"(\d+)"
    FIELD_PATTERN: Final[str] = r"\s+|\W+"
    max_chars: int = 0
    skip_chars: int = 0
    skip_fields: int = 0


def get_character_compare_sequence(line: str) -> str:
    """
    Returns the character sequence from the line to use for comparing.
    :param line: The line.
    :return: The character sequence to use for comparing.
    """
    if Program.args.ignore_blanks:  # --ignore-blanks
        line = line.strip()

    if Program.args.skip_fields:  # --skip-fields
        line = "".join(re.split(SortInfo.FIELD_PATTERN, line)[SortInfo.skip_fields:])

    if Program.args.max_chars or Program.args.skip_chars:  # --max_chars or --skip_chars
        start_index = SortInfo.skip_chars
        end_index = start_index + SortInfo.max_chars if Program.args.max_chars else len(line)

        line = line[start_index:end_index]

    if Program.args.ignore_case:  # --ignore-case
        line = line.casefold()

    return line


def get_dictionary_order_key(line: str) -> str:
    """
    Returns the dictionary order key.
    :param line: The line.
    :return: The dictionary order key.
    """
    line = get_character_compare_sequence(line)

    # Ensure non-alphanumeric characters sort to the top.
    if line and not line[0].isalnum():
        line = f"{chr(0)}{line}"

    return line.casefold()


def get_natural_order_key(line: str) -> list[int | str]:
    """
    Returns the natural order key.
    :param line: The line.
    :return: The natural order key.
    """
    line = get_character_compare_sequence(line)

    return [int(t) if t.isdigit() else t.casefold() for t in re.split(SortInfo.DIGIT_PATTERN, line)]


def main() -> None:
    """
     A program to sort and print files to standard output.
    :return: None
    """
    parse_arguments()
    set_sort_info_values()

    # Ensure color is only True if --color=on and the output is to the terminal.
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Set --no-file-header to True if there are no files.
    Program.args.no_file_header = not Program.args.files

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
    parser.add_argument("-b", "--ignore-blanks", action="store_true", help="ignore blanks when comparing")
    parser.add_argument("-f", "--skip-fields", help="avoid comparing the first N fields", metavar="N", nargs=1,
                        type=int)
    parser.add_argument("-H", "--no-file-header", action="store_true", help="suppress the file name header on output")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore differences in case when comparing")
    parser.add_argument("-m", "--max-chars", help="compare no more than N characters", metavar="N", nargs=1, type=int)
    parser.add_argument("-r", "--reverse", action="store_true", help="reverse the result of comparisons")
    parser.add_argument("-s", "--skip-chars", help="avoid comparing the first N characters", metavar="N", nargs=1,
                        type=int)
    sort_group.add_argument("-d", "--dictionary-order", action="store_true", help="compare lines lexicographically")
    sort_group.add_argument("-n", "--natural-order", action="store_true",
                            help="compare words alphabetically and numbers numerically")
    sort_group.add_argument("-R", "--random-order", action="store_true", help="randomize the result of comparisons")
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
    SortInfo.max_chars = 1 if not Program.args.max_chars else Program.args.max_chars[0]  # --max-chars
    SortInfo.skip_chars = 0 if not Program.args.skip_chars else Program.args.skip_chars[0]  # --skip-chars
    SortInfo.skip_fields = 0 if not Program.args.skip_fields else Program.args.skip_fields[0]  # --skip-fields

    # Validate the values.
    if SortInfo.skip_fields < 0:
        print_error_message(f"skip fields ({SortInfo.skip_fields}) cannot be less than 0", raise_system_exit=True)

    if SortInfo.skip_chars < 0:
        print_error_message(f"skip characters ({SortInfo.skip_chars}) cannot be less than 0", raise_system_exit=True)

    if SortInfo.max_chars < 1:
        print_error_message(f"max characters ({SortInfo.max_chars}) cannot be less than 1", raise_system_exit=True)


def sort_lines(lines: list[str], *, has_newlines: bool) -> None:
    """
    Sorts the lines.
    :param lines: The lines.
    :param has_newlines: Whether the lines end with a newline character.
    :return: None
    """
    print_end = "" if has_newlines else "\n"

    # Sort lines.
    if Program.args.random_order:  # --random-order
        random.shuffle(lines)
    elif Program.args.dictionary_order:  # --dictionary-order
        lines.sort(key=get_dictionary_order_key, reverse=Program.args.reverse)
    elif Program.args.natural_order:  # --natural-order
        lines.sort(key=get_natural_order_key, reverse=Program.args.reverse)
    else:
        lines.sort(key=get_character_compare_sequence, reverse=Program.args.reverse)

    # Print lines.
    for line in lines:
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
