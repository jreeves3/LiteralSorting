import argparse
import os
from collections import defaultdict
from time import time
from typing import List
import networkx as nx
# from tqdm import tqdm
# import pickle


'''
This script parses a KNF formula and returns a variable ordering by

  1. Parsing the KNF
  2. Creating the variable incidence graph (VIG)
  3. Running community detection up to 50 times or until the timeout is reached
  4. Selecting a variable ordering from the best community
  5. Prints the ordeirng


Default Exuection:

  > python3 VIG_ordering.py <KNF> > <ORDER>


Note on modules,

  networkx module is included in the supplementary materials

  pickle allows uploading and downloading graphs, 
  currently commented out to avoid any package issues 
  during reproducibility checks.

  tqdm allows pretty time bars, again commented out to 
  avoid package issues.
'''


def vprint(*args, verbose=True, **kwargs):
    if verbose:
        print(*args, **kwargs)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("knf", help="Input KNF File to be reordered")
    parser.add_argument(
        "-w",
        "--weight",
        action="store_false",
        help="Weight each variable inside the group based on it's weight",
    )
    parser.add_argument(
        "-d",
        "--descending",
        action="store_false",
        help="Sort variables within the groups in descending order",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="Output file to write to after the reorder",
    )
    parser.add_argument(
        "-i",
        "--iteration",
        type=int,
        default=50,
        help="Max iteration for calculating Louvain Communities",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=300.0,
        help="Timeout for calculating Louvain Communities",
    )
    parser.add_argument(
        "-c",
        "--community",
        help="Pilckle file that store/load community result",
    )
    parser.add_argument(
        "-g",
        "--graph",
        help="Pilckle file that store/load graph",
    )
    parser.add_argument(
        "-s",
        "--sort-variables",
        action="store_true",
        help="Sort variables within the groups",
    )
    parser.add_argument(
        "-m",
        "--multi",
        action="store_true",
        help="Allow multiple same edges",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print out more information",
    )
    parser.add_argument(
        "-z",
        "--only_order",
        action="store_false",
        help="Print out the variable order",
    )
    return parser.parse_args()


def main(
    knf,
    sort_variables,
    weight,
    descending,
    output_file,
    iteration,
    timeout,
    only_order,
    verbose=False,
    graph_file=None,
    community_file=None,
    multi=False,
):
    clauses: List[List] = []
    _clauses: List[List] = []
    clauses_for_community_finding = []
    cardinality_constraint_bounds = []
    cardinality_constraints = []
    # DICT = defaultdict(list)
    info = ""
    var_occ_cnts = {}

    '''
    1. Parse the KNF formula

    - parse the clauses, with _clauses containing variables (absolute value of literals)
    - skip the cardinality constraints, not used in VIG, and only used if printing entire formula
    '''

    vprint("=== read file ===", verbose=verbose)
    with open(knf, "r") as input_file:
        cardinality_constraint_indexes = []

        info = input_file.readline()
        _, _, total_num_vars, _ = info.split()
        total_num_vars = int(total_num_vars)

        lines = input_file.readlines()
        for i in range(len(lines)):
            vars = lines[i].split()
            if vars[0] == "k":
                cardinality_constraint_indexes.append(i)
                continue
            clause = []
            _clause = []
            for j in range(len(vars) - 1):
                clause.append(int(vars[j]))
                _clause.append(abs(int(vars[j])))
                if  abs(int(vars[j])) not in var_occ_cnts:
                  var_occ_cnts [abs(int(vars[j]))] = 1
                else:
                  var_occ_cnts [abs(int(vars[j]))] += 1
            clauses.append(clause)
            _clauses.append(_clause)

        cardinality_constraints = [
            [0 for _ in range(total_num_vars)]
            for _ in range(len(cardinality_constraint_indexes))
        ]
        for i in range(len(cardinality_constraint_indexes)):
            vars = lines[cardinality_constraint_indexes[i]].split()
            cardinality_constraint_bounds.append(int(vars[1]))
            for j in range(2, len(vars) - 1):
                if int(vars[j]) > 0:
                    cardinality_constraints[i][int(vars[j]) - 1] += 1
                elif int(vars[j]) < 0:
                    cardinality_constraints[i][(-int(vars[j])) - 1] -= 1
    '''
    2. Create the VIG
    '''
    if graph_file is not None and os.path.exists(graph_file):
        vprint("=== load graph ===", verbose=verbose)
        # with open(graph_file, "rb") as fp:
        #     G = pickle.load(fp)
    else:
        if multi:
            G = nx.MultiGraph()
        else:
            G = nx.Graph()

        # NOTE: each variable is a node
        G.add_nodes_from(range(1, total_num_vars + 1))

        # NOTE: any two variables that in a same clause has an edge
        vprint("=== add edges ===", verbose=verbose)
        # PERF: improve performance for generating graph
        from itertools import combinations

        for c in _clauses:
            G.add_edges_from(combinations(c, 2))

        # if graph_file is not None:
        #     with open(graph_file, "wb") as fp:
        #         pickle.dump(G, fp)

    '''
    3. Detect communities
    '''
    if community_file is not None and os.path.exists(community_file):
        vprint("=== load louvain community ===", verbose=verbose)
        # with open(community_file, "rb") as fp:
        #     best_communities = pickle.load(fp)
    else:
        best_communities = []
        max_num_communities = 0
        vprint("=== Calculate Louvain Community ===", verbose=verbose)
        start = time()
        for i in range(iteration):
            # exit if we hit a timeout
            if (time() - start) > timeout:
                break
            # Seed with loop iteration index for reproducibility
            communities = nx.community.louvain_communities(G, seed=i)
            if len(communities) > max_num_communities:
                max_num_communities = len(communities)
                best_communities.clear()
                best_communities.append(sorted(map(sorted, communities)))
            elif len(communities) == max_num_communities:
                best_communities.append(sorted(map(sorted, communities)))
        # if community_file is not None:
        #     with open(community_file, "wb") as fp:
        #         pickle.dump(best_communities, fp)

    # with open('best', 'w') as f:
    #     f.write(f'{best_communities = }')


    '''
    4. Select a variable ordering from the best community
    '''
    best_group = []
    ideal_group_size = total_num_vars // len(best_communities[0])
    min_deviation = 99999999999

    for i in range(len(best_communities)):
        current_deviation = 0
        for group in best_communities[i]:
            current_deviation += abs(len(group) - ideal_group_size)
        if current_deviation < min_deviation:
            best_group = best_communities[i].copy()

    new_best = []
    if sort_variables:
      print("Sorting")
      for group in best_group:
        new_best.append((sorted(group, key=lambda x: var_occ_cnts[x],reverse=True)))

      best_group = new_best

    # print(best_group)
    '''
    5. Write the ordering to a file (or print out the formula with reordered cardinality constraints)
    '''
    k_constraints = []
    for index in range(len(cardinality_constraints)):
        literals = (
            str(i * (1 if cardinality_constraints[index][i - 1] > 0 else -1))
            for group in best_group
            for i in group
            for _ in range(abs(cardinality_constraints[index][i - 1]))
        )
        if only_order:
          k_constraints.append(
              f'{" ".join(literals)}'
          )
        else:
          k_constraints.append(
              f'k {cardinality_constraint_bounds[index]} {" ".join(literals)} 0\n'
          )

    if output_file is not None:
        if only_order:
          with open(output_file, "w") as f:
              f.write(
                  "".join(k_constraints[0] + " \n"
                  )
              )
        else:
          with open(output_file, "w") as f:
              f.write(
                  "".join(
                      [info]
                      + [line for line in lines if not line.startswith("k")]
                      + k_constraints
                  )
              )
    else:
      if only_order:
        print("".join(k_constraints[0] + " \n"))
      else:
        print("".join(k_constraints))


if __name__ == "__main__":
    args = parse_arguments()
    main(
        args.knf,
        args.sort_variables,
        args.weight,
        args.descending,
        args.output_file,
        args.iteration,
        args.timeout,
        args.only_order,
        args.verbose,
        args.graph,
        args.community,
        args.multi,
    )
