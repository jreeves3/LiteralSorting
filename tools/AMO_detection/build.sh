#!/bin/bash

(cd tbuddy; make)
(cd src; make)

mv src/cnf2knf amo_detect