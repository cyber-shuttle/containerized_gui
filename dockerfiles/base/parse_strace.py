#!/usr/bin/env python3

import argparse
import json
import os
import re
import socket

# Only consider files that are written
syscall_line = re.compile(r"\d+\s+open\w*\(\w+, \"([^\"]+)\".*(O_WRONLY|O_RDWR)")
file_exclusions = re.compile(r"/root/.config|/root/.cache|/root/.local|/dev")
exit_code_line = re.compile(r"(\d+)\s+\+\+\+ exited with (-?\d+) \+\+\+")


def process_strace_log(log_file):
    output_file_paths = set()
    exit_code = None
    for line in log_file:
        line = line.strip()

        m = syscall_line.match(line)
        if m:
            file_path = m.group(1)
            if file_exclusions.match(file_path):
                continue
            if not os.path.exists(file_path):
                continue
            output_file_paths.add(file_path)
        m = exit_code_line.match(line)
        if m:
            pid, exit_code = m.groups()
            # assuming that the last reported exit code is the exit code of the main process
            exit_code = int(exit_code)
    return output_file_paths, exit_code


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--exit-code",
        help="only print exit code of traced process",
        action="store_true",
    )
    parser.add_argument("log_file", type=open)
    args = parser.parse_args()

    output_file_paths, exit_code = process_strace_log(args.log_file)
    if args.exit_code:
        print(f"{exit_code}")
    else:
        print(
            json.dumps(
                {
                    "output-files": list(output_file_paths),
                    # Get docker container id (https://stackoverflow.com/a/577710160)
                    "container-id": socket.gethostname(),
                    "exit-code": exit_code,
                }
            )
        )
