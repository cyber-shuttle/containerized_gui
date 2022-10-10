#!/bin/bash

Xvfb "$DISPLAY" -screen 0 1024x768x24 &
openbox >& /tmp/openbox.log &
exec /startgui.sh "$@" >& /tmp/gui.log &
echo $! > /tmp/gui.pid
/usr/bin/x11vnc -display "$DISPLAY" -usepw -forever -bg >& /tmp/x11vnc.log
exec /start_strace.sh
