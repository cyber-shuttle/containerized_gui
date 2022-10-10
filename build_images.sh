#!/bin/sh

docker build -t gui-base dockerfiles/base/
docker build -t gimp dockerfiles/gimp/
docker build -t physicell dockerfiles/physicell/
