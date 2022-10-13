#!/bin/bash

Xvfb "$DISPLAY" -screen 0 1024x768x24 &
openbox >& /tmp/openbox.log &
exec /startgui.sh "$@" >& /tmp/gui.log &
GUI_PID="$!"
/usr/bin/x11vnc -display "$DISPLAY" -usepw -forever -bg >& /tmp/x11vnc.log

# Run strace on the GUI process. This only works if Docker container started with --cap-add=SYS_PTRACE
strace -p $GUI_PID -Tf -e trace=openat -A -o /tmp/strace.log >& /tmp/strace_error.log

if [ $? != 0 ]; then
    echo "strace failed: make sure to start Docker container with --cap-add=SYS_PTRACE"
    cat /tmp/strace_error.log
    exit 1
fi

# If the GUI exited with errors, write out the GUI log file
GUI_EXIT_STATUS=$(/parse_strace.py -e /tmp/strace.log)
if [ $GUI_EXIT_STATUS != 0 ]; then
    echo "gui exited with errors: $GUI_EXIT_STATUS"
    cat /tmp/gui.log
else
    /parse_strace.py /tmp/strace.log
fi
