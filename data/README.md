# Data for The Impact of Literal Sorting on Cardinality Constraints

Supplementary materials for AAAI submission, data CSV files and processing.

To run, use

```bash
python3 process_data_paper.py [-c] [-p] [-t]
```

Options:

-c : cactus plot Figure 6
-p : preprocessing plot Figure 5
-t : tables 1 and 2

CSV files hold preprocessing and solving data for encoding types and ordering configurations mentioned in AAAI submission. Only kmtotalizer has an evaluation on all ordering configurations, and other encoding types use a selection of the ordering configurations.

MaxSAT benchmark information including number of hard clause, bound, and number of soft constraints is also included. 

coverage.txt contains the coverage data used in the paper.