# https://www.howtogeek.com/devops/how-to-run-gui-applications-in-a-docker-container/
# https://github.com/creack/docker-firefox/blob/master/Dockerfile
# Need 20.04 because 22.04 only installs a Firefox Snap and getting the snap to install Firefox is painful
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y firefox x11vnc xvfb
RUN	mkdir ~/.vnc
RUN	x11vnc -storepasswd 1234 ~/.vnc/passwd
# RUN echo "exec firefox" > ~/.xinitrc && chmod +x ~/.xinitrc
ENV DISPLAY=:0
COPY startx11vnc.sh /startx11vnc.sh
EXPOSE 5900
CMD ["/startx11vnc.sh"]
