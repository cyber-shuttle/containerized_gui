FROM ubuntu:20.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    openbox \
    python3 \
    strace \
    x11vnc \
    xvfb
RUN	mkdir ~/.vnc
RUN	x11vnc -storepasswd 1234 ~/.vnc/passwd
ENV DISPLAY=:0
ENV DISPLAY_WIDTH=1024
ENV DISPLAY_HEIGHT=768
COPY init.sh /init.sh
COPY parse_strace.py /parse_strace.py
EXPOSE 5900
ENTRYPOINT ["/init.sh"]
