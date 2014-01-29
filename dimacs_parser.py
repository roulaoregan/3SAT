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


'''
Parse the Dimacs file which is in Conjunctive Normal Form
TODO: change "print" comments to logger!

'''
class DimacsParser(object):
        def __init__(self,filepath):
                self.file_path = filepath
                self.clauses = []
                self.symbols = Literals()
                self.model

        def parse():
                symbol_list = []
                if filepath:
                        with open(self.filepath) as data:
                                data_lines = (line.rstrip("\r\n") for line in data)
                                for line in data_lines:
                                        match_comment = re.match("^p", line)
                                        match_clause = re.match("^[0-9]|^\-", line)
                                        split_lines = line.rsplit(" ")

                                        if match_clause:
                                                print "number of clauses: %s and number of variables: %s" % (split_lines[-1], split_lines[-2])
                                        if match_clause:
                                                self.clauses.append(int([split_lines[0]]) + int([split_lines[1]]) + int([split_lines[2]]))
                                                symbol_list.extend(self.clauses[-1])
                                                print "adding clause: %s"%self.clauses[-1]

                        [self.symbol.add(symbol) for symbol in symbol_list]
                else:
                        raise FileInputException("no file path provided")

        def sentences():
                self.model = [{'clause':cl, 'original':cl, 'conflict' = []} for cl in self.clauses]
                return (self.clauses, self.symbols, self.model)
