#!/bin/bash

export DISPLAY=:0
Xvfb "$DISPLAY" -screen 0 1024x768x24 &
gimp "$@" &
echo $! > /tmp/gui.pid
/start_strace.sh &
echo $! > /tmp/strace.pid
exec /usr/bin/x11vnc -display "$DISPLAY" -usepw -forever
