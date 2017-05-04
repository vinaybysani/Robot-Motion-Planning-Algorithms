# CS598-HW2
The following algorithms have been implemented:

* Vertical Cell Decomposition (VCD)
* Probabilistic Roadmap (PRM)
* Rapidly-exploring Random Trees (RRT)
* Shortest Path Roadmap (SPRM) (_Work in Progress_)

Usage:
```
python main.py [-h] [-in IN] [-algo ALGO] [-out OUT] [-n N] [-k K]
               [-plot PLOT]

arguments:
  -h, --help  show help message and exit
  -in IN      input file
  -algo ALGO  algorithm to implement: vcd, prm, rrt, [sprm]
  -out OUT    output file
  -n N        number of samples for PRM/RRT
  -k K        number of nearest neighbors for PRM
  -plot PLOT  plot final output? [y/n]
```