#!/bin/bash

(cd tools/AMO_detection; sh clean.sh)
(cd cadical; make clean)
(rm tools/proximity/proximity)
(rm maxSAT_to_KNF/maxSAT2KNF)
(rm -r tmp)