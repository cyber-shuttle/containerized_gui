#!/bin/bash

PID=$(cat /tmp/gui.pid)
strace -p $PID -Tf -e trace=openat -A -o /tmp/strace.log >& /tmp/strace_error.log
