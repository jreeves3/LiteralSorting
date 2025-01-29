#!/bin/bash

formula=$1

# argument -z to print coverage
for sorting in occurence proximity natural graph; do
  echo "\n\nVariable ordering then Coverage for "$sorting"\n"
  python3 tools/order_and_encode.py -k $formula -v $sorting -z
done
