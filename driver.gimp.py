#!/usr/bin/env python

import os
import shutil
import subprocess
import sys
from tempfile import tempdir
import tempfile
import webbrowser


if __name__ == "__main__":

    # command line arguments
    # - positional: input-file
    if len(sys.argv) < 2:
        print("Missing filename of input file")
        sys.exit(1)
    input_file = sys.argv[1]
    print(input_file)

    # Create a data directory and copy input file into it
    with tempfile.TemporaryDirectory() as data_volume:
        filename = os.path.basename(input_file)
        shutil.copy(input_file, os.path.join(data_volume, filename))

        docker_proc = subprocess.Popen(
            [
                "docker",
                "run",
                "-p",
                # TODO: Can this be dynamic?
                "5900:5900",
                "-v",
                f"{data_volume}:/data",
                "--cap-add=SYS_PTRACE",
                "gimp",
                f"/data/{filename}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        # Start a VNC viewer, pointed at container
        novnc_proc = subprocess.Popen(
            [
                "./novnc_proxy",
                "--vnc",
                "localhost:5900",
            ],
            stdout=subprocess.PIPE,
            cwd="./noVNC-1.3.0/utils/",
        )
        for line in novnc_proc.stdout:
            line = line.decode()
            if line.strip().startswith("http"):
                webbrowser.open(line.strip())
                break
            print(line)
        # Wait for container to exit
        docker_proc.wait()
        novnc_proc.terminate()
        # TODO: Retrieve output file from container
        # TODO: Remove docker container
