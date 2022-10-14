FROM gui-base

RUN apt-get install -y \
    curl \
    g++ \
    make \
    python3 \
    python3-matplotlib \
    python3-pandas \
    python3-pyqt5 \
    python3-pyqt5.qtsvg \
    python3-scipy

RUN mkdir /app

# Build Physicell
WORKDIR /app
RUN curl -OL https://github.com/MathCancer/PhysiCell/archive/refs/tags/1.10.4.tar.gz
RUN tar zxf 1.10.4.tar.gz
WORKDIR /app/PhysiCell-1.10.4
# Build the 'template' project and copy the project executable to /usr/local/bin
RUN make template
COPY build_physicell.sh .
RUN ./build_physicell.sh
RUN cp project /usr/local/bin/

# Download Physicell Model Builder
WORKDIR /app
RUN curl -OL https://github.com/PhysiCell-Tools/PhysiCell-model-builder/archive/refs/tags/v2.8.6.tar.gz
RUN tar zxf v2.8.6.tar.gz

# startgui.sh assumes that this is the working directory
WORKDIR /app/PhysiCell-model-builder-2.8.6

COPY startgui.sh /startgui.sh
