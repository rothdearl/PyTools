#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pyniq.py
Author: Roth Earl
Version: 1.0.0
Description: A program to filter matching lines in files.
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
    FILE_NAME: Final[str] = "\x1b[95m"  # Bright magenta
    GROUP_COUNT: Final[str] = "\x1b[92m"  # Bright green
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
class MatchInfo:
    """
    Class for managing match constants.
    """
    FIELD_PATTERN: Final[str] = r"\s+|\W+"
    max_chars: int = 0
    skip_chars: int = 0
    skip_fields: int = 0


@final
class Program:
    """
    Class for managing program constants.
    """
    NAME: Final[str] = "pyniq"
    VERSION: Final[str] = "1.0.0"
    args: argparse.Namespace
    has_errors: bool = False


def filter_matching_lines(lines: TextIO | list[str], *, has_newlines: bool, origin_file) -> None:
    """
    Filters lines that match.
    :param lines: The lines.
    :param has_newlines: Whether the lines end with a newline character.
    :param origin_file: The file where the lines originated from.
    :return: None
    """
    file_header_printed = False
    print_end = "" if has_newlines else "\n"

    # Group matches.
    if Program.args.adjacent:
        groups = group_adjacent_matching_lines(lines)
    else:
        groups = group_all_matching_lines(lines).values()

    # Print groups.
    last_group_index = len(groups) - 1

    for group_index, group in enumerate(groups):
        group_count = len(group)

        for line_index, line in enumerate(group):
            can_print = True
            group_count_str = ""

            if Program.args.count:  # --count
                width = 7

                # Only print the group count for the first line.
                if line_index == 0:
                    if Colors.on:
                        group_count_str = f"{Colors.GROUP_COUNT}{group_count:>{width},}{Colors.COLON}:{Colors.RESET}"
                    else:
                        group_count_str = f"{group_count:>{width},}:"
                else:
                    space = " "
                    group_count_str = f"{space:>{width}} "

            if Program.args.duplicate or Program.args.repeated:  # --duplicate or --repeated
                can_print = group_count > 1
            elif Program.args.unique:  # --unique
                can_print = group_count == 1

            if can_print:
                if not file_header_printed:
                    print_file_header(origin_file)
                    file_header_printed = True

                print(f"{group_count_str}{line}", end=print_end)

                if not (Program.args.duplicate or Program.args.group):  # --duplicate or --group
                    break

        if Program.args.group and group_index < last_group_index:  # --group
            print()


def filter_matching_lines_from_files(files: TextIO | list[str]) -> None:
    """
    Filters lines that match from files.
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
                    filter_matching_lines(text, has_newlines=True, origin_file=file)
        except FileNotFoundError:
            print_error_message(f"{file if file else "\"\""}: no such file or directory")
        except PermissionError:
            print_error_message(f"{file}: permission denied")
        except OSError:
            print_error_message(f"{file}: unable to read file")
        except UnicodeDecodeError:
            print_error_message(f"{file}: unable to decode file")


def filter_matching_lines_from_input() -> None:
    """
    Filters lines that match from standard input until EOF is entered.
    :return: None
    """
    eof = False
    lines = []

    while not eof:
        try:
            lines.append(input())
        except EOFError:
            eof = True

    filter_matching_lines(lines, has_newlines=False, origin_file="")


def get_character_compare_sequence(line: str) -> str:
    """
    Returns the character sequence from the line to use for comparing.
    :param line: The line.
    :return: The character sequence to use for comparing.
    """
    if Program.args.skip_whitespace:  # --skip-whitespace
        line = line.strip()

    if Program.args.skip_fields:  # --skip-fields
        line = "".join(re.split(MatchInfo.FIELD_PATTERN, line)[MatchInfo.skip_fields:])

    if Program.args.max_chars or Program.args.skip_chars:  # --max_chars or --skip_chars
        start_index = MatchInfo.skip_chars
        end_index = start_index + MatchInfo.max_chars if Program.args.max_chars else len(line)

        line = line[start_index:end_index]

    if Program.args.ignore_case:  # --ignore-case
        line = line.casefold()

    return line


def group_adjacent_matching_lines(lines: TextIO | list[str]) -> list[list[str]]:
    """
    Groups adjacent lines that match.
    :param lines: The lines.
    :return: A list of lines where the first element is the group and the remaining elements are the matching lines.
    """
    group_index = 0
    group_list = []
    previous_line = None

    for line in lines:
        next_line = get_character_compare_sequence(line)

        if Program.args.skip_blank and (not next_line or next_line == "\n"):  # --skip-blank
            continue

        if previous_line is None:
            group_list.append([line])
        elif next_line == previous_line:
            group_list[group_index].append(line)
        else:
            group_index += 1
            group_list.append([line])

        previous_line = next_line

    return group_list


def group_all_matching_lines(lines: TextIO | list[str]) -> dict[str, list[str]]:
    """
    Groups all lines that match.
    :param lines: The lines.
    :return: A mapping of lines where the key is the group and the values are the matching lines.
    """
    group_map = {}

    for line in lines:
        key = get_character_compare_sequence(line)

        if Program.args.skip_blank and (not key or key == "\n"):  # --skip-blank
            continue

        if Program.args.ignore_case and key in (k.casefold() for k in group_map.keys()):  # --ignore-case
            group_map[key].append(line)
        elif key in group_map:
            group_map[key].append(line)
        else:
            group_map[key] = [line]

    return group_map


def main() -> None:
    """
    A program to filter matching lines in files.
    :return: None
    """
    parse_arguments()
    set_match_info_values()

    # Ensure color is only True if --color=on and the output is to the terminal.
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Set --no-file-header to True if there are no files.
    if not Program.args.files:
        Program.args.no_file_header = True

    # Check if the input is being redirected.
    if not sys.stdin.isatty():
        if Program.args.xargs:  # --xargs
            filter_matching_lines_from_files(sys.stdin)
        else:
            if standard_input := sys.stdin.readlines():
                filter_matching_lines(standard_input, has_newlines=True, origin_file="")

        if Program.args.files:  # Process any additional files.
            filter_matching_lines_from_files(Program.args.files)
    elif Program.args.files:
        filter_matching_lines_from_files(Program.args.files)
    else:
        filter_matching_lines_from_input()


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description="filter matching lines in FILES",
                                     epilog="with no FILES, read standard input")
    print_group = parser.add_mutually_exclusive_group()

    parser.add_argument("files", help="files to filter", metavar="FILES", nargs="*")
    parser.add_argument("-a", "--adjacent", action="store_true", help="only filter matching adjacent lines")
    parser.add_argument("-b", "--skip-blank", action="store_true", help="avoid comparing blank lines")
    parser.add_argument("-c", "--count", action="store_true", help="prefix lines by the number of occurrences")
    parser.add_argument("-f", "--skip-fields", help="avoid comparing the first N fields", metavar="N", nargs=1,
                        type=int)
    parser.add_argument("-H", "--no-file-header", action="store_true", help="suppress the file name header on output")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore differences in case when comparing")
    parser.add_argument("-m", "--max-chars", help="compare no more than N characters", metavar="N", nargs=1, type=int)
    parser.add_argument("-s", "--skip-chars", help="avoid comparing the first N characters", metavar="N", nargs=1,
                        type=int)
    parser.add_argument("-w", "--skip-whitespace", action="store_true",
                        help="avoid comparing leading and trailing whitespace")
    print_group.add_argument("-d", "--repeated", action="store_true",
                             help="only print duplicate lines, one for each group")
    print_group.add_argument("-D", "--duplicate", action="store_true", help="print all duplicate lines")
    print_group.add_argument("-g", "--group", action="store_true",
                             help="show all items, separating groups with an empty line")
    print_group.add_argument("-u", "--unique", action="store_true", help="only print unique lines")
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


def set_match_info_values() -> None:
    """
    Sets the values to use for matching lines.
    :return: None
    """
    MatchInfo.max_chars = 1 if not Program.args.max_chars else Program.args.max_chars[0]  # --max-chars
    MatchInfo.skip_chars = 0 if not Program.args.skip_chars else Program.args.skip_chars[0]  # --skip-chars
    MatchInfo.skip_fields = 0 if not Program.args.skip_fields else Program.args.skip_fields[0]  # --skip-fields

    # Validate the values.
    if MatchInfo.skip_fields < 0:
        print_error_message(f"skip fields ({MatchInfo.skip_fields}) cannot be less than 0", raise_system_exit=True)

    if MatchInfo.skip_chars < 0:
        print_error_message(f"skip characters ({MatchInfo.skip_chars}) cannot be less than 0", raise_system_exit=True)

    if MatchInfo.max_chars < 1:
        print_error_message(f"max characters ({MatchInfo.max_chars}) cannot be less than 1", raise_system_exit=True)


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
