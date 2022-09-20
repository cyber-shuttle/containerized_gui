#!/usr/bin/env python

import json
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

        # This doesn't work, probably executes too soon?
        # docker_container_id = (
        #     subprocess.check_output(["docker", "ps", "-l", "--quiet"]).decode().strip()
        # )
        # print(f"{docker_container_id=}")

        # Start a VNC viewer, pointed at container
        novnc_proc = subprocess.Popen(
            [
                "./novnc_proxy",
                "--vnc",
                "localhost:5900",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd="./noVNC-1.3.0/utils/",
        )
        for line in novnc_proc.stdout:
            line = line.decode()
            # print(line)
            if line.strip().startswith("http"):
                novnc_url = line.strip() + "&autoconnect=1&password=1234"
                print(f"opening browser tab for {novnc_url}")
                webbrowser.open(novnc_url)
                break
        # Wait for container to exit
        docker_proc.wait()
        novnc_proc.terminate()
        # Parse stdout and get output file paths
        container_output = docker_proc.stdout.read().decode()
        # print(f"{container_output=}")
        container_output_dict = json.loads(container_output)
        output_file_paths = container_output_dict["output-files"]
        docker_container_id = container_output_dict["container-id"]
        for output_file_path in output_file_paths:
            # Retrieve output file from container
            print(f"copying {os.path.basename(output_file_path)} to ./output")
            subprocess.check_call(
                [
                    "docker",
                    "cp",
                    f"{docker_container_id}:{output_file_path}",
                    "./output",
                ]
            )
        # TODO: Remove docker container
