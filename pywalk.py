#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pywalk.py
Author: Roth Earl
Version: 1.0.3
Description: A program to find files in a directory hierarchy.
License: GNU GPLv3
"""

import argparse
import os
import pathlib
import re
import sys
import time
from typing import Final, final


@final
class Colors:
    """
    Class for managing color constants.
    """
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
    NAME: Final[str] = "pywalk"
    VERSION: Final[str] = "1.0.3"
    args: argparse.Namespace = None
    has_errors: bool = False


def file_matches_filters(file: pathlib.Path) -> bool:
    """
    Returns whether the file matches any of the filters.
    :param file: The file.
    :return: True or False.
    """
    matches_filters = True

    try:
        if Program.args.type:  # --type
            is_dir = file.is_dir()

            if Program.args.type == "d":
                matches_filters = is_dir
            else:
                matches_filters = not is_dir

        if matches_filters and Program.args.empty:  # --empty
            if file.is_dir():
                matches_filters = not os.listdir(file)
            else:
                matches_filters = not file.lstat().st_size

            if Program.args.empty == "n":
                matches_filters = not matches_filters

        # --m-days, --m-hours, or --m-mins
        if matches_filters and any((Program.args.m_days, Program.args.m_hours, Program.args.m_mins)):
            if Program.args.m_days:
                last_modified = Program.args.m_days[0] * 86400  # Convert seconds to days.
            elif Program.args.m_hours:
                last_modified = Program.args.m_hours[0] * 3600  # Convert seconds to hours.
            else:
                last_modified = Program.args.m_mins[0] * 60  # Convert seconds to minutes.

            difference = time.time() - file.lstat().st_mtime

            if last_modified < 0:
                matches_filters = difference < (last_modified * -1)
            else:
                matches_filters = difference > last_modified
    except PermissionError:
        print_error_message(f"{file}: permission denied")

    return matches_filters


def file_name_matches_patterns(file_name: str) -> bool:
    """
    Returns whether the file name matches any of the find patterns.
    :param file_name: The file name.
    :return: True or False.
    """
    matches_patterns = True

    if Program.args.find:  # --find
        matches_patterns = text_has_patterns(file_name, Program.args.find)

        if Program.args.invert_find:  # --invert-find
            matches_patterns = not matches_patterns

    return matches_patterns


def highlight_patterns(patterns: list[str], file_name: str) -> str:
    """
    Highlights all patterns in the file name.
    :param patterns: The patterns.
    :param file_name: The file name.
    :return: The file name with patterns highlighted.
    """
    flags = re.IGNORECASE if Program.args.ignore_case else 0

    for pattern in patterns:
        for sub_pattern in split_pattern_on_pipe(pattern):
            if match := re.search(sub_pattern, file_name, flags=flags):
                replace = f"{Colors.MATCH}{file_name[match.start():match.end()]}{Colors.RESET}"

                file_name = re.sub(sub_pattern, repl=replace, string=file_name, flags=flags)

    return file_name


def main() -> None:
    """
    A program to find files in a directory hierarchy.
    :return: None
    """
    parse_arguments()

    # Ensure Colors.on is only True if --color=on and the output is to the terminal
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Check if the input is being redirected.
    if not sys.stdin.isatty():
        for directory in sys.stdin:
            print_files(directory.rstrip("\n"))

        if Program.args.dirs:  # Process any additional directories.
            for directory in Program.args.dirs:
                print_files(directory)
    else:
        dirs = os.curdir if not Program.args.dirs else Program.args.dirs

        for directory in dirs:
            print_files(directory)


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description="find files in a directory hierarchy",
                                     epilog="default directory is the current directory")
    modified_group = parser.add_mutually_exclusive_group()

    parser.add_argument("dirs", help="the directory starting-points", metavar="DIRECTORIES", nargs="*")
    parser.add_argument("-e", "--escape-spaces", action="store_true", help="print paths with spaces escaped")
    parser.add_argument("-f", "--find", action="extend", help="find files that match PATTERN", metavar="PATTERN",
                        nargs=1)
    parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore case in patterns and input data")
    parser.add_argument("-I", "--invert-find", action="store_true", help="find non-matching files")
    parser.add_argument("-q", "--quiet", "--silent", action="store_true", help="suppress all normal output")
    parser.add_argument("--abs", action="store_true", help="print absolute file paths")
    parser.add_argument("--color", choices=("on", "off"), default="on", help="print the matched strings in color")
    parser.add_argument("--empty", choices=("y", "n"), help="find files that are empty")
    parser.add_argument("--type", choices=("d", "f"), help="find files by type")
    modified_group.add_argument("--m-days", help="find files modified < than or > than n days", metavar="±n", nargs=1,
                                type=int)
    modified_group.add_argument("--m-hours", help="find files modified < than or > than n hours", metavar="±n", nargs=1,
                                type=int)
    modified_group.add_argument("--m-mins", help="find files modified < than or > than n minutes", metavar="±n",
                                nargs=1, type=int)
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


def print_file(file: pathlib.Path) -> None:
    """
    Prints the file.
    :param file: The file.
    :return: None
    """
    if file_matches_filters(file):
        file_name = file.name

        # The dot file does not have a file name.
        if not file_name:
            file_name = os.path.curdir

        if file_name_matches_patterns(file_name):
            MatchInfo.at_least_one_match = True

            if not Program.args.quiet:  # --quiet
                path = str(file.absolute() if Program.args.abs else file)  # --abs

                if Program.args.escape_spaces:  # --escape-spaces
                    path = path.replace(" ", "\\ ")

                if Colors.on:  # --color
                    if Program.args.find and not Program.args.invert_find:  # --find and not --invert-find
                        highlight = highlight_patterns(Program.args.find, file_name)

                        # Ensure only the file name gets highlighted and nothing else in the path.
                        path = highlight.join(path.rsplit(file_name, maxsplit=1))

                print(path)


def print_files(directory: str) -> None:
    """
    Prints all the files in the directory hierarchy.
    :param directory: The directory to walk.
    :return: None
    """
    if os.path.exists(directory):
        directory_hierarchy = pathlib.Path(directory)

        print_file(directory_hierarchy)

        try:
            for file in directory_hierarchy.rglob("*"):
                print_file(file)
        except PermissionError as error:
            print_error_message(f"{error.filename}: permission denied")
    else:
        print_error_message(f"{directory if directory else "\"\""}: no such file or directory")


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
