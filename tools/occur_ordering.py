from functools import cmp_to_key
import sys
import getopt
import random
# import lzma


'''
This script parses a KNF formula and returns a variable ordering by

  1. Parsing the KNF
  2. Counts occurences (during parsing)
  5. Prints the ordeirng


Default Exuection:

  > python3 occur_ordering.py <KNF> > <ORDER>


Note on modules,

  Assuming the input is not zipped with lzma so commenting code to reduce dependencies
'''

def trim(s):
    while len(s) > 0 and s[-1] in '\r\n':
        s = s[:-1]
    return s
    
def remove_comment(s):
  for i in range(len(s)):
    if s[i] == 'c': return s[:i]
  return s
  
def generate_occ_ordering (knf_input):


  # open knf formula (likely zipped with xz)
  knf_lines = None
  # if (knf_input.endswith('.xz')):
  #   knf_lines = lzma.open(knf_input, mode='rt', encoding='utf-8')
  # else:
  knf_lines = open(knf_input, 'r')


  clauses = [] # clauses (list of list of integers)
  max_var = None  # max variables used to set new auxiliary variables in encodings

  # get number of variables from header for 
  for line in knf_lines:
    line = trim(line)
    tokens = line.split()

    if tokens[0] == "p": # pcnf header
      max_var = int(tokens[2])
      break

  var_occ_cnt = [0] * (max_var + 1)
  



  # 1. Parse KNF formula
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
      
      for l in literals:
        # use bound as crude estimate of # occs in clauses
        # Does not affect AAAI orderings because MaxSAT problems have 
        # one large cardinality constraint so all of those soft units
        # will get same bump here, and will be differentiated by occurs
        # in the hard clauses.
        var_occ_cnt [abs(l)] += bound 

    else: # standard clause
      literals = [int (lit) for lit in tokens[:-1]] # remove last '0'
      for l in literals:
         var_occ_cnt [abs(l)] += 1

  knf_lines.close()

  ps = list (zip (range(1,max_var+1),var_occ_cnt[1:]))

  # Sort in descending order
  ps.sort(key=lambda x : x[1], reverse=True)

  # 3. Print ordering
  l = []
  for i in range(max_var):
     l.append(str(ps[i][0]))
  print(' '.join(l))

    
def run(name, args):
    
    knf_input = None
    
    optlist, args = getopt.getopt(args, "k:")
    for (opt, val) in optlist:
        if opt == '-k':
            knf_input = val
    
    generate_occ_ordering (knf_input)
    
if __name__ == "__main__":
    run(sys.argv[0], sys.argv[1:])
