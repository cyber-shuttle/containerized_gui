#!/bin/bash

ARCH=$(arch)
if [ $ARCH == "aarch64" ]; then
    make CFLAGS="-march=native -O3 -fomit-frame-pointer -fopenmp -std=c++11"
else
    make
fi
