#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pyline.py
Author: Roth Earl
Version: 1.0.0
Description: A program to find lines that match patterns.
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
    LINE_NUMBER: Final[str] = "\x1b[92m"  # Bright green
    MATCH: Final[str] = "\x1b[91m"  # Bright red
    RESET: Final[str] = "\x1b[0m"
    on: bool = False


@final
class ExitCodes:
    """
    Class for managing exit code constants.
    """
    NO_MATCHES: Final[int] = 1
    ERROR: Final[int] = 2
    KEYBOARD_INTERRUPT: Final[int] = 130


@final
class MatchInfo:
    """
    Class for managing match constants.
    """
    at_least_one_match: bool = False


@final
class Program:
    """
    Class for managing program constants.
    """
    NAME: Final[str] = "pyline"
    VERSION: Final[str] = "1.0.0"
    args: argparse.Namespace
    has_errors: bool = False


def highlight_patterns(patterns: list[str], line: str) -> str:
    """
    Highlights all patterns in the line.
    :param patterns: The patterns.
    :param line: The line.
    :return: The line with patterns highlighted.
    """
    flags = re.IGNORECASE if Program.args.ignore_case else 0

    for pattern in patterns:
        for split_pattern in split_pattern_on_pipe(pattern):
            if match := re.search(split_pattern, line, flags=flags):
                replace = line[match.start():match.end()]
                line = re.sub(split_pattern, f"{Colors.MATCH}{replace}{Colors.RESET}", line)

    return line


def line_matches_patterns(line: str) -> bool:
    """
    Returns whether the line matches any of the find patterns.
    :param line: The line.
    :return: True or False.
    """
    matches_patterns = True

    if Program.args.find:  # --find
        matches_patterns = text_has_patterns(line, Program.args.find)

        if Program.args.invert_find:  # --invert-find
            matches_patterns = not matches_patterns

    return matches_patterns


def main() -> None:
    """
    A program to find lines that match patterns.
    :return: None
    """
    parse_arguments()

    # Ensure color is only True if --color=on and the output is to the terminal.
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Set --no-file-header to True if there are no files.
    if not Program.args.files:
        Program.args.no_file_header = True

    # Check if the input is being redirected.
    if not sys.stdin.isatty():
        if Program.args.xargs:  # --xargs
            print_matches_in_files(sys.stdin)
        else:
            if standard_input := sys.stdin.readlines():
                print_matches_in_lines(standard_input, has_newlines=True, origin_file="")

        if Program.args.files:  # Process any additional files.
            print_matches_in_files(Program.args.files)
    elif Program.args.files:
        print_matches_in_files(Program.args.files)
    else:
        print_matches_in_input()


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description="find lines that match patterns in FILES",
                                     epilog="with no FILES, read standard input")

    parser.add_argument("files", help="files to find lines in", metavar="FILES", nargs="*")
    parser.add_argument("-c", "--count", action="store_true",
                        help="print only a count of matching lines per input file")
    parser.add_argument("-f", "--find", action="extend", help="find lines that match PATTERN", metavar="PATTERN",
                        nargs=1)
    parser.add_argument("-H", "--no-file-header", action="store_true", help="suppress the file name header on output")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore case in patterns and input data")
    parser.add_argument("-I", "--invert-find", action="store_true", help="find non-matching lines")
    parser.add_argument("-n", "--line-number", action="store_true", help="print line number with output lines")
    parser.add_argument("-q", "--quiet", "--silent", action="store_true", help="suppress all normal output")
    parser.add_argument("--color", choices=("on", "off"), default="on",
                        help="print the matched strings, file names, and line numbers in color")
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


def print_matches_in_files(files: TextIO | list[str]) -> None:
    """
    Prints matches found in files.
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
                    print_matches_in_lines(text, has_newlines=True, origin_file=file)
        except FileNotFoundError:
            print_error_message(f"{file if file else "\"\""}: no such file or directory")
        except PermissionError:
            print_error_message(f"{file}: permission denied")
        except OSError:
            print_error_message(f"{file}: unable to read file")
        except UnicodeDecodeError:
            print_error_message(f"{file}: unable to decode file")


def print_matches_in_input() -> None:
    """
    Prints matches found in standard input until EOF is entered.
    :return: None
    """
    eof = False
    lines = []

    while not eof:
        try:
            line = input()

            # If --count, wait until EOF before finding matches.
            if Program.args.count:
                lines.append(line)
            else:
                print_matches_in_lines([line], has_newlines=False, origin_file="")
        except EOFError:
            eof = True

    if Program.args.count:  # --count
        print_matches_in_lines(lines, has_newlines=False, origin_file="")


def print_matches_in_lines(lines: TextIO | list[str], *, has_newlines: bool, origin_file: str) -> None:
    """
    Prints matches found in lines.
    :param lines: The lines.
    :param origin_file: The file where the lines originated from.
    :param has_newlines: Whether the lines end with a newline character.
    :return: None
    """
    line_number = 0
    matches = []
    print_end = "" if has_newlines else "\n"

    # Find matches.
    for line in lines:
        line_number += 1

        if line_matches_patterns(line):
            MatchInfo.at_least_one_match = True

            if Colors.on:
                if Program.args.find and not Program.args.invert_find:  # --find and not --invert-find
                    line = highlight_patterns(Program.args.find, line)

            if Program.args.line_number:  # --line-number
                width = 7

                if Colors.on:
                    line = f"{Colors.LINE_NUMBER}{line_number:>{width}}{Colors.COLON}:{Colors.RESET}{line}"
                else:
                    line = f"{line_number:>{width}}:{line}"

            matches.append(line)

    # Print matches.
    if not Program.args.quiet:  # --quiet
        file_name = ""

        if not Program.args.no_file_header:  # --no-file-header
            file_name = os.path.relpath(origin_file) if origin_file else "(standard input)"

            if Colors.on:
                file_name = f"{Colors.FILE_NAME}{file_name}{Colors.COLON}:{Colors.RESET}"
            else:
                file_name = f"{file_name}:"

        if Program.args.count:  # --count
            print(f"{file_name}{len(matches)}")
        elif matches:
            if file_name:
                print(file_name)

            for _ in matches:
                print(_, end=print_end)


def split_pattern_on_pipe(pattern: str) -> list[str]:
    """
    Splits the pattern on the pipe character if it is not preceded by a backslash character.
    :param pattern: The pattern.
    :return: A list of patterns.
    """
    patterns = []
    pipe_index = 0

    for index, ch in enumerate(pattern):
        if index and ch == "|" and pattern[index - 1] != "\\":
            patterns.append(pattern[pipe_index:index])
            index += 1
            pipe_index = index

    patterns.append(pattern[pipe_index:])

    return patterns


def text_has_patterns(text: str, patterns: list[str]) -> bool:
    """
    Returns whether the text has all the patterns.
    :param text: The text.
    :param patterns: The patterns.
    :return: True or False.
    """
    flags = re.IGNORECASE if Program.args.ignore_case else 0
    has_patterns = True
    pattern = None

    try:
        for pattern in patterns:
            if not re.search(pattern, text, flags=flags):
                has_patterns = False
                break
    except re.error:
        print_error_message(f"invalid regex pattern: {pattern}", raise_system_exit=True)

    return has_patterns


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

        if not MatchInfo.at_least_one_match:
            raise SystemExit(ExitCodes.NO_MATCHES)
    except KeyboardInterrupt:
        print()  # Add a newline after Ctrl-C.
        raise SystemExit(ExitCodes.ERROR if windows else ExitCodes.KEYBOARD_INTERRUPT)
    except OSError:
        raise SystemExit(ExitCodes.ERROR)
