// Parser adapted from https://github.com/jreeves3/unsat-proof-skeletons
// Original author Benjamin Kiesl-Ritter, MIT-0 License

#ifndef MAXSAT2KNF_H
#define MAXSAT2KNF_H

#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <tuple>
#include "assert.h"
#include "knf-parse.hpp"


using namespace std;

class KnfCheck : public KnfParserObserver {
public:
  
  KnfCheck () {
    acc_soft_weight = 0;
    max_weight = -2;
  }

  void Header(int max_var, int max_cls, int max_weight) override {

    this->max_var = max_var;
    this->max_cls = max_cls;
    this->max_weight = max_weight;

  }

  void Clause(vector<int>& lits, double weight, string s_weight) override {

    if (lits.size() == 0) {
      cout << "empty lits\n";
      cout << "Line number " << cardinality_constraints.size() + clauses.size() << endl;
      return;
    }

    vector<int> temp = lits;

    clauses.push_back(temp);
    clause_weights.push_back (weight);
    clause_s_weights.push_back (s_weight);
    if (has_weight ())
      {if (stoi (s_weight) != max_weight ) acc_soft_weight += stoi (s_weight);}

  }

  void CardinalityConstraint(vector<int>& lits, int bound, double weight, string s_weight, int guard) override {

    vector<int> temp = lits;
    int tempB = bound;

    if (lits.size() == 0) {
      cout << "empty lits\n";
      cout << "Line number " << cardinality_constraints.size() + clauses.size() << endl;
      return;
    }

    if (bound == 0) { // trivially satisfied constraint??
      cout <<"trivially satisfied consrtaint with bound 0\n";
      cout << "Line number " << cardinality_constraints.size() + clauses.size() << endl;
      return;
    }

    if (bound == 1) { // keep clauses separate
      Clause (lits, weight, s_weight);
    } else {
      cardinality_constraints.push_back(make_tuple(temp, bound));
      card_weights.push_back (weight);
      card_s_weights.push_back (s_weight);
      card_guards.push_back (guard);
      
      if (has_weight ())
      {if (stoi (s_weight) != max_weight ) acc_soft_weight += stoi (s_weight);}
    }

  }


  void Comment(const string& comment) override {;}


  void write_clause (int cidx) {
    for (auto lit : clauses[cidx]) cout << lit << " ";
    cout << 0 << endl;
  }

  void write_card (int cidx) {
    for (auto lit : get<0> (cardinality_constraints[cidx])) cout << lit << " ";
    cout << 0 << endl;
  }

  void writeKnf (string out_path) {

    ofstream out_file(out_path);

    cout << "writing to " << out_path << endl;

    out_file << "c converted file format" << endl;

    int new_cls = cardinality_constraints.size() + clauses.size();

    cout << "Old header with " << max_cls << " constraints, new header with " << new_cls << " constraints\n";

    // write header
    if (has_weight()) out_file << "p wknf " << max_var << " " << new_cls << " " << max_weight << endl;
    else out_file << "p knf " << max_var << " " << new_cls << endl;

    // write clauses
    for (int i = 0; i < clauses.size(); i++) {
      if (has_weight()) out_file << clause_s_weights[i] << " ";
      for (auto lit : clauses[i]) out_file << lit << " ";
      out_file << "0" << endl;
    }

    // write cardinality constraints
    for (int i = 0; i < cardinality_constraints.size(); i++) {
      if (has_weight()) out_file << card_s_weights[i] << " ";
      auto tpl = cardinality_constraints[i];
      out_file << "k " << get<1>(tpl) << " ";
      for (auto lit : get<0>(tpl)) out_file << lit << " ";
      out_file << "0" << endl;
    }

    out_file.close ();

  }

  bool has_weight () {return max_weight != -2;}

  void SetMaxVar () override {
    // write clauses
    for (int i = 0; i < clauses.size(); i++) {
      for (auto lit : clauses[i]) {
        if (abs (lit) > max_var) max_var = abs (lit);
      }
    }

    // write cardinality constraints
    for (int i = 0; i < cardinality_constraints.size(); i++) {
      auto tpl = cardinality_constraints[i];
      for (auto lit : get<0>(tpl)) {
        if (abs (lit) > max_var) max_var = abs (lit);
      }
    }

  }

  void write_hard_clause (vector<int> lits, ofstream &file) {
      file << "h ";
      for (auto lit : lits) {
        file << lit << " ";
      }
      file << "0\n";
  }

  void write_soft_unit (int lit, ofstream &file) {
    file << "1 " << lit << " 0\n";
  }

  void write_hard_clause_knf (vector<int> lits, ofstream &file, bool write) {
      if (write) {
        for (auto lit : lits) {
          file << lit << " ";
        }
        file << "0\n";
      }

      clause_knf_cnt++;
  }

  void write_soft_unit_knf (int lit, ofstream &file, bool write) {
    if (write)
      file << lit << " 0\n";
    clause_knf_cnt++;
  }

  int write_soft_clause_knf (vector<int> lits, ofstream &file, int new_max_var, vector<int> &soft_units, bool write) {
      
      if (lits.size() == 1) {
        // standard soft clause
        soft_units.push_back (lits[0]);

        // Only an issue if cardinality constraint cannot support duplicate literals
        // if (pos_used_soft_lits [abs(lits[0])] == 1) {
        //   cout << "ERROR soft unit " << lits[0] << " already used\n";
        //   exit (1);
        // }

        pos_used_soft_lits [abs(lits[0])] = 1;
      } else {
        // create new hard clause and new soft unit
        lits.push_back (-new_max_var);
        soft_units.push_back (new_max_var);
        write_hard_clause_knf (lits, file, write);
        new_max_var++;
      }
      return new_max_var;
  }

  int write_soft_clause (vector<int> lits, ofstream &file, int new_max_var) {
      
      if (lits.size() == 1) {
        // standard soft clause
        write_soft_unit (lits[0], file);
      } else {
        // create new hard clause and new soft unit
        write_soft_unit (new_max_var, file);
        lits.push_back (-new_max_var);
        write_hard_clause (lits, file);
        new_max_var++;
      }
      return new_max_var;
  }

  void MaxSAT2KNF (string out_path, int add_bound) {
    ofstream out_file(out_path);

    vector<int> soft_units;


    // check if formula has only single polarity
    // vector<int> pos_occs, neg_occs;
    // for (int i = 0; i <= max_var; i++) {
    //   pos_occs.push_back(0);
    //   neg_occs.push_back(0);
    // }

    // for (int i = 0; i < clauses.size(); i++) {
    //   for (auto lit : clauses[i]) {
    //     int sign = lit > 0;
    //     int var = abs(lit);

    //     if (sign) pos_occs[var]++;
    //     else neg_occs[var]++;

    //     if (pos_occs[var] > 1 && neg_occs[var] > 1) {
    //       cout << "Both polarities\n";
    //       exit (1);
    //     }
    //   }
    // }

    // cout << "Single polariy\n";

    // exit (0);

    for (int i = 0; i <= max_var; i++) {
      pos_used_soft_lits.push_back(0);
      neg_used_soft_lits.push_back(0);
    }

    int old_max_var = max_var;

    int new_max_var = max_var + 1;

    clause_knf_cnt = 0;


    // process formula, 
    //   check if any soft clauses have len > 1 and require
    //   new variables to become unit (modify maxVar and nClauses)
    for (int i = 0; i < clauses.size(); i++) {
      if ( (clause_weights[i]) == max_weight)
        write_hard_clause_knf (clauses[i], out_file, 0);
      else
        new_max_var =  write_soft_clause_knf (clauses[i], out_file, new_max_var, soft_units, 0);
    }

    // print header
    out_file << "p knf " << new_max_var - 1 << " " << clause_knf_cnt + 1 << endl; 

    // print cardinality constraint over the soft units
    if (add_bound) {
      out_file << "k " << soft_units.size() - add_bound;
      for (auto lit : soft_units) out_file << " " << lit;
      out_file << " 0\n";
    }

    new_max_var = old_max_var + 1;

    clause_knf_cnt = 0;

    // write hard clauses and soft clauses
    for (int i = 0; i < clauses.size(); i++) {
      // write hard clauses like normal
      if ( (clause_weights[i]) == max_weight)
        write_hard_clause_knf (clauses[i], out_file, 1);
      else
        new_max_var =  write_soft_clause_knf (clauses[i], out_file, new_max_var, soft_units, 1);

    }

  }

  void fix_MaxSAT (string out_path) {
    ofstream out_file(out_path);

    int new_max_var = max_var + 1;

    for (int i = 0; i < clauses.size(); i++) {
      // write hard clauses like normal
      if ( (clause_weights[i]) == max_weight)
        write_hard_clause (clauses[i], out_file);
      else
        new_max_var =  write_soft_clause (clauses[i], out_file, new_max_var);

    }

    out_file.close ();

  }

private:

  vector<vector<int>> clauses;
  vector<tuple<vector<int>,int>> cardinality_constraints;
  vector<int> card_guards;
  vector<int> clause_weights, card_weights;
  vector<string> clause_s_weights, card_s_weights;

  vector<int> assignment;

  vector<int> pos_used_soft_lits, neg_used_soft_lits;

  int max_var, max_cls, max_weight, cardSat,cardUnsat,clauseSat,clauseUnsat;

  int acc_soft_weight;

  int total_soft_unsat_weight, total_soft_sat_weight;
  int card_total_soft_unsat_weight, card_total_soft_sat_weight;

  int hard_sat, hard_unsat, soft_sat, soft_unsat;
  int card_hard_sat, card_hard_unsat, card_soft_sat, card_soft_unsat;

  int clause_knf_cnt;

};

#endif