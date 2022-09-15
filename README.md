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
