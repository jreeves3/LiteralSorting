import sys
import getopt
import csv

'''
Script for processing the data for the experimental evlauation in 
AAAI25 submission. Data is printed in a tikz style.

From the data directoy run,

  python3 process_data_paper.py [options]

  -t : print tables
  -p : print preprocessing plot
  -c : print cactus plot (for kmtotalizer)

Other options for more data processing should be ignored, 
are not relevant to the AAAI submission.

'''
   
colors1 = ["darkestblue","redpurple","browngreen","clearorange","darkpurple","black,thick","greypurple","redorange","softblue","softgreen","clearyellow","mildgray"]
colors = ["darkestblue","redpurple","browngreen","clearorange","darkpurple","greypurple","redorange","softblue","softgreen","clearyellow","mildgray"]

marks = ["x", "o","diamond","square","star","+","triangle"]

def tikz_cactus_header(title,xlabel,ylabel, xmin=0,xmax=2000,ymin=0,ymax=1000,xmode="",xleg=0.9,yleg=0.2):
  return "%\\begin{figure}\n% \\centering\n% \\begin{subfigure}[b]{.49\textwidth}\n\\centering\n\\begin{tikzpicture}[scale = 1.05]\n\\begin{axis}[mark options={scale=1.0},grid=both, grid style={black!10},  legend style={at={("+str(xleg)+","+str(yleg)+")}}, legend cell align={left},\nx post scale=1,xlabel="+xlabel+",ylabel="+ylabel+",mark size=3pt, "+xmode+"   height=12cm,width=12cm,ymin="+str(ymin)+",ymax="+str(ymax)+",xmin="+str(xmin)+",xmax="+str(xmax)+",title={"+title+"}]\n  \n"

def tikz_scatter_header(title,xlabel,ylabel):
  return "%\\begin{figure}\n% \\centering\n\\begin{tikzpicture}[scale = 1.05]\n\\begin{axis}[mark options={scale=1.0},grid=both, grid style={black!10},  legend style={at={(0.9,0.2)}}, legend cell align={left},\nx post scale=1,xlabel="+xlabel+", ylabel="+ylabel+",mark size=3pt, xmode=log,    ymode=log,height=12cm,width=12cm,xmin=0.1,xmax=2000,ymin=0.1,ymax=2000,title={"+title+"}]\n"
 
def tikz_ender():
  return  "\\end{axis}\n\\end{tikzpicture}\n%\\end{figure}"

def tikz_scatter_ender(legend):
  return  "\\addplot[color=black] coordinates {(0.009, 0.009) (1800, 1800)};\n\\addplot[color=black, dashed] coordinates {(0.009, 1800) (1800, 1800)};\n\\addplot[color=black, dashed] coordinates {(1800, 0.009) (1800, 1800)};\n\\"+legend+"\n\\end{axis}\n\\end{tikzpicture}\n%\\end{figure}"

def trim(s):
    while len(s) > 0 and s[-1] in '\r\n':
        s = s[:-1]
    return s
    
def strip_lead(s):
  skip = True
  new_s = ""
  for i in range(len(s)-1,0,-1):
    if skip:
      if s[i] == '.': skip = False
    else:
      if s[i] == '/':
        if new_s[-4:] == ".cnf":
          new_s = new_s[:-4]
        return(new_s)
      else: new_s = s[i] + new_s
 
 # Not used in AAAI submission
# def print_scatter ( scatter_times, ordering, sat, encoding, formula_data, scatMin, scatMax):
  
#   if sat == 2: print(tikz_scatter_header ("SAT "+encoding,"Natural", ordering))
#   elif sat == 1: print(tikz_scatter_header ("UNSAT "+encoding,"Natural", ordering))
#   else: print(tikz_scatter_header (encoding, "Natural",ordering))
  
#   legend = []
#   pos = -1
#   first_points = []
#   remaining_points = []
#   marks = ["x","diamond"]
#   # for i in range(len(families)):
#   for i in range(len(selected_families)):

#     # family = families[i]
#     family = selected_families[i]

#     first = True

#     if len(scatter_times[ordering][family]) == 0:
#       continue

#     color = colors[i%len(colors)]


    
#     mark = marks[0]
#     if i >= len(colors):
#       mark = marks[1]

    
#     legend.append(family.replace('_','-'))

#     for orgt,ot,sz,rs in scatter_times[ordering][family]:


#       if orgt < scatMin: orgt = scatMin
#       if ot < scatMin: ot = scatMin
#       if orgt > scatMax: orgt = scatMax
#       if ot > scatMax: ot = scatMax

#       if orgt == scatMin and ot == scatMin: continue
#       if orgt == scatMax and ot == scatMax: continue

#       if rs == 1: mark = marks[0]
#       else: mark = marks[1]
#       line = "\\addplot[color="+color+",mark="+mark+",opacity=0.5,mark size="+str(sz)+"pt] coordinates { ("+str(orgt) + "," + str(ot) + ") };"
#       if first:
#         first_points.append(line)
#         first=False
#       else:
#         remaining_points.append(line)

#   for line in first_points:
#     print(line)
#   for line in remaining_points:
#     print(line)

  
#   print("\\legend{"+", ".join(legend)+"}")

#   print(tikz_scatter_ender("legend{"+", ".join(legend)+"}"))  

# Not used in AAAI submission
# def print_scatter_ran ( scatter_times, ordering, sat, encoding):
  
#   if sat == 2: print(tikz_scatter_header ("SAT "+encoding,"Natural", ordering))
#   elif sat == 1: print(tikz_scatter_header ("UNSAT "+encoding,"Natural", ordering))
#   else: print(tikz_scatter_header (encoding, "Natural",ordering))
  
#   legend = []
#   pos = -1
#   first_points = []
#   remaining_points = []
#   clr_cnt = 0
#   for i in range(len(families)):

#     family = families[i]

#     first = True



#     if len(scatter_times["BestRan"][family]) == 0:
#       continue

#     color = colors[clr_cnt %len(colors)]
#     mark = marks[0]
#     if clr_cnt  >= len(colors):
#       mark = marks[1]

#     for orgt,bt,wt in scatter_times["BestRan"][family]:
#       if orgt < 0.1: orgt = 0.1
#       if bt < 0.1: bt = 0.1
#       if wt < 0.1: wt = 0.1

#       line = "\\addplot[color="+color+",mark="+mark+",opacity=0.5] coordinates { ("+str(orgt) + "," + str(bt) + ") ("+str(orgt) + "," + str(wt) + ") };"
#       if first:
#         first_points.append(line)
#         first=False
#       else:
#         remaining_points.append(line)

#     if not first:
#       legend.append(family.replace('_','-'))
#       clr_cnt += 1

#   for line in first_points:
#     print(line)
#   for line in remaining_points:
#     print(line)

  
#   print("\\legend{"+", ".join(legend)+"}")

#   print(tikz_scatter_ender("legend{"+", ".join(legend)+"}"))  


def print_preprocessing_times_cactus ( data, title, xTitle, yTitle ):
  var_types = []
  maxX = 0
  for v in data.keys():
    var_types.append(v)
    data[v].sort(key=lambda x:x[0])
    maxX = data[v][-1][0]

  print(tikz_cactus_header (title,xTitle,yTitle,100,maxX,0.4,1800,"xmode=log,ymode=log,","1","0.28"))

  for v in var_types:
    st = ("\\addplot[only marks, color="+colors[var_types.index(v)]+",mark="+marks[var_types.index(v)%len(marks)]+",opacity=0.5] coordinates { ")
    for cls,pre in data[v]:
      # make sure it shows up on the log plot
      if pre < 0.4: pre = 0.4
      
      st +=  ("("+str(cls) + "," + str(pre) + ")")
    st += ("};")
    print(st)
  print("\\legend{"+", ".join(var_types)+"}")
  print(tikz_ender())


def print_cactus ( solve_times,config, sat):
  
  c_list = []
  c_types= []
  solve_times_l = list(solve_times.items())
  solve_times_l.sort(key=lambda x:len(x[1]),reverse=True)
  for c,l in solve_times_l:
    c_list.append(sorted(l))
    c_types.append(c)

  # if sat == 2: print(tikz_cactus_header ("SAT "+config,"time (s)", "number solved",50,200))
  # elif sat == 1: print(tikz_cactus_header ("UNSAT "+config,"time (s)", "number solved",300,500))
  else: print(tikz_cactus_header (config + " sovled instances", "time (s)","number solved",0,1800,200,700,"","0.8","0.5"))
  
  legend = []
  pos = -1
  for i in range(len(c_types)):
    c = c_types[i]
    l = c_list[i]
    legend.append(c.replace('_','-'))
    cnt = 1
    pos += 1
    st = ""
    print ("\\addplot[color="+colors1[i%len(colors1)]+",mark="+marks[i%len(marks)]+",opacity=0.5] coordinates { ")
    for time in l:
      st += ("("+str(time) + "," + str(cnt) + ") ")
      cnt += 1
    st += ("("+str(2000) + "," + str(cnt-1) + ") };")
    print (st)

  
  print("\\legend{"+", ".join(legend)+"}")

  print(tikz_ender())  

families = [
  "unsat",
  "sat"
]
selected_families = [
  "unsat",
  "sat"
]

# MaxSAT competition unweighted track 2023 benchmark families
families = [
  "aes",
  "atcoss",
  "bcp",
  "biorepair",
  "Circuit",
  "close_solutions",
  "ConsistentQueryAnswering",
  "decision-tree",
  "drmx",
  "extension-enforcement",
  "fault-diagnosis",
  "frb",
  "gen-hyper",
  "Haplotype",
  "inconsistency-measure",
  "jobshop",
  "judgment-aggregation",
  "kbtree",
  "logic-synthesis",
  "MaxSATQueries",
  "mbd",
  "mqc",
  "min-fill",
  "optic-gen",
  "optimizing-BDDs",
  "planning-bnn",
  "program-disambiguation",
  "protein_ins",
  "pseudoBoolean",
  "railway",
  "reversi",
  "rna-alignment",
  "routing-normalized",
  "scheduling-cnf",
  "SeanSafarpour",
  "tpr",
  "treewidth",
  "uaq",
  "vpa",
  "xai"
]


def family_index (family):
  return families.index (family)

def get_family (formula):
  for f in families:
    if f == "normalized-":
      for i in range(2,10):
        if f+str(i) in formula:
          return f
    else:
      if f in formula:
        return f

  print(f"Missing family {formula}")
  exit ()

def get_name_seed (config):
  s = -1
  c = config

  if config[-2] == "_":
    s = int(config[-1])
    c = config[:-2]
  return c,s

# get preprocesisng and solving data from the CSV files
def get_csv_data_random (file) :
  candidates = []
  solve_stats = {}
  configurations = []
  with open(file, mode='r') as csvFile:
    csvReader = csv.DictReader(csvFile)
    for line in csvReader:
      temp_b = line["Name"]
      config_o = None

      encoding = None
      if "\ufeffEncoding" in line:
        encoding = line["\ufeffEncoding"]
      else: 
        encoding = line["Encoding"]

      config_o = line["Configuration"]

      (config,s) = get_name_seed (config_o)

      if encoding not in configurations: configurations.append (encoding)
      if temp_b not in candidates: candidates.append(temp_b)
      if not temp_b in solve_stats: solve_stats[temp_b] = {}
      if encoding not in solve_stats[temp_b]:
        solve_stats[temp_b][encoding] = {}

      if (config,s) in solve_stats[temp_b][encoding]:
        print (f"Duplicated {temp_b}")
        exit ()

      solve_stats[temp_b][encoding][(config,s)] = {'Pre-CPU':line['Pre-CPU'], 'solve-CPU':line['solve-CPU'], 'line':line}

  return candidates, solve_stats, configurations

def get_formula_data (file) :
  data = {}
  with open(file, mode='r') as csvFile:
    csvReader = csv.DictReader(csvFile)
    for line in csvReader:
      temp_b = line["Name"]
      data[temp_b] = line
  return data

# Combination of preprocessing and solving time.
# tiemout of 1800 seconds
def get_runt (stats,c,b,t,s=-1):
  t = float(stats[b][c][(t,s)]["solve-CPU"]) + get_pret (stats,c,b,t,s)

  if t > 1800: t = 1800

  return t

def get_pret (stats,c,b,t,s=-1):
  return float(stats[b][c][(t,s)]["Pre-CPU"])


'''
Get the data for solved instances and par2 scores on each formula for the given 
encoding and orderings.

Additional provided to print formulas from certain families and formulas 
with large solving time difference from Natural ordering. Not relevant 
to AAAI submission.

'''
def get_solve_data (solve_stats,c,orderings,benchmarks,diff_filt,pre_filt, do_print,print_ts, sat,  formula_data,realFamily,texTable, specialTexTable) :

    timeout = 1800

    # Pretty printing for other options
    syms = ["*","+","@","#","!","&",'^','{','}','^','%']
    zip_sims = {}
    cnt = 0
    st_keys = ""
    for o in orderings:
      zip_sims[o] = syms[cnt]
      cnt += 1
      if o != "Natural":
        st_keys += "{:<8} ".format(o+zip_sims[o])
    if do_print:
      print("\n\n******************************")
      print(c)
      print("******************************")
    if print_ts:
      print("{:<8} ".format("")+st_keys)
    st = ""
    for o in orderings:
      if o == "Random":
        st += "{:<8} {:<8} ".format("BestRan", "WorstRan")
      else:
        st += "{:<8} ".format(o)
    if print_ts:
      print(st+"Res Formula")


    l = []
    nSolved = 0
    solved = {}
    Par2 = {}
    Best = {}
    solve_times = {}

    # virtual best solver, selects best run for each formula
    VBS = {}
    VBS["par2"] = 0
    VBS["solved"] = 0

    scatters = {}

    chosen_families = {}

    if not realFamily:
      families = [
  "unsat",
  "sat"
]

    # Initializing data for each ordering configuration
    scatters["BestRan"] = {}
    for f in families:
      scatters["BestRan"][f] = []
    for o in orderings:
      if o == "Natural": continue
      scatters[o] = {}
      for f in families:
        scatters[o][f] = []
    for o in orderings:
      if o == "Random":
        solve_times["BestRan"] = []
        solve_times["WorstRan"] = []
        Par2["BestRan"] = 0
        Par2["WorstRan"] = 0
        solved["BestRan"] = 0
        solved["WorstRan"] = 0
        Best["BestRan"] = 0
        Best["WorstRan"] = 0
      else:
        solve_times[o] = []
        Par2[o] = 0
        solved[o] = 0
        Best[o] = 0

    nForms = 0
    for b in benchmarks:
      
      # remove -sat,-unsat from benchmark names to get Natural name
      # use -sat/unsat to get result of the formula
      fix_b = ""
      r_real = 0
      if "-unsat" == b[-6:]: 
        fix_b = b[:-6]
        r_real = 1
      elif "-sat" in b[-4:]: 
        fix_b = b[:-4]
        r_real = 2

      if sat == 2 and r_real == 2: 
        continue
      if sat == 1 and r_real == 1: 
        continue

      family = get_family (b)

      result = None
      if not realFamily:
        if r_real == 2:
          family = "sat"
          result = "SAT"
        elif r_real == 1:
          family = "unsat"
          result = "UNSAT"
        else:
          family = None

      orig = get_runt (solve_stats,c,b,"Natural")
      pass_filt = False

      # get runtimes (b_runs) and check if at least one ordering solved the formula
      new_b = b
      b_runs = {}
      one_solved = False
      for o in orderings:
        runt = None
        if o == "Random": # get best and worst random over 5 seeds
          worst = max([get_runt (solve_stats,c,b,"Random",s) for s in range(1,6)])
          runt = min([get_runt (solve_stats,c,b,"Random",s) for s in range(1,6)])
          b_runs['BestRan'] = runt
          b_runs['WorstRan'] = worst
        else:
          runt = get_runt (solve_stats,c,b,o)
          b_runs[o] = runt
        if runt < timeout:
          one_solved = True
          if abs(runt - orig) >= diff_filt and diff_filt > 0:
            pass_filt = True
          if runt < orig - 10:
            new_b = new_b + zip_sims[o]

      if one_solved:
        if family is None:
          print("ERRROR one solved but family is None")
          print(b)
          print(b_runs)
        diff_bound = diff_bound = int(formula_data[fix_b]["SoftUnits"]) - int(formula_data[fix_b]["UnsatBound"])
        mark_size = pow(diff_bound,1/3)
        if mark_size >10: mark_size = 10
        if mark_size < 2: mark_size = 2
        # For scatter plot (not used in AAAI submission)
        for o,t in b_runs.items():
          if "BestRan" in o:
            scatters[o][family].append((orig,b_runs['BestRan'],b_runs['WorstRan']))
          if o == "Natural" or "Ran" in o: continue
          scatters[o][family].append((orig,t,mark_size,r_real))

      # if max(b_runs.values()) < pre_filt and pre_filt > 0:
      #   continue

      # Update Par2 scores
      best_ordering = None
      best_time = timeout * 2
      nForms += 1
      for o in orderings:
          runt = None
          if o == "Random":
            runt = min([get_runt (solve_stats,c,b,"Random",s) for s in range(1,6)])
            worst = max([get_runt (solve_stats,c,b,"Random",s) for s in range(1,6)])
            if worst < timeout:
              Par2["WorstRan"] += worst
              solved["WorstRan"] += 1
            else:
              Par2["WorstRan"] += timeout * 2
            if runt < timeout:
              Par2["BestRan"] += runt
              solved["BestRan"] += 1
              if runt < best_time: # VBS update
                best_time = runt
                best_ordering = "BestRan"
            else:
              Par2["BestRan"] += timeout * 2
          else:
            runt = get_runt (solve_stats,c,b,o)
            if runt < timeout:
              Par2[o] += runt
              solved[o] += 1
              if runt < best_time: # VBS update
                best_time = runt
                best_ordering = o
            else:
              Par2[o] += timeout * 2

      VBS["par2"] += best_time
      if one_solved:
        nSolved += 1
        Best[best_ordering] += 1
        VBS["solved"] += 1

        # append solve times to list for cactus plots
        for o in orderings:
          runt = None
          if o == "Random":
            worst = max([get_runt (solve_stats,c,b,"Random",s) for s in range(1,6)])
            runt = min([get_runt (solve_stats,c,b,"Random",s) for s in range(1,6)])
            if worst < timeout:
              solve_times["WorstRan"].append(worst)
            if runt < timeout:
              solve_times["BestRan"].append(runt)
          else:
            runt = get_runt (solve_stats,c,b,o)
            if runt < timeout:
              solve_times[o].append(runt)

      # if not pass_filt: continue

      if family not in chosen_families:
        chosen_families[family] = 1
      chosen_families[family] += 1

      l.append((b_runs,result,new_b))

    # printing table to terminal for each formula
    # not used in AAAI submission
    l.sort(key=lambda x:x[2])
    for runs, res, b in l:
      st = ""
      for o in runs.keys():
        st += "{:<8} ".format(round(runs[o],2))
      if print_ts:
        print(st + str(res) + " "+b)
    
    # print number solved for basic table
    if texTable:
      st = ""
      st += "{:<8} & ".format(c)
      for o,v in solved.items():
        st += "{:<8} & ".format(v)
      print(st[:-2] + "\\\\")

    # Collect SAT and UNSAT solved and Par2 scores for special table
    specTable = []
    if specialTexTable:
      sum_best = 0
      row = ["VBS",VBS['solved'],int(VBS['par2']/nForms)]
      specTable.append(row)
      for o,v in solved.items():
        # st = "{:<8} & ".format(o)
        # st += "{:<8} & ".format(v)
        value = Par2[o]
        # st += "{:<8} & ".format(int(value/nForms))
        # st += "{:<8} & ".format(Best[o])
        # print(st[:-2] + "\\\\")
        sum_best += Best[o]
        row = [o,v,int(value/nForms),Best[o]]
        specTable.append(row)
      # print((sum_best,nSolved))
      # print(f"VBS: {VBS['solved']} , {int(VBS['par2']/nForms)}")

    # do_print not used for AAAI submission
    # printing instead happens in main function
    if do_print:
      st = ""
      st_h = ""
      for o,v in solved.items():
        st += "{:<8} ".format(v)
        st_h += "{:<8} ".format(o)
      print(st_h)
      print(st)
      st = ""
      for key,value in Par2.items():
        st += "{:<8} ".format(round(value/nForms,2))
      print(st)

    if do_print:
      print(f"\nTotal solved formulas {nSolved}")
      print(f"Total processed formulas {nForms}")
      print((chosen_families))

    if realFamily:
      global selected_families
      selected_families = []
      for f,c in chosen_families.items():
        if c >= 4:
          selected_families.append(f)

    # return collected data to be printed in calling function
    return solve_times, scatters, specTable


def process_data (print_ts, cactus, sat,diff_cut, pre_cut, scatter, realFamily, preproc, tables):

  configs = []

  # Parse CSV data from files
  benchmarks, solve_stats_kmtotalizer, _ = get_csv_data_random ("kmtotalizer-paper.csv")
  _, solve_stats_all, configs_all = get_csv_data_random ("all-encodings-paper.csv")

  # Parse information about maxSAT formulas to get #hard clauses for preproc plot
  formula_data = get_formula_data ("maxSAT_formula_info.csv")

  solve_times = {}
  scatter_times = {}

  # print preprocessing times for orderings listed below
  if preproc:
    print("\n\nPlot with preprocessing times:\n")
    e_type = "kmtotalizer"
    vars = ["PAMO","Proximity", "Natural","Occurrence","Graph"]

    order_times = {}
    for v in vars:
      order_times[v] = []
      for b in benchmarks: 
        fix_b = ""
        if "-unsat" == b[-6:]: fix_b = b[:-6]
        elif "-sat" in b[-4:]: fix_b = b[:-4]

        order_times[v].append((int(formula_data[fix_b]["HardClauses"]), get_pret (solve_stats_kmtotalizer,e_type,b,v)))

    print_preprocessing_times_cactus (order_times,"Preprocessing time","Formula size (clauses)","Time (s)")

  if tables:
    # print table for all encoding types
    print("\n\nTable for all encoding types:\n")
    specialTexTable = False
    no_print = False
    texTable = True
    vars = [ "Natural","PAMO+Occur", "Proximity","Occurrence","Random"]
    st = "        "
    for v in vars:
      if v == "Random":
        st += "{:<8} & {:<8} & ".format("BestRan", "WorstRan")
      else:
        st += "{:<8} & ".format(v)
    print(st[:-2]+ "\\\\")
    for c in configs_all:
      solve_times[c], scatter_times[c], _ = get_solve_data(solve_stats_all,c,vars,benchmarks,diff_cut, pre_cut, no_print,print_ts, sat, formula_data, realFamily,texTable, specialTexTable)


    # print table for kmtotalizer and all ordering types
    print("\n\nTable for all kmtotalizer with all ordering types:\n")
    vars = ["PAMO+Occur","Natural+PAMO","PAMO","Proximity","Graph", "Natural","Occurrence","Random"]

    specialTexTable = True
    no_print = False
    texTable = False
    c = "kmtotalizer"
    print("Configuration & Solve SAT & Solve UNSAT & Par2 SAT & Par2 UNSAT")
    solve_times[c], scatter_times[c], specTableSat = get_solve_data(solve_stats_kmtotalizer,c,vars,benchmarks,diff_cut, pre_cut, no_print,print_ts, 1, formula_data, realFamily,texTable, specialTexTable)
    solve_times[c], scatter_times[c], specTableUnsat = get_solve_data(solve_stats_kmtotalizer,c,vars,benchmarks,diff_cut, pre_cut, no_print,print_ts, 2, formula_data, realFamily,texTable, specialTexTable)

    for i in range(len(specTableSat)):
      print(f"{specTableSat[i][0]} & {specTableSat[i][1]} & {specTableUnsat[i][1]} & {specTableSat[i][2]} & {specTableUnsat[i][2]}   \\\\")

  # Print cactus for kmtotalizer with all orderings
  if cactus:
    vars = ["PAMO+Occur","Natural+PAMO","PAMO","Proximity","Graph", "Natural","Occurrence","Random"]
    print("\n\nCactus plot for all kmtotalizer with all ordering types:\n")
    specialTexTable = False
    no_print = False
    texTable = False
    specialTexTable = True
    c = "kmtotalizer"
    solve_times[c], scatter_times[c], specTableSat = get_solve_data(solve_stats_kmtotalizer,c,vars,benchmarks,diff_cut, pre_cut, no_print,print_ts, 0, formula_data, realFamily,texTable, specialTexTable)
    print_cactus (solve_times[c],c,sat)

  

    
#######################################################################################
# MAIN FUNCTION
#######################################################################################
  
def run(name, args):
    
    print_ts = False
    cactus = False
    sat = -1
    pre_cut = -1
    diff_cut = 0
    scatter = False
    realFamily = False
    preproc = False
    tables = False

    optlist, args = getopt.getopt(args, "pfztlcd::s:k:")
    for (opt, val) in optlist:
      if opt == '-c':
        cactus = True
      elif opt == '-p':
        preproc = True
      elif opt == '-d':
        diff_cut = int(val)
      elif opt == '-k':
        pre_cut = int(val)
      elif opt == '-l':
       print_ts = True
      elif opt == '-t':
       tables = True
      elif opt == '-s':
       sat = int(val)
      elif opt == '-z':
       scatter = True
      elif opt == '-f':
       realFamily = True
        
        
    process_data(print_ts, cactus, sat, diff_cut, pre_cut, scatter, realFamily, preproc, tables)
        

if __name__ == "__main__":
    run(sys.argv[0], sys.argv[1:])
