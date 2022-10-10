#!/usr/bin/env python3

import fileinput
import json
import os
import re
import socket

# Only consider files that are written
syscall_line = re.compile(r"\d+\s+open\w*\(\w+, \"([^\"]+)\".*(O_WRONLY|O_RDWR)")
file_exclusions = re.compile(r"/root/.config|/root/.cache|/root/.local|/dev")


def get_output_files(log_file):
    output_file_paths = set()
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
    return output_file_paths


if __name__ == "__main__":
    output_file_paths = get_output_files(fileinput.input())

    print(
        json.dumps(
            {
                "output-files": list(output_file_paths),
                # Get docker container id (https://stackoverflow.com/a/577710160)
                "container-id": socket.gethostname(),
            }
        )
    )
