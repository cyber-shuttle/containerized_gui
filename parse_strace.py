#!/usr/bin/env python3

import fileinput
import json
import re
import socket
import tempfile
import shutil
import os
import requests

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
            if not file_exclusions.match(file_path):
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

    docker_host_ip =  os.getenv('DOCKER_HOST_IP')
    execution_id =  os.getenv('EXECUTION_ID')
    apiUrl = "http://" + docker_host_ip + ":8080/api/"

    with tempfile.TemporaryDirectory() as data_volume:
        out_dir = os.path.join(data_volume, 'outputs')
        os.mkdir(out_dir)
        for output_file in output_file_paths:
            filename = os.path.basename(output_file)
            shutil.copy(output_file, os.path.join(out_dir, filename))
        
        shutil.make_archive(os.path.join(data_volume, "ARCHIVE"), 'zip', out_dir)
        

        headers={'Accept': 'application/json, text/plain, */*',
                 'Accept-Encoding': 'gzip, deflate, br',
                 'Accept-Language': 'en-US,en;q=0.9',
                 'Connection': 'keep-alive'}

        files = {'file': open(os.path.join(data_volume,'ARCHIVE.zip'), 'rb')}
        archive_upload_response = requests.post(apiUrl + "archive/upload", data={}, headers=headers, files=files)

        archive_id = ""
        if archive_upload_response.status_code == 200:
            
            response_json = archive_upload_response.json()
            archive_json = {"path": response_json["path"],"description": "Archive for UI Container Output"}
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            response = requests.post(apiUrl + 'archive/', data=json.dumps(archive_json), headers=headers)
            if response.status_code == 200:
                print("Archive with name : " + archive_json["description"] + " was uploaded")
                archive_id = response.json()["id"]

                execution_result_json = {"executionId": execution_id, "archiveId": archive_id}
                execution_result_response = requests.post(apiUrl + 'ui/result/', data=json.dumps(execution_result_json), headers=headers)
                if execution_result_response.status_code == 200:
                    print("Submitted execution result")
                    print(execution_result_response.json())
                else:
                    print("Failed to submit execution result for execution id " + execution_id + ". Err : " + str(execution_result_response.status_code))

            else:
                print("Failed to create archive metadata in server with status code " + str(response.status_code))
