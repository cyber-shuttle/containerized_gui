#!/usr/bin/env python
from contextlib import redirect_stdout
import functools
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
from uuid import uuid4
import webbrowser

FILE_ARG = object()


class ContainerizedGUIThread(threading.Thread):
    def __init__(
        self,
        input_file,
        image_name,
        *args,
        vnc_url_handler=None,
        output_files_list=None,
        run_args=[FILE_ARG],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.input_file = input_file
        self.image_name = image_name
        self.vnc_url_handler = vnc_url_handler
        if output_files_list is not None:
            self.output_files = output_files_list
        else:
            self.output_files = []
        self.kill_event = threading.Event()
        self.run_args = run_args

    def run(self) -> None:
        print("inside run")

        with tempfile.TemporaryDirectory() as data_volume:
            filename = os.path.basename(self.input_file)
            shutil.copy(self.input_file, os.path.join(data_volume, filename))

            run_args = list(
                map(
                    lambda a: f"/data/{filename}" if a is FILE_ARG else a, self.run_args
                )
            )
            print(f"{run_args=}")

            docker_container_name = str(uuid4())
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
                    "--name",
                    docker_container_name,
                    self.image_name,
                    *run_args,
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
                    if self.vnc_url_handler is not None:
                        self.vnc_url_handler(novnc_url)
                    else:
                        print(f"opening browser tab for {novnc_url}")
                        webbrowser.open(novnc_url)
                    break
            # Wait for container to exit
            print("noVNC is running now")
            returncode = docker_proc.poll()
            while not self.kill_event.is_set() and returncode is None:
                try:
                    print(
                        f"waiting for docker container {docker_container_name=}, {returncode=}"
                    )
                    returncode = docker_proc.wait(1)
                except subprocess.TimeoutExpired:
                    pass
            else:
                # if container hasn't exited, then we're trying to kill it, so forceably stop it
                if returncode is None:
                    subprocess.run(
                        ["docker", "stop", "--time", "1", docker_container_name],
                        capture_output=True,
                    )
            novnc_proc.terminate()
            print("terminated noVNC")
            try:
                # Parse stdout and get output file paths
                container_output = docker_proc.stdout.read().decode()
                # print(f"{container_output=}")
                container_output_dict = json.loads(container_output)
                output_file_paths = container_output_dict["output-files"]
                docker_container_id = container_output_dict["container-id"]
                working_dir = container_output_dict["working-dir"]
                result = []
                for output_file_path in output_file_paths:
                    # Retrieve output file from container
                    output_filename = os.path.basename(output_file_path)
                    # Some paths are relative to the container working directory
                    full_output_file_path = (
                        output_file_path
                        if os.path.isabs(output_file_path)
                        else os.path.join(working_dir, output_file_path)
                    )
                    print(f"copying {output_filename} to ./output")
                    copy_result = subprocess.run(
                        [
                            "docker",
                            "cp",
                            f"{docker_container_id}:{full_output_file_path}",
                            "./output",
                        ]
                    )
                    # verify that copy succeeds
                    if copy_result.returncode == 0:
                        result.append(os.path.join(".", "output", output_filename))
                self.output_files = result
            except:
                pass
            finally:
                # Remove docker container
                print("removing docker container")
                subprocess.run(
                    ["docker", "rm", "-f", docker_container_name], capture_output=True
                )

    def kill(self):
        self.kill_event.set()


def run_gui(input_file, image_name, vnc_url_handler=None):
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
                if vnc_url_handler is not None:
                    vnc_url_handler(novnc_url)
                else:
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
        working_dir = container_output_dict["working-dir"]
        result = []
        for output_file_path in output_file_paths:
            # Retrieve output file from container
            output_filename = os.path.basename(output_file_path)
            # Some paths are relative to the container working directory
            full_output_file_path = (
                output_file_path
                if os.path.isabs(output_file_path)
                else os.path.join(working_dir, output_file_path)
            )
            print(f"copying {output_filename} to ./output")
            copy_result = subprocess.run(
                [
                    "docker",
                    "cp",
                    f"{docker_container_id}:{full_output_file_path}",
                    "./output",
                ]
            )
            # verify that copy succeeds
            if copy_result.returncode == 0:
                result.append(os.path.join(".", "output", output_filename))
        # Remove docker container
        subprocess.run(["docker", "rm", docker_container_id], capture_output=True)
        return result


def ui(name=None, width=1024, height=768, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(input_file, *args, **kwargs):

            # create output widget
            import ipywidgets as widgets
            from IPython.display import IFrame

            out = widgets.Output(layout={"border": "1px solid black"})

            # create vnc url handler, write iframe to output widget
            def vnc_url_handler(vnc_url):
                out.append_display_data(IFrame(vnc_url, width, height))

            def run_gui_thread(input_file):
                output_files = run_gui(
                    input_file, name, vnc_url_handler=vnc_url_handler
                )
                # Capture any output from wrapped function and write to output widget
                with redirect_stdout(io.StringIO()) as stdout:
                    func(output_files)
                # Clear output widget (closes VNC iframe)
                # (See https://github.com/jupyter-widgets/ipywidgets/issues/3260#issuecomment-907715980 for this workaround)
                out.outputs = ()
                out.append_stdout(stdout.getvalue())

            thread = threading.Thread(target=run_gui_thread, args=(input_file,))
            thread.start()
            return out

        return wrapper

    return decorator
