#include <iostream>
#include <string>
#include "maxSAT2KNF.hpp"

/*

Input : maxSAT formula, output formula name, bound
Output: KNF formula with hard constraints and one cardinality constraint over soft units, using the given bound

Run: ./max2knf {in_file} -MaxSAT2KNF {ofile_sat} -add_bound {bound}
*/


char* commandLineParseOption(char ** start, char ** end, const string & marker, bool &found) {
  char ** position = find(start,end,marker);
  found = false;
  if ( position != end ) found = true;
  if ( ++position == end) {return 0;}
  return *position;
}

void printHelp(char ** start, char ** end) {
  char ** position = find(start,end,"-h");
  if ( position == end ) return;
  
  cout << "Run: ./maxSAT2KNF <MaxSAT_formula> -MaxSAT2KNF {knf_Formula-sat} -add_bound {bound}" << endl;
  
  exit (0);
}


int main(int argc, char* argv[]) {
  
  
  printHelp(argv, argv+argc);

  bool fix_MaxSAT, MaxSAT2KNF, add_bound;
  fix_MaxSAT = MaxSAT2KNF = add_bound = 0;

  char * fix_MaxSAT_out = commandLineParseOption (argv, argv+argc, "-fix_MaxSAT", fix_MaxSAT);

  char * MaxSAT2KNF_out = commandLineParseOption (argv, argv+argc, "-MaxSAT2KNF", MaxSAT2KNF);

  char * add_bound_out_char = (commandLineParseOption (argv, argv+argc, "-add_bound", add_bound));
  int add_bound_out = 0;
  if (add_bound) {
    add_bound_out = stoi (add_bound_out_char);
  }

  string knf_path = argv[1];

  Input_Type input_type = UNKNOWN;
  
  KnfCheck knfcheck;

  PlainTextKnfParser knf_parser;
  knf_parser.AddObserver(&knfcheck);
  // cout << "Parsing formula\n";
  knf_parser.Parse(knf_path, input_type);

  if (fix_MaxSAT) {
    // cout << "Fixing MaxSAT\n";
    knfcheck.fix_MaxSAT (fix_MaxSAT_out);
    return 0;
  }

  if (MaxSAT2KNF) {
    // cout << "Transforming MaxSAT to KNF\n";
    knfcheck.MaxSAT2KNF (MaxSAT2KNF_out, add_bound_out);
    return 0;
  }

  return 0;
}
