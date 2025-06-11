#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: pytail.py
Author: Roth Earl
Version: 1.0.2
Description: A program to print the last part of files.
License: GNU GPLv3
"""

import argparse
import os
import sys
import time
from threading import Thread
from typing import Final, TextIO, final


@final
class Colors:
    """
    Class for managing color constants.
    """
    COLON: Final[str] = "\x1b[96m"  # Bright cyan
    FILE_NAME: Final[str] = "\x1b[95m"  # Bright magenta
    FOLLOWING: Final[str] = "\x1b[2;37m"  # Dim white
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
class Program:
    """
    Class for managing program constants.
    """
    NAME: Final[str] = "pytail"
    VERSION: Final[str] = "1.0.2"
    args: argparse.Namespace = None
    has_errors: bool = False


def follow_file(file_name: str, print_file_name: bool, polling_interval: float = .5) -> None:
    """
    Follows a file for new lines.
    :param file_name: The file name.
    :param print_file_name: Whether to print the file name with each update.
    :param polling_interval: The duration between each check.
    :return: None
    """
    try:
        encoding = "iso-8859-1" if Program.args.iso else "utf-8"  # --iso

        # Get the initial file content.
        with open(file_name, "r", encoding=encoding) as file:
            previous_content = file.read()

        # Follow file until Ctrl-C.
        while True:
            # Re-open the file with each iteration.
            with open(file_name, "r", encoding=encoding) as file:
                next_content = file.read()

                # Check for changes.
                if previous_content != next_content:
                    print_index = 0

                    if next_content.startswith(previous_content):
                        print_index = len(previous_content)
                    elif len(next_content) < len(previous_content):
                        print_error_message(f"data deleted in: {file_name}")
                    else:
                        print_error_message(f"data modified in: {file_name}")

                    if print_file_name:
                        print_file_header(file_name)

                    print(next_content[print_index:], end="")
                    previous_content = next_content

            time.sleep(polling_interval)
    except FileNotFoundError:
        print_error_message(f"{file_name} has been deleted")
    except (OSError, UnicodeDecodeError):
        print_error_message(f"{file_name} is no longer accessible")


def follow_files(files: list[str]) -> list[Thread]:
    """
    Follows the files for new lines.
    :param files: The files.
    :return: A list of threads that are following files.
    """
    print_file_name = len(files) > 1
    threads = []

    for file in files:
        thread = Thread(target=follow_file, args=(file, print_file_name))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    return threads


def main() -> None:
    """
    A program to print the last part of files.
    :return: None
    """
    files_printed = []

    parse_arguments()

    # Ensure Colors.on is only True if --color=on and the output is to the terminal.
    Colors.on = Program.args.color == "on" and sys.stdout.isatty()

    # Ensure --line-number is only True if --follow=False.
    Program.args.line_number = Program.args.line_number and not Program.args.follow

    # Set --no-file-header to True if there are no files and --xargs=False.
    if not Program.args.files and not Program.args.xargs:
        Program.args.no_file_header = True

    # Check if the input is being redirected.
    if not sys.stdin.isatty():
        if Program.args.xargs:  # --xargs
            files_printed.extend(print_lines_from_files(sys.stdin))
        else:
            if standard_input := sys.stdin.readlines():
                print_file_header(file="")
                print_lines(standard_input, has_newlines=True)

        if Program.args.files:  # Process any additional files.
            files_printed.extend(print_lines_from_files(Program.args.files))
    elif Program.args.files:
        files_printed.extend(print_lines_from_files(Program.args.files))
    else:
        print_lines_from_input()

    if Program.args.follow and files_printed:  # --follow
        for thread in follow_files(files_printed):
            thread.join()


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description="print the last 10 lines from FILES",
                                     epilog="with no FILES, read standard input")

    parser.add_argument("files", help="files to print", metavar="FILES", nargs="*")
    parser.add_argument("-f", "--follow", action="store_true", help="output appended data as the file grows")
    parser.add_argument("-H", "--no-file-header", action="store_true", help="suppress the file name header on output")
    parser.add_argument("-n", "--lines", help="print the last or all but the first n lines", metavar="±n", nargs=1,
                        type=int)
    parser.add_argument("-N", "--line-number", action="store_true", help="print line number with output lines")
    parser.add_argument("--color", choices=("on", "off"), default="on", help="print the file headers in color")
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
        following = f" (following)" if Program.args.follow and file else ""

        if Colors.on:
            file_name = f"{Colors.FILE_NAME}{file_name}{Colors.COLON}:{Colors.FOLLOWING}{following}{Colors.RESET}"
        else:
            file_name = f"{file_name}:{following}"

        print(file_name)


def print_lines(lines: list[str], *, has_newlines: bool) -> None:
    """
    Prints the lines.
    :param lines: The lines.
    :param has_newlines: Whether the lines end with a newline character.
    :return: None
    """
    line_number = 0
    lines_to_print = 10 if not Program.args.lines else Program.args.lines[0]  # --lines
    print_end = "" if has_newlines else "\n"
    skip_to_line = len(lines) - lines_to_print

    # Print all but the first 'n' lines.
    if lines_to_print < 0:
        skip_to_line = abs(lines_to_print)

    for line in lines:
        line_number += 1

        if line_number > skip_to_line:
            if Program.args.line_number:  # --line-number
                width = 7

                if Colors.on:
                    line = f"{Colors.LINE_NUMBER}{line_number:>{width}}{Colors.COLON}:{Colors.RESET}{line}"
                else:
                    line = f"{line_number:>{width}}:{line}"

            print(line, end=print_end)


def print_lines_from_files(files: TextIO | list[str]) -> list[str]:
    """
    Prints lines from files.
    :param files: The files.
    :return: A list of the files printed.
    """
    encoding = "iso-8859-1" if Program.args.iso else "utf-8"  # --iso
    files_printed = []

    for file in files:
        file = file.rstrip("\n")

        try:
            if os.path.isdir(file):
                print_error_message(f"{file}: is a directory")
            else:
                with open(file, "r", encoding=encoding) as text:
                    print_file_header(file=file)
                    print_lines(text.readlines(), has_newlines=True)
                    files_printed.append(file)
        except FileNotFoundError:
            print_error_message(f"{file if file else "\"\""}: no such file or directory")
        except PermissionError:
            print_error_message(f"{file}: permission denied")
        except OSError:
            print_error_message(f"{file}: unable to read file")
        except UnicodeDecodeError:
            print_error_message(f"{file}: unable to decode file")

    return files_printed


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
            print_lines(lines, has_newlines=False)
            lines.clear()

            # --follow on standard input is an infinite loop until Ctrl-C.
            if not Program.args.follow:
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
