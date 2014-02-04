3SAT
====

(1) PROJECT:
This is a Python implementation of Davis–Putnam–Logemann–Loveland (DPLL) algorithm for solving CNF-SAT (Conjunctive Normal Form satisfiability) problems.
 
Current version is single-threaded implementation.


How to Run at Command line:
Reads and parses Dimacs files
Argument Handlers:
$ python driverSAT.py -h
Usage: ****************  DPLL 3 SAT Solver  ****************

Options:
  -h, --help            show this help message and exit
  -f FILE, --file=FILE  Dimacs file in CNF, Format -->> in cwd: file.dimacs
                        else: /path/to/file/dimacs_file.dimacs
  -v, --verbose  

Todo:
Backtrack is currently set to "OFF" until all unit tests are complete and successful.

License:

(LGPL version 3)

Copyright (c) 2010 Spiridoula O'Regan

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this program. If not, see http://www.gnu.org/licenses/.

