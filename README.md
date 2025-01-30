# The Impact of Literal Sorting on Cardinality Constraints

Supplementary materials for AAAI submission, includes preprocesor (literal sorting) code and evaluation data. Find the SAT solver cadical at https://github.com/arminbiere/cadical and place it in the main directory to run solving scripts. 

We provide a selection of benchmarks from the evaluation for running local experiments, along with a maxsquares benchmark (not from evaluation) with a fast solving time for testing.

## Build All

To build use

```bash
sh build.sh
```

Requires python3 and modules PySAT (for cardinality constraint encodings), networkx (for community detection).
`pip3 install python-sat`
`pip3 install networkx`

To clean use

```bash
sh clean.sh
```

## KNF format

KNF (cardinality conjunctive normal form) has the same format as dimacs CNF with the addition of at-least-k cardinality constraints, denoted with a `k` and followed by a bound:

`k <bound> <literals> 0`

The header for KNF is `p knf <maxVariable> <numberConstraints>`

The formulas we allow are in KNF with some number of clauses and a single cardinality constraint. These resemble the SAT problems generated from MaxSAT benchmarks.

## Generate CNF from KNF

A script that runs a literal sorting configuration then encodes the input SAT problem (given in KNF format) into a CNF formula.

The AMO extraction is adapted from the work in (https://github.com/jreeves3/Cardinality-CDCL)

The script will print the new variable ordeirng for the cardinality constraint.

Orderings and encodings are described in more detail in the paper.

Orderings include: natural, occurence, proximity, PAMO, random_fixed_`seed`, natural+PAMO, PAMO+Occur, graph
Encodings from PySAT include: seqcounter, sortnetwrk, cardnetwrk, mtotalizer, kmtotalizer

If you would like to print the same KNF except with literals sorted (no clausal encoding), use original_cardinality as the encoding.

```bash
 > python3 tools/order_and_encode.py -k <knf_formula> -e <encoding> -v <ordering> -c <output_cnf_Formula> -q <ordering>
 ```

An example run,
```bash
 > python3 tools/order_and_encode.py -k benchmarks/maxsquare-7-33-unsat.knf -e kmtotalizer -v PAMO -c tmp/maxsquare_kmtotalizer_PAMO.cnf -q tmp/maxsquare_kmtotalizer_PAMO.ord
 ```


## Generate CNF from KNF and Solve the CNF

This script will generate a CNF formula using the provided encoding type and ordering configuration, place the formula in the `tmp` directory, then will run CaDiCaL on the CNF formula.

For natural+PAMO, CaDiCaL is run on the natural formula for 100 seconds, if this times out then CaDiCaL is run on the PAMO formula.

The script has an 1800 timeout for both preprocessing and solving (note, in the paper the timeout includes both preprocessing and solving)

```bash
 > sh scripts/run_preproc_and_solve.sh <knf_Formula> <ordering> <encoding>
 ```

An example run,
 ```bash
 > sh scripts/run_preproc_and_solve.sh benchmarks/maxsquare-7-33-unsat.knf PAMO kmtotalizer 
 ```

SAT solver used for evaluation (not modified in this work):
* CaDiCaL (https://github.com/arminbiere/cadical)

## Get Coverage for a KNF formula

We provide a script to obtain the coverage for the orderings (occurence, proximity, natural, graph) and formula presented in the paper:

```bash
 > sh scripts/run_coverage.sh benchmarks/extension-enforcement-extension-enforcement_strict_com_100_0.05_4_20_3-unsat.knf
```

Note, you can get the coverage for any formula in KNF that has a single cardinality constraint using any of the provided ordering types by editting the script as needed.

## Data

Refer to the readme inside the data directory.

## Convert MaxSAT formulas to KNF

If you wish to generate the entire benchmark set used in the evaluation, you can do so by following the steps below:

- Download MaxSAT 2023 competition unweighted track benhcmark set (https://maxsat-evaluations.github.io/2023/benchmarks.html)
  - place benchmarks in directory mse23-exact-unweighted-benchmarks and decompress them
- run `python3 scripts/MaxSAT_to_knf.py`

MaxSAT_to_knf.py calls ./maxSAT2KNF from maxSAT_to_KNF for each benchmark that has an optimum bound greater than 1 and less than the number of soft units - 1, creating both a satsifiable and unsatisfiable SAT problem in KNF format. You can call the converter directly with the following command line options.

```bash
 > ./maxSAT_to_KNF/maxSAT2KNF  {maxSAT_Formula} -MaxSAT2KNF {knf_Formula-sat} -add_bound {bound}
 > ./maxSAT_to_KNF/maxSAT2KNF  {maxSAT_Formula} -MaxSAT2KNF {knf_Formula-unsat} -add_bound {bound-1}
```