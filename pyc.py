#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pyc.py
Author: Roth Earl
Version: 1.0.2
Description: A program to print line, word and character counts in files.
License: GNU GPLv3
"""

import argparse
import os
import re
import sys
from typing import Final, TextIO, final

# Define type aliases.
Stats = tuple[int, int, int, int]


@final
class Colors:
    """
    Class for managing color constants.
    """
    RESET: Final[str] = "\x1b[0m"
    STAT: Final[str] = "\x1b[96m"  # Bright cyan
    STAT_ORIGIN: Final[str] = "\x1b[95m"  # Bright magenta
    STAT_TOTAL: Final[str] = "\x1b[93m"  # Bright yellow
    on: bool = False


@final
class CountInfo:
    """
    Class for managing count constants.
    """
    OPTIONS: Final[list[bool]] = [False, False, False, False]
    TOTALS: Final[list[int]] = [0, 0, 0, 0]
    WORD_PATTERN: Final[str] = r"\b\w+\b"
    files_counted: int = 0
    options_count: int = 0
    tab_width: int = 8


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
    NAME: Final[str] = "pyc"
    VERSION: Final[str] = "1.0.2"
    args: argparse.Namespace = None
    has_errors: bool = False


@final
class StatIndexes:
    """
    Class for managing stat index constants.
    """
    LINES: Final[int] = 0
    WORDS: Final[int] = 1
    CHARACTERS: Final[int] = 2
    MAX_LINE_LENGTH: Final[int] = 3


def add_stats_to_totals(stats: Stats) -> None:
    """
    Adds the stats to the totals.
    :param stats: The stats.
    :return: None
    """
    CountInfo.TOTALS[StatIndexes.LINES] += stats[StatIndexes.LINES]
    CountInfo.TOTALS[StatIndexes.WORDS] += stats[StatIndexes.WORDS]
    CountInfo.TOTALS[StatIndexes.CHARACTERS] += stats[StatIndexes.CHARACTERS]

    if stats[StatIndexes.MAX_LINE_LENGTH] > CountInfo.TOTALS[StatIndexes.MAX_LINE_LENGTH]:
        CountInfo.TOTALS[StatIndexes.MAX_LINE_LENGTH] = stats[StatIndexes.MAX_LINE_LENGTH]


def get_stats(text: TextIO | list[str]) -> Stats:
    """
    Returns the counts for the lines, words, characters and the maximum line length in the text.
    :param text: The text.
    :return: The stats.
    """
    character_count = 0
    line_count = 0
    max_line_length = 0
    words = 0

    for line in text:
        line_length = len(line)
        max_display_width = line_length + (line.count("\t") * CountInfo.tab_width) - 1  # -1 for the newline.

        character_count += line_length
        line_count += 1
        words += len(re.findall(CountInfo.WORD_PATTERN, line))

        if max_display_width > max_line_length:
            max_line_length = max_display_width

    return line_count, words, character_count, max_line_length


def main() -> None:
    """
    A program to print line, word and character counts in files.
    :return: None
    """
    parse_arguments()
    set_count_info_values()

    # Ensure Colors.on is only True if --color=on and the output is to the terminal.
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Check if the input is being redirected.
    if not sys.stdin.isatty():
        if Program.args.xargs:  # --xargs
            print_stats_from_files(sys.stdin)
        else:
            if standard_input := sys.stdin.readlines():
                stats = get_stats(standard_input)

                CountInfo.files_counted += 1
                add_stats_to_totals(stats)
                print_stats(stats, stat_origin="(standard input)" if Program.args.files else "")

        if Program.args.files:  # Process any additional files.
            print_stats_from_files(Program.args.files)
    elif Program.args.files:
        print_stats_from_files(Program.args.files)
    else:
        print_stats_from_input()

    if Program.args.total and CountInfo.files_counted > 1:  # --total
        print_stats(CountInfo.TOTALS, stat_origin="total")


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description="print line, word and character counts in FILES",
                                     epilog="with no FILES, read standard input")

    parser.add_argument("files", help="files to count", metavar="FILES", nargs="*")
    parser.add_argument("-c", "--chars", action="store_true", help="print the character counts")
    parser.add_argument("-l", "--lines", action="store_true", help="print the line counts")
    parser.add_argument("-L", "--max-line-length", action="store_true", help="print the maximum line length")
    parser.add_argument("-t", "--tab-width", help="count tabs as N+ spaces instead of 8 for line length", metavar="N+",
                        nargs=1, type=int)
    parser.add_argument("-T", "--total", action="store_true", help="print a line with total counts")
    parser.add_argument("-w", "--words", action="store_true", help="print the word counts")
    parser.add_argument("--color", choices=("on", "off"), default="on", help="print the counts and file names in color")
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


def print_stats(stats: Stats | list[int], *, stat_origin: str) -> None:
    """
    Prints the stats.
    :param stats: The stats.
    :param stat_origin: Where the stats originated from.
    :return: None
    """
    stat_color = Colors.STAT_TOTAL if stat_origin == "total" else Colors.STAT
    stat_origin_color = Colors.STAT_TOTAL if stat_origin == "total" else Colors.STAT_ORIGIN

    for index, stat in enumerate(stats):
        if CountInfo.OPTIONS[index]:
            width = 12 if CountInfo.options_count > 1 or stat_origin else 0

            if Colors.on:
                print(f"{stat_color}{stat:>{width},}{Colors.RESET}", end="")
            else:
                print(f"{stat:>{width},}", end="")

    if stat_origin:
        if Colors.on:
            print(f"\t{stat_origin_color}{stat_origin}{Colors.RESET}")
        else:
            print(f"\t{stat_origin}")
    else:
        print()


def print_stats_from_files(files: TextIO | list[str]) -> None:
    """
    Prints stats from files.
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
                    stats = get_stats(text)

                    CountInfo.files_counted += 1
                    add_stats_to_totals(stats)
                    print_stats(stats, stat_origin=file)
        except FileNotFoundError:
            print_error_message(f"{file if file else "\"\""}: no such file or directory")
        except PermissionError:
            print_error_message(f"{file}: permission denied")
        except OSError:
            print_error_message(f"{file}: unable to read file")
        except UnicodeDecodeError:
            print_error_message(f"{file}: unable to decode file")


def print_stats_from_input() -> None:
    """
    Prints stats from standard input until EOF is entered.
    :return: None
    """
    eof = False
    lines = []

    while not eof:
        try:
            lines.append(f"{input()}\n")  # Add a newline to the input.
        except EOFError:
            eof = True

    print_stats(get_stats(lines), stat_origin="")


def set_count_info_values() -> None:
    """
    Sets the values to use for counting.
    :return: None
    """
    if Program.args.tab_width:  # --tab-width
        CountInfo.tab_width = Program.args.tab_width[0]

    if CountInfo.tab_width < 1:
        print_error_message(f"tab width ({CountInfo.tab_width}) cannot be less than 1", raise_system_exit=True)

    # -1 one for the actual tab character.
    CountInfo.tab_width -= 1

    # Check which stat options were provided: --lines, --words, --chars, or --max-line-length
    for index, option in enumerate(
            (Program.args.lines, Program.args.words, Program.args.chars, Program.args.max_line_length)):
        if option:
            CountInfo.OPTIONS[index] = True
            CountInfo.options_count += 1

    # If no stat options, default to lines, words and characters.
    if not CountInfo.options_count:
        CountInfo.OPTIONS[StatIndexes.LINES] = True
        CountInfo.OPTIONS[StatIndexes.WORDS] = True
        CountInfo.OPTIONS[StatIndexes.CHARACTERS] = True
        CountInfo.options_count = 3


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
