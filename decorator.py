#!/usr/bin/env python
import functools
import json
import os
import shutil
import subprocess
import tempfile
import webbrowser


def run_gui(input_file, image_name):
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
                image_name,
                f"/data/{filename}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # TODO: wait for docker VNC server to be ready

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
        result = []
        for output_file_path in output_file_paths:
            # Retrieve output file from container
            output_filename = os.path.basename(output_file_path)
            print(f"copying {output_filename} to ./output")
            subprocess.run(
                [
                    "docker",
                    "cp",
                    f"{docker_container_id}:{output_file_path}",
                    "./output",
                ]
            )
            result.append(os.path.join(".", "output", output_filename))
        # Remove docker container
        subprocess.run(["docker", "rm", docker_container_id], capture_output=True)
        return result


def ui(name=None, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(input_file, *args, **kwargs):
            output_files = run_gui(input_file, name)
            func(output_files)

        return wrapper

    return decorator


if __name__ == "__main__":

    @ui(name="gimp")
    def svg2png(output_files):
        print(f"{output_files=}")
        # TODO: do something with the output_files?
        return output_files

    output_files = svg2png("./data/space-shuttle.svg")
