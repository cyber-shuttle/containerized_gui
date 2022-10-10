FROM gui-base

RUN apt-get install -y \
    curl \
    python3 \
    python3-matplotlib \
    python3-pandas \
    python3-pyqt5 \
    python3-pyqt5.qtsvg \
    python3-scipy

RUN mkdir /app
WORKDIR /app

RUN curl -OL https://github.com/PhysiCell-Tools/PhysiCell-model-builder/archive/refs/tags/v2.8.6.tar.gz
RUN tar zxf v2.8.6.tar.gz

WORKDIR /app/PhysiCell-model-builder-2.8.6

COPY startgui.sh /startgui.sh
