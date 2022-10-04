FROM ubuntu:20.04
RUN apt-get update && apt-get install -y --no-install-recommends strace x11vnc xvfb python3
RUN	mkdir ~/.vnc
RUN	x11vnc -storepasswd 1234 ~/.vnc/passwd
ENV DISPLAY=:0
COPY init.sh /init.sh
COPY start_strace.sh /start_strace.sh
COPY parse_strace.py /parse_strace.py
EXPOSE 5900
ENTRYPOINT ["/init.sh"]
