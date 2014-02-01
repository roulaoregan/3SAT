'''
 copyright 2014
 author: Spiridoula O'Regan
 email: roula.oregan@gmail.com
 github user: roulaoregan
'''
import logging
import math
import os
import random
import re
import sys

from collections import Counter
from optparse import OptionParser
from dimacs_parser import DimacsParser
from sat import SAT

'''
Handles file input errors
'''
class FileInputError(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)

def main(argv):
	logger = logging.getLogger('dpll_log')
	logger.setLevel(logging.DEBUG)

	fh = logging.FileHandler("dpll.log")
	fh.setLevel(logging.DEBUG)
	
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)

	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	logger.addHandler(fh)
	logger.addHandler(ch)

	arg_handler = OptionParser("DPLL 3 SAT Solver")
	#arg_handler.add_option('d', '--debug', type='string', help='debug and log info and errors')    
	#arg_handler.add_option('p', '--printtostdout', action='store_true', default=False, help='Print all log message to stdout')
	#options, args = arg_handler.parse_args()

	#Parse Dimacs file
	parse_file = DimacsParser(argv[0])
	parse_file.parse()
	(clauses, symbols, model) = parse_file.sentences()
	logger.debug("parsed Dimacs file")
	logger.debug("clauses: %s"%(clauses))
	logger.debug("created Literals() and add symbols: %s"%(symbols))
	logger.debug("model: %s"%(model))
	#call SAT Solver
	solver = SAT(logger=logger, clauses=clauses, symbols=symbols, model=model)
	logger.debug("calling SAT solver")
	satisfiable = solver.satisfiable()


if __name__ == "__main__":
	main(sys.argv[1:])

