from functools import cmp_to_key
import sys
import getopt
import random
import os
# from pysat import *
from pysat.card import *



'''
This script parses a KNF formula orders literals within cardinality constraints, then encodes to CNF

  1. Parsing the KNF
  2. Run some variable ordering algorithm
  3. Encode cardinality constraints with new ordering and given encoding type
  4. Print the CNF


Default Exuection:

Note seed for random,

  > python3 order_and_encode.py <KNF> > <ORDER>

You can also use this script to print the coverage statistics for an ordering

  > python3 


Note on modules,

  pysat module is included in the supplementary materials Readme

'''

def trim(s):
    while len(s) > 0 and s[-1] in '\r\n':
        s = s[:-1]
    return s
    
def remove_comment(s):
  for i in range(len(s)):
    if s[i] == 'c': return s[:i]
  return s

def write_clause(file, clause):
   file.write(' '.join(str (lit) for lit in (clause + [0])) + "\n")

def write_hclause(file, clause):
   file.write("h " + ' '.join(str (lit) for lit in (clause + [0])) + "\n")

# sort the literals based on the positions in the var_map
# the smaller the value, the closer to the front of the list
# example: with map [1->3, 2->2, 3->1] and literals [1,2,3] return [3,2,1]
def sort_literals(literals, var_map):
   def compare_map(e1,e2):
      if var_map[abs(e1)] >= var_map[abs(e2)]:
         return 1 
      else:
         return -1
      
   new_lits = sorted(literals, key=cmp_to_key(compare_map))
   return new_lits
  
# Parse the ordering returns by an ordering algorithm
def parse_ordering (in_file, var_map, max_var):
  lines = open(in_file, 'r')
  cnt = 1

  already_parsed = {}

  for line in lines:
    line = trim(line)
    tokens = line.split()

    for sv in tokens:
      v = abs(int(sv))

      if v in already_parsed:
        print("Error, appears twice")
        exit ()
      else:
        already_parsed[v] = 1

      var_map[v] = cnt
      cnt += 1

  return var_map

# 1. Parse the KNF formula
def parse_knf (knf_input):
  knf_lines = open(knf_input, 'r')
  
  klauses = []
  soft_units = []

  for line in knf_lines:
    line = trim(line)
    tokens = line.split()

    if len(tokens) == 0: # empty line
       continue

    if tokens[0] == "p": # pcnf header
      continue
  
    if tokens[0] == "c": # comment
       continue
    
    if tokens[0] == "k": # cardinality constraint
      literals = [int(lit) for lit in tokens[2:-1]]
      bound = int (tokens[1])

      klauses.append ((bound, literals))
      soft_units += [abs(int(lit)) for lit in tokens[2:-1]]

    else: # standard clause
      literals = [int (lit) for lit in tokens[:-1]] # remove last '0'
      klauses.append((1,literals))


  return klauses, list(set(soft_units))

def parse_knf_remove_soft (knf_input, soft):
  knf_lines = open(knf_input, 'r')
  
  clauses = []
  is_soft = {}
  occs = {}
  for v in soft: is_soft[v] = 1

  for line in knf_lines:
    line = trim(line)
    tokens = line.split()

    if len(tokens) == 0: # empty line
       continue

    if tokens[0] == "p": # pcnf header
      continue
  
    if tokens[0] == "c": # comment
       continue
    
    if tokens[0] == "k": # cardinality constraint
      continue

    else: # standard clause
      literals = [abs (int (lit)) for lit in tokens[:-1] if (abs(int(lit))) in is_soft] # remove last '0'
      if len(literals) > 0: clauses.append(literals)

      for v in literals:
        if v not in occs:
          occs[v] = [len(clauses) - 1]
        else:
          occs[v].append(len(clauses) - 1)

  return clauses, occs

# Print the coverage statistic, using tikz style printing format
def print_coverage (order, soft, clauses, occs,maxVar, cnt):

  colors = ["darkestblue","redpurple","browngreen","clearorange","darkpurple","greypurple","redorange","softblue","softgreen","clearyellow","mildgray"]

  marks = ["x", "o","diamond","square","star","+","triangle"]


  shuff_vars = sort_literals (soft,order)
  nCov = 0
  nCovs = []
  cls_done = {}
  lit_seen = [0]*(maxVar+1)

  # loop over the variables in the new ordering
  for v in shuff_vars:
    lit_seen[v] = 1
    # append the new count of covered clauses (init at 0)
    nCovs.append(nCov)
    if v not in occs: continue
    for cid in occs[v]:
      if cid in cls_done: continue 
      notS = False
      for v in clauses[cid]:
        if lit_seen[v] == 0: 
          notS = True 
          break
      if notS:
        continue 
      # new clause has been covered
        # mark as covered and add one to covered count
      cls_done[cid] = 1
      nCov += 1
  # append the final count of covered clauses = number of clauses in the formula touhced by variables in cardinality constraints
  nCovs.append(nCov)

  # print the coverage
  st = ("\\addplot[only marks, color="+colors[cnt%len(colors)]+",mark="+marks[cnt%len(marks)]+",opacity=0.5] coordinates { ")
  for i in range(len(nCovs)):
    st +=  ("("+str(i) + "," + str(nCovs[i]) + ")")
  st += ("};")
  print(st)
      

def sign_int (l):
  if l > 0: return 1
  else: return -1

def rename_knf (klauses, var_map, max_var):
  new_klauses = []

  for (bound,lits) in klauses:
    new_lits = [sign_int (l) *var_map[abs(l)] for l in lits]
    new_klauses.append((bound,new_lits))

  return new_klauses


# 4. Write the SAT problem as a CNF, encoding cardinality constraints with the 
# specified encoding type and the new literal ordering
def write_cnf (klauses, var_map, max_var, cnf_output, encoding_type, rename):
  clauses = []
  # loop over input KNF formula, replacing cardinality constraints with encoded clauses
  for (bound, literals) in klauses:
    if bound > 1: # cardinality constraint
      if rename:
        shuffled_literals = sort_literals(literals, list(range(0,max_var+1)))
      else:
        # shuffle literals inside the cardinality consrtaint based on new ordering
        shuffled_literals = sort_literals (literals, var_map)

      # if localMAC:
      #   print(shuffled_literals)


      # encode using the specific encoding type from PySAT
      if encoding_type == "original_cardinality":
        clauses.append (["k",str(bound)] + shuffled_literals)
      else:
        new_cnf = None
        if encoding_type == "seqcounter":
          new_cnf = CardEnc.atleast(shuffled_literals, bound, max_var,encoding=EncType.seqcounter) 
        elif encoding_type == "totalizer":
          new_cnf = CardEnc.atleast(shuffled_literals, bound, max_var,encoding=EncType.totalizer)
        elif encoding_type == "sortnetwrk":
          new_cnf = CardEnc.atleast(shuffled_literals, bound, max_var,encoding=EncType.sortnetwrk)
        elif encoding_type == "cardnetwrk":
          new_cnf = CardEnc.atleast(shuffled_literals, bound, max_var,encoding=EncType.cardnetwrk)
        elif encoding_type == "mtotalizer":
          new_cnf = CardEnc.atleast(shuffled_literals, bound, max_var,encoding=EncType.mtotalizer)
        elif encoding_type == "kmtotalizer":
          new_cnf = CardEnc.atleast(shuffled_literals, bound, max_var,encoding=EncType.kmtotalizer)
        else:
          print(f"Error: encoding type {encoding_type} not recognized")
          exit()

        # Update max variable based on largest aux variable used in the encoding
        max_var = max([max([abs(l) for l in lits]) for lits in new_cnf.clauses])
        clauses = clauses + new_cnf.clauses

    else: # standard clause
      clauses.append(literals)

  # write the output CNF formula
  out_file = open(cnf_output, 'w')

  # header  
  if encoding_type == "original_cardinality":
    out_file.write("p knf "+str(max_var)+" "+str(len(clauses))+"\n")
  else:
    out_file.write("p cnf "+str(max_var)+" "+str(len(clauses))+"\n")

  for clause in clauses:
     write_clause (out_file, clause)

  out_file.close()


'''
Writing MaxSAT problem, not used in AAAI paper

Assuming the one big cardinality constraint is actually all of the soft clauses
'''
def write_wcnf (klauses, var_map, max_var, cnf_output):
  clauses = []
  soft_units = []
  # loop over input KNF formula, replacing cardinality constraints with encoded clauses
  for (bound, literals) in klauses:
    if bound > 1: # cardinality constraint
      for l in literals:
        soft_units.append(l)

    else: # standard clause
      clauses.append(literals)

  # write the output CNF formula
  out_file = open(cnf_output, 'w')

  soft_units.sort()
  for l in soft_units:
    out_file.write("1 " + str(l)+" 0\n")
  for clause in clauses:
     write_hclause (out_file, clause)

  out_file.close()

'''
  Get new variable ordering

  Encode into CNF or calculate coverage statistic
'''
def generate_cnf (knf_input, cnf_output, encoding_type, variable_ordering_type, random_seed, rename, maxSAT_out, bias_change,  occLimit, tempOrdered, get_coverage, temp_order_file):

  # set random seed
  random.seed(random_seed)

  # open knf formula (likely zipped with xz)
  knf_lines = None

  ## if needing to unzip
  # if (knf_input.endswith('.xz')):
  #   knf_lines = lzma.open(knf_input, mode='rt', encoding='utf-8')
  # else:

  knf_lines = open(knf_input, 'r')


  clauses = [] # clauses (list of list of literals)
  max_var = None  # max variables used to set new auxiliary variables in encodings
  max_cls = None

  # get number of variables from header for 
  for line in knf_lines:
    line = trim(line)
    tokens = line.split()

    if tokens[0] == "p": # pcnf header
      max_var = int(tokens[2])
      max_cls = int(tokens[3])
      break
  knf_lines.close()

  # set ordering for variables
  #  should map all variables up to max_var
  var_map = []

  # 2. Get the variable ordering, calling a separate script for more complex orderings
  
  if tempOrdered is not None:
    # Option to pass the ordering in directly via a file
    # Not used in AAAI paper
    for i in range(max_var+1):
      var_map.append(i)

    var_map = parse_ordering (tempOrdered, var_map, max_var)

  elif variable_ordering_type == "natural":
    # Every variable is mapped to itself, order by variable names
    for i in range(max_var+1):
      var_map.append(i)

  elif variable_ordering_type == "random_fixed":
    # basic random map
    for i in range(1,max_var+1):
      var_map.append(i)
    
    random.shuffle (var_map)

    # shift right one because zero is not a variable index
    var_map.insert(0,0)
  
  else:
    cmd = None # command to call for ordering script
    if variable_ordering_type == "graph":
      # call script that performs the community detection algorithm
      occ_script = "tools/VIG_ordering.py "
      cmd = ("python3 "+occ_script+" "+knf_input+" > " + temp_order_file)

    elif variable_ordering_type == "graphOcc":
      # call script that performs the community detection algorithm
      # with additional argument not used in AAAI paper
      occ_script = "tools/VIG_ordering.py "
      cmd = ("python3 "+occ_script+" "+knf_input+" -s > " + temp_order_file)

    elif variable_ordering_type == "occurence" or (occLimit > 0 and max_cls >= occLimit):
      # Call script that performs the occurence ordering algorithm.
      # Could count this locally but we kept it a separate script for consistency.
      occ_script = "tools/occur_ordering.py"
      cmd =  ("python3 "+occ_script+" -k "+knf_input+" > " + temp_order_file)

    elif variable_ordering_type == "proximity":
      # Call script that performs the proximity ordering algorithm.
      occ_script = "./tools/proximity/proximity"
      cmd = occ_script+" "+knf_input+" > " + temp_order_file

    elif variable_ordering_type == "PAMO":
      # Call script that performs the proximity ordering algorithm with AMO detection
      occ_script = "sh tools/PAMO.sh"
      cmd = occ_script+" "+knf_input+" " + temp_order_file

    if cmd is not None:
      os.system (cmd)

      for i in range(max_var+1):
        var_map.append(i)

      var_map = parse_ordering (temp_order_file, var_map, max_var)
    else:
      print(f"Error: variable ordering {variable_ordering_type} not recognized")
      exit()


  # print out ordering for comparative purposes...
  shuffled_all = sort_literals (list(range(1,max_var+1)), var_map)
  # if encoding_type == "kmtotalizer":
  print("Variable Order " + str(shuffled_all))

  # parse the KNF
  input_klauses, soft_units = parse_knf (knf_input)

  if get_coverage:
    # get the coverage statistics for an ordering then exit
    clauses, occs = parse_knf_remove_soft (knf_input, soft_units)
    lst = ["occurence", "proximity" ,"PAMO", "natural", "graph"]
    print_coverage (var_map, soft_units, clauses, occs, max_var, lst.index(variable_ordering_type))

    exit ()


  if rename:
    # rename only soft units, not other variables.
    # Not used in AAAI paper.

    soft_units = list(dict.fromkeys(soft_units)) # remove duplicates for renaming
    soft_units.sort()
    sorted_units = sort_literals (soft_units, var_map)
    is_soft = [0] * (max_var+1)
    for l in sorted_units:
      is_soft[abs(l)] = 1

    for i in range(max_var+1):
      if is_soft[i] == 1:
        var_map[i] =  soft_units[sorted_units.index(i)] #  sorted_units[soft_units.index(i)]
      else:
        var_map[i] = i
    klauses = rename_knf (input_klauses, var_map, max_var)
  else:
    klauses = input_klauses
  # klauses kept in order for backwards compatibility

  # output CNF or MaxSAT
  if maxSAT_out: # Not used in AAAI paper
    write_wcnf (klauses, var_map, max_var, cnf_output)
  elif cnf_output is not None:
    write_cnf (klauses, var_map, max_var, cnf_output, encoding_type, rename)
  
    
def run(name, args):
    
    knf_input = None
    cnf_output = None
    encoding_type = None
    variable_ordering_type = None
    random_seed = 0
    maxSAT_out = False
    rename = False

    occLimit = -1

    tempORDERED = None
    
    get_coverage = False
    
    temp_order_file = "temp.ord"

    bias_change = "0"

    optlist, args = getopt.getopt(args, "zrmk:c:e:v:s:b:o:t:q:")
    for (opt, val) in optlist:
        if opt == '-k':
            knf_input = val
        elif opt == '-c':
            cnf_output = val
        elif opt == '-s':
          random_seed = int(val)
        elif opt == '-e':
          encoding_type = val
        elif opt == '-v':
          variable_ordering_type = val
        elif opt == '-r':
          rename = True
        elif opt == '-m':
          maxSAT_out = True
        elif opt == '-b':
          bias_change = val
        elif opt == '-o':
          occLimit = int (val)
        elif opt == '-t':
          tempORDERED = val
        elif opt == '-z':
          get_coverage = True
        elif opt == '-q':
          temp_order_file = val

    if variable_ordering_type == "PAMO+Occur":
      variable_ordering_type = "PAMO"
      occLimit = 1000000 # set to one million before switching to Occur
    
    if "random_fixed" in variable_ordering_type:
      random_seed = int(variable_ordering_type[13:])
      variable_ordering_type = "random_fixed"
      
    generate_cnf (knf_input, cnf_output, encoding_type, variable_ordering_type, random_seed, rename, maxSAT_out, bias_change, occLimit, tempORDERED, get_coverage, temp_order_file)
    
if __name__ == "__main__":
    run(sys.argv[0], sys.argv[1:])
