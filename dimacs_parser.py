'''
 copyright 2014
 author: Spiridoula O'Regan
 email: roula.oregan@gmail.com
 github user: roulaoregan
'''
import copy
import logging
import math
import os
import random
import re
import sys

from collections import Counter
from optparse import OptionParser
from literals import Literals

'''
Parse the Dimacs file which is in Conjunctive Normal Form

'''
class DimacsParser(object):
        def __init__(self, filepath, log):
                self.file_path = filepath
                self.clauses = []
                self.symbols = Literals()
                self.model = {}
                self.log = log
                print "self.log: %s"%self.log

        def parse(self):
                
                symbol_list = []
                self.log.debug("******************************************************")
                print "self.file_path: %s"%self.file_path
                print "type: %s"%type(self.file_path)
                print os.path.isfile(str(self.file_path))
                if os.path.isfile(str(self.file_path)):
                        with open(self.file_path) as data:                                
                                data_lines = (line.rstrip("\r\n") for line in data)
                                self.log.debug("data_lines: %s"%data_lines)
                                for line in data_lines:
                                        match_comment = re.match("^p", line)                                        
                                        match_clause = re.match("^[0-9]|^\-", line)
                                        split_lines = line.rsplit(" ")

                                        if match_comment:
                                                print "number of clauses: %s and number of variables: %s" % (split_lines[-1], split_lines[-2])
                                                self.log.debug("number of clauses: %s and number of variables: %s" % (split_lines[-1], split_lines[-2]))
                                        
                                        if match_clause:                                                
                                                clause = [int(split_lines[x]) for x in range(3)]
                                                self.log.debug("adding clause: %s"%clause)
                                                self.clauses.append(clause)
                                                symbol_list.extend(clause)    

                        [self.symbols.add(symbol) for symbol in symbol_list]


        def sentences(self):

                deep_copy = copy.deepcopy(self.clauses)
                self.model = [{'clause':cl, 'original':copy.deepcopy(cl), 'conflict': []} for cl in deep_copy]
                self.log.debug("******************************************************")
                self.log.debug("clauses: %s"%self.clauses)
                self.log.debug("symbols: %s"%self.symbols.literals)
                self.log.debug("model: %s"%self.model)
                self.log.debug("******************************************************")
                
                return (self.clauses, self.symbols, self.model)

