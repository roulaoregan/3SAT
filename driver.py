'''
 copyright 2014
 author: Spiridoula O'Regan
 email: roula.oregan@gmail.com
 github user: roulaoregan
'''
import logging
import math
import os
import pprint
import random
import re
import sys

from collections import Counter
from optparse import OptionParser
from dimacs_parser import DimacsParser
from sat import SAT
from exception_file_handling import FileInputError


def set_logger(file_path, verbose=False):
	logger = None

	if file_path and os.path.exists(file_path):
		logger = logging.getLogger("dpll_log")
		logger.setLevel(logging.DEBUG)
		#save log in current working directory
		fh = logging.FileHandler(os.path.join(os.getcwd(), "dpll.log"))
		fh.setLevel(logging.DEBUG)
			
		ch = logging.StreamHandler()
		if verbose:
			ch.setLevel(logging.DEBUG)
		else:
			ch.setLevel(logging.INFO)

		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)
		
		logger.addHandler(fh)
		logger.addHandler(ch)
		
		return logger
	else:
		raise FileInputError("No file path or file doesn't exist")
	

def main(argv):
	pp = pprint.PrettyPrinter(indent=4)	

	arg_handler = OptionParser("****************  DPLL 3 SAT Solver  ****************")
	arg_handler.add_option('-f', '--file', type='string', help='Dimacs file in CNF, Format -->> in cwd: file.dimacs else: /path/to/file/dimacs_file.dimacs')
	arg_handler.add_option("-v", "--verbose", action="store_true", dest="verbose")
	options, args = arg_handler.parse_args()
	option_dict = vars(options)
	
	file_name = None
	if arg_handler.get_option("-f"):
		file_name = option_dict['file']	
	else:
		raise FileInputError("Need to provide a Dimacs file")

	verbose = False
	if arg_handler.get_option("-v"):
		verbose = True

	logger = set_logger(file_name, verbose=verbose)
	
	####################
	# Parse Dimacs file
	#
	parse_file = DimacsParser(file_name,logger)
	parse_file.parse()
	(clauses, symbols, model) = parse_file.sentences()
	logger.debug("parsed Dimacs file")
	logger.debug("clauses: %s"%(clauses))
	logger.debug("created Literals() and add symbols: %s"%(symbols))
	logger.debug("model: %s"%(model))

	####################
	# SAT Solver
	#
	solver = SAT(logger=logger, clauses=clauses, symbols=symbols, model=model)
	logger.info("calling SAT solver")
	satisfiable = solver.dpll_satisfiable()
	
	####################
	# Result
	#
	if satisfiable:
		logger.info("*******************************")
		logger.info("CNF Sentence is Satisfiable")
		logger.info("*******************************")
		assignment = solver.get_assignment()
		pp.pprint("Literal assignment: %s"%assignment)
	else:
		logger.info("*******************************")
		logger.info("CNF Sentence is Unsatisfiable")
		logger.info("*******************************")


if __name__ == "__main__":
	main(sys.argv[1:])

