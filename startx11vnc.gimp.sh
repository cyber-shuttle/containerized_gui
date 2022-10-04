#!/bin/bash

unzip /opt/ARCHIVE.zip -d /inputs
FILES=`ls /inputs`
export DISPLAY=:0
Xvfb "$DISPLAY" -screen 0 1024x768x24 &
gimp /inputs/$FILES >& /dev/null &
echo $! > /tmp/gui.pid
/usr/bin/x11vnc -display "$DISPLAY" -usepw -forever -bg >& /dev/null
exec /start_strace.sh
