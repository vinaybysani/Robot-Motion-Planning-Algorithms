The following algorithms have been implemented:

* Vertical Cell Decomposition (VCD)
* Probabilistic Roadmap (PRM)
* Rapidly-exploring Random Trees (RRT)
* Shortest Path Roadmap (SPRM) (_Work in Progress_) (untill adjacency graph)

Usage:
```
python main.py [-h] [-in IN] [-algo ALGO] [-out OUT] [-n N] [-k K]
               [-plot PLOT]

arguments:
  -h, --help  show this help message and exit
  -in IN      input file (default: input.txt)
  -algo ALGO  algorithm to implement: vcd, prm, rrt, [sprm] (default: prm)
  -out OUT    output file (default: output.txt)
  -n N        number of samples for PRM/RRT (default: 1000)
  -k K        number of nearest neighbors for PRM (default: 5)
  -plot PLOT  plot final output? [y/n] (default: y)
```