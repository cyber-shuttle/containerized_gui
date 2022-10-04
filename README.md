# Containerized GUI Experiments

## Getting Started

First, clone the repository. Then perform the following steps inside the repo.

### Build 'base' image

```
docker build -t gui-base dockerfiles/base/
```

### Build 'gimp' image

```
docker build -t gimp dockerfiles/gimp/
```

### noVNC install

```
curl -OL https://github.com/novnc/noVNC/archive/refs/tags/v1.3.0.tar.gz
tar zxf v1.3.0.tar.gz
```

### Python virtual environment

```
python3 -m venv venv
source ./venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt
```

### Start JupyterLab

```
jupyter-lab svg2png.ipynb
```

## Containerized GUIs

https://github.com/jlesage/docker-firefox

    docker run -d --name=firefox -p 5800:5800 -p 5900:5900 -e VNC_PASSWORD=1234 --shm-size 2g jlesage/firefox

also https://github.com/jlesage/docker-baseimage-gui and
https://jlesage.github.io/docker-apps/

## Other containerized GUI repos

- https://github.com/kasmtech/workspaces-images
- https://github.com/linuxserver
  - Guacamole
  - https://github.com/linuxserver/docker-baseimage-rdesktop-web
- https://stackoverflow.com/questions/16296753/can-you-run-gui-applications-in-a-linux-docker-container/16311264
- https://github.com/tkreind/docker-gui-novnc

## Difference between Guacamole and NoVNC

https://sourceforge.net/p/guacamole/discussion/1110834/thread/00b95bb2/#9355

## Strace

```
strace -p PID -Tf -e trace=openat -A -o /tmp/strace.log
```

## noVNC

```
cd noVNC-1.3.0/utils
./novnc_proxy --vnc localhost:5900
```

## JupyterLab and VNC integration

- https://discourse.jupyter.org/t/jupyterhub-gui-applications/6714/3
- https://pypi.org/project/jupyterlab-novnc/
- https://github.com/SwissDataScienceCenter/renku-vnc
- https://github.com/jupyterhub/jupyter-remote-desktop-proxy
