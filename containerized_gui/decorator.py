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
import time
import requests
import re

apiUrl = "http://localhost:8080/api/"

def run_gui(input_file, image_name, appName,  vnc_url_handler=None):
    # Create a data directory and copy input file into it
    with tempfile.TemporaryDirectory() as data_volume:
        filename = os.path.basename(input_file)
        input_dir = os.path.join(data_volume, 'inputs')
        os.mkdir(input_dir)
        shutil.copy(input_file, os.path.join(input_dir, filename))
        shutil.make_archive(os.path.join(data_volume, "ARCHIVE"), 'zip', input_dir)


        headers={'Accept': 'application/json, text/plain, */*',
                 'Accept-Encoding': 'gzip, deflate, br',
                 'Accept-Language': 'en-US,en;q=0.9',
                 'Connection': 'keep-alive'}

        files = {'file': open(os.path.join(data_volume,'ARCHIVE.zip'), 'rb')}
        archive_upload_response = requests.post(apiUrl + "archive/upload", data={}, headers=headers, files=files)

        archive_id = ""
        if archive_upload_response.status_code == 200:
            
            response_json = archive_upload_response.json()
            archive_json = {"path": response_json["path"],"description": "Archive for UI Container"}
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            response = requests.post(apiUrl + 'archive/', data=json.dumps(archive_json), headers=headers)
            if response.status_code == 200:
                # print("Archive with name : " + archive_json["description"] + " was uploaded")
                archive_id = response.json()["id"]
            else:
                print("Failed to create archive metadata in server with status code " + str(response.status_code))

        url = apiUrl + "ui/launch"
        req_json = {'appName': appName, 'archiveId': archive_id}

        resp = requests.post(url, json = req_json)
        resp_json = resp.json()
        novnc_url = resp_json['vncUrl']
        container_id = resp_json['containerId']
        execution_id = resp_json['executionId']
        
        status_url = apiUrl + 'ui/container/status/' + container_id
        resp = requests.post(status_url, json = req_json)
        status_resp_json = resp.json()
        container_status = status_resp_json['status']

        while(not container_status == 'PORT_OPEN'):
            time.sleep(1)
            resp = requests.get(status_url, json = req_json)
            status_resp_json = resp.json()
            container_status = status_resp_json['status']
        
        if vnc_url_handler is not None:
            # print(f"Running vnc handler for url {novnc_url}" )
            vnc_url_handler(novnc_url)
        else:
            print(f"opening browser tab for {novnc_url}")
            webbrowser.open(novnc_url)
    
        while(not container_status == 'STOPPED'):
            time.sleep(1)
            resp = requests.get(status_url, json = req_json)
            status_resp_json = resp.json()
            container_status = status_resp_json['status']

        result_url = apiUrl + 'ui/result/execution/' + execution_id
        resp = requests.get(result_url, json = req_json)
        
        if (resp.status_code == 200):
            result_resp_json = resp.json()
            # print(result_resp_json)
            archive_id = result_resp_json['archiveId']
            ouput_dir = os.path.join("output", appName, execution_id)
            os.makedirs(ouput_dir)
            download_file = download_file_from_url(apiUrl + 'archive/download_archive/' + archive_id, ouput_dir)
            shutil.unpack_archive(download_file, ouput_dir, "zip")
            os.remove(download_file)
            output_files = os.listdir(ouput_dir)
            # print("Files available in " + ouput_dir + " are " + str(output_files))
            for i in range(len(output_files)):
                output_files[i] = os.path.join(ouput_dir, output_files[i])

            return output_files
        else:
            print("Failed to fetch execution result. Err code " + str(resp.status_code))


        return []

def download_file_from_url(download_url, download_dir):
    resp = requests.get(download_url, allow_redirects=True)
    disp_header = resp.headers.get('content-disposition')
    if disp_header:
        file_name = re.findall('filename=(.+)', disp_header)
        if len(file_name) == 0:
            return None

        open(os.path.join(download_dir, file_name[0]), 'wb').write(resp.content)
        # print("File " + file_name[0] + " was downloaded")
        return os.path.join(download_dir, file_name[0])
    else:
        print("Could not find the file name in download response")
        

def ui(name=None, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(input_file, *args, **kwargs):

            # create output widget
            import ipywidgets as widgets
            from IPython.display import IFrame

            out = widgets.Output(layout={"border": "1px solid black"})

            # create vnc url handler, write iframe to output widget
            def vnc_url_handler(vnc_url):
                # TODO: make VNC iframe height/width configurable, here and in GUI container
                out.append_display_data(IFrame(vnc_url, 1024, 768))

            def run_gui_thread(input_file):
                output_files = run_gui(
                    input_file, name, "gimp", vnc_url_handler=vnc_url_handler
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
