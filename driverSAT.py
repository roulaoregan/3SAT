'''
 copyright 2014
 author: Spiridoula O'Regan
 email: roula.oregan@gmail.com
 github user: roulaoregan
'''
import logger
import math
import os
import random
import re
import sys

from collections import Counter
from optparse import OptionParser
from literals import Literals
from dimacs_parser import DimacsParser
from sat import SAT

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
	arg_handler.add_option('d', '--debug', type='string', help='debug and log info and errors')    
	#arg_handler.add_option('p', '--printtostdout', action='store_true', default=False, help='Print all log message to stdout')
	options, args = arg_handler.parse_args()

	#Parse Dimacs file
	parse_file = DimacsParser(argv[0])
	parse_file.parse()
	(clauses, literals, model) = parse_file.sentences()
	symbols = Literals(literals)
	
	logger.info("parsed Dimacs file")
	logger.info("clauses: %s"%(clauses))
	logger.info("created Literals() and add symbols: %s"%(symbols))
	logger.info("model: %s"%(model))
	
	#call SAT Solver
	solver = SAT(clauses, symbols, model)
	satisfiable = solver.satisfiable(clauses, symbols, model)


if __name__ = "__main__":
	main(sys.argv[1:])

