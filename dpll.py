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


def main(argv):
        logging.basicConfig(filename='dpll_log.log', level=logging.INFO)

        arg_handler = OptionParser("DPLL 3 SAT Solver")
        arg_handler.add_option('d', '--debug', type='string', help='debug levels Critical (3), Error (2), Warning (1), info (0), debug (-1), default='CRITICAL')    
        arg_handler.add_option('p', '--printtostdout', action='store_true', default=False, help='Print all log message to stdout')
        options, args = arg_handler.parse_args()

        #Parse DCIMACS file
        parse_file = DimacsParser(argv[0])
        parse_file.parse()
        (clauses, symbols, model) = parse_file.sentences()

        satisfiable = dpll(clauses, symbols, model)


if __name__ = "__main__":
        main(sys.argv[1:])
