import sys
import os
import csv

'''

  Script to convert the maxSAT comp 23 problems into SAT and UNSAT KNF formulas (one SAT and one UNSAT for each known bound that is not 1 or len(soft units) -1)

'''
def get_formula_data (file) :
  data = {}
  candidates = []
  with open(file, mode='r') as csvFile:
    csvReader = csv.DictReader(csvFile)
    for line in csvReader:
      temp_b = line["Name"]
      data[temp_b] = line
      candidates.append(temp_b)
  return candidates, data

def convertmax2knf():

  candidates, formula_data = get_formula_data ("data/maxSAT_formula_info.csv")

  for b in candidates:

    # Remove formulas with optimal bound that does not allow but 
    # sat/unsat formulas, or would force an AMO constraint
    bound = int(formula_data[b]['UnsatBound']) - 1
    if (int(formula_data[b]['SoftUnits']) - bound) < 2 or bound < 2:
      continue

    # rewriten to match converter formatting for optimal bound
    bound = (int(formula_data[b]['SoftUnits']) - int(formula_data[b]['UnsatBound']) ) + 1

    converter = "maxSAT_to_KNF/maxSAT2KNF"
    in_file = f"mse23-exact-unweighted-benchmarks/{b}.wcnf"
    ofile_sat = f"benchmarks/{b}-sat.knf"
    ofile_unsat = f"benchmarks/{b}-unsat.knf"
    
    sys.stdout.flush()
    # write the SAT formula
    os.system (f"{converter} {in_file} -MaxSAT2KNF {ofile_sat} -add_bound {bound}")

    # write the UNSAT formula with a modified bound
    os.system (f"{converter} {in_file} -MaxSAT2KNF {ofile_unsat} -add_bound {bound-1}")

    
#######################################################################################
# MAIN FUNCTION
#######################################################################################
  
def run(name, args):
    
    convertmax2knf()
        

if __name__ == "__main__":
    run(sys.argv[0], sys.argv[1:])
