#!/bin/sh

# How to build cadical once you have downloaded it
#(cd cadical; ./configure && make)


(cd tools/proximity; g++ --std=c++11 main.cpp -o proximity)
(cd tools/AMO_detection; sh build.sh)
(cd maxSAT_to_KNF; sh build.sh)
mkdir -p tmp