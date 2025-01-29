#!/bin/bash

formula=$1
ordering=$2
encoding=$3

PREPROC=tools/order_and_encode.py
CADICAL=cadical/build/cadical

outcnf=$encoding"_"$ordering".cnf"

timeout=1800

TMP=tmp

mkdir -p $TMP


if [ $ordering == "natural+PAMO" ]; then 
  # run natural for 100 seconds then PAMO
  timeout 100s sh scripts/run_preproc_and_solve.sh $formula natural $encoding > $TMP/orig.out

  if grep -q "satisfiable" $TMP/orig.out; then
    cat $TMP/orig.out
  elif grep -q "unsatisfiable" $TMP/orig.out; then
    cat $TMP/orig.out
  else 
    # solver returns unknown
    # try proximity for remaining 1700seconds
    echo Unsolved in natural
    timeout 1700s sh scripts/run_preproc_and_solve.sh $formula proximity $encoding
  fi

else 
  # standard ordering

  # run preprocessor
  echo "\nRun Preprocessor"
  time timeout $timeout"s" python3 $PREPROC -k $formula -e $encoding -v $ordering -c $TMP/$outcnf -q $TMP/temp.ord

  # run solver
  echo "\nRun Solver"
  time timeout $timeout"s" ./$CADICAL $TMP/$outcnf > $TMP/cadical.out

  # print solver result
  if grep -Fxq "s SATISFIABLE" $TMP/cadical.out; then
    echo "\nSolver returns satisfiable"
  elif grep -Fxq "s UNSATISFIABLE" $TMP/cadical.out; then
    echo "\nSolver returns unsatisfiable"
  else 
    echo "\nSolver returns unknown"
  fi

fi
