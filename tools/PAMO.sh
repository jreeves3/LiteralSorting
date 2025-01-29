#!/bin/sh

INPUTKNF=$1
OUTPUTORD=$2

CNF2KNF="tools/AMO_detection/amo_detect"
PROX="tools/proximity/proximity"

 ./$CNF2KNF --Quick_Write=true --Direct_AMO_Small=false -Direct_timeout 25 -Encoded_timeout 25 $INPUTKNF > temp.amo

 cat $INPUTKNF temp.amo > temp.knf

 ./$PROX temp.knf > $OUTPUTORD

 rm temp.amo temp.knf

