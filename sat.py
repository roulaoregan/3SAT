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

'''
class that handles the recursive DPLL procedure
handles backtracking too
'''
class SAT(object):
    def __init__(self, logger=None, clauses=None, symbols=None, model=None):

        self.log = logger
        self.clauses = clauses
        self.symbols = symbols
        self.model = {}
        
        if model is not None:
            self.model = model

        self._UNIT_ = 1


    def get_assignment(self):
        return self.symbols.assigned_stack

    '''
    :param: sentence tuple in the form of (clauses, symbols, model)
    :ptype: tuple 
    :return: whether sentence in CNF is SAT
    :rtype boolean
    '''
    def dpll_satisfiable(self):
    	
        return self._dpll(self.clauses, self.symbols, self.model)

    '''
    :param: model, list of dictionaries
       	e.g. [{'clause':[4, 3, 22], 'original':[4, 3, 22]},{'clause': [7, 2, 3], 'original': [7, 2, 3}]
                if clause is all assigned to "TRUE" change dictionary to: {'clause': True, 'original': [7, 2, 3]}
                if clause is False: {'clause':[], 'original': [7, 2, 3]}
                if there is a conflict:{'clause':[], 'original': [9,5,3], 'conflict': [-9]}
    :param: symbols, set set([7, 15, 8, 4,12]) of type Literal Class
    :param: clauses --> remains unchanged!!! list of lists: [[7,2,3],[6,-14,2],[7,15,-3]]
    :return: whether CNF is SAT or UNSAT
    :rtype: boolean
    '''
    def _dpll(self, clauses, symbols, model={}):

        #If every clause in clauses is True in model return True
        #
        if model:
            self.log.debug("Check if every clause is True")
            clause_values = [x for x in model if 'clause' in x and x['clause'] == True]
            self.log.debug("check if every clause in clauses is True and in model, clause_values: %s"%clause_values)
            if len(clause_values) == len(model):
                return True

        # If some clause is clauses is False in model return False
        #
        if model:
            empty_clause = [x for x in model if not x.get('clause', None)]
            self.log.debug("check if some clause is False in model, empty_clause: %s"%empty_clause)

            # Check for conflicts
            #
            empty_clause = [cl['conflict'].append(P) for cl in model if not cl['clause']]
            if empty_clause:
                print "found empty_clause"
                self.log.debug("found empty clause with %s assigning conflict: "%(P, empty_clause))

            unit_clauses = [ clause[-1] for clause in clauses if len(clause) == self._UNIT_]
            conflict = [ literal for literal in unit_clauses  if -literal in unit_clauses]
            if conflict:
                for cl in model:
                    if not isinstance(cl['clause'], bool):
                        if (P or -P) in cl['clause'] and len(cl['clause']) == self._UNIT_:
                            if P in cl['clause']:
                                cl['conflict'].append(P)
                            else:
                                cl['conflict'].append(-P)
            self.log.debug("found conflict assigning literal: %s"%P)
            if empty_clause:
                self.log.debug("found empty clause: %s"%empty_clause)

                # Call Backtrack
                #
                #self.__backtrack(clauses, symbols, model, q)
                ["found empty clause, original clause: %s conflict with literal: %s"%(x['original'], x['conflict']) for x in empty_clause]
                return False

        ##########################
        # Heuristic 1: Pure Symbol
        #	
        P = self._find_pure_symbol(clauses, symbols, model)
        self.log.debug("calling heuristic - pure symbol")

        if P is not None:
            self.log.debug("removing pure literal P: %s"%P)
            self.log.debug("forward chaining calling unit_prop")
            symbols.remove(P)
            clauses, model = self._unit_propagation(clauses, model, P)
            #
            self.log.debug( "revised symbols.literals %s"%symbols.literals)
            return self._dpll(clauses, symbols, model)

        ##########################
        # Heuristic 2: Unit Clause and Unit Propagation
        #
        P = self._find_unit_clause(clauses, model)
        self.log.debug("calling heuristic unit clause, P: %s" % P)
        if P is not None:            
            self.log.debug("removing symbols in P")
            symbols.remove(P)
            self.log.debug("calling forward chaining, clauses: %s\n model: %s\n symbols: %s"%(clauses, symbols,model))
            clauses, model = self._unit_propagation(clauses, model, P)  
            return self._dpll(clauses, symbols, model)

        ##########################
        # Rest
        #
        P = self._most_watched(clauses,symbols)
        self.log.debug("calling most watched fn, returns P: %s"%P)
        if P is not None:
            self.log.debug("removing %s from symbols and calling _unit_propagation fn"%P)
            symbols.remove(P)
            clauses, model = self._unit_propagation(clauses, model, P)

        return self._dpll(clauses, symbols, model)

    '''
    :return: first pure literal seen
    :rtype: integer
    '''
    def _find_pure_symbol(self, clauses, symbols, model):

        pure = None
        flatten = [ sublist for x in clauses for sublist in x]
        unique = [ literal for literal in flatten if -literal not in flatten]

        if unique:
            self.log.debug("found unique symbol unique list: %s returning last one found: %s"%(unique,unique[-1]))
            pure = unique[-1]
        self.log.debug("returning pure literal: %s"%pure)
        return pure

    '''
    :return: literal in first found unit clause
    :rtype: integer
    '''
    def _find_unit_clause(self, clauses, model):
        found_literal = None
        for cl in model:
            if not isinstance(cl['clause'],bool):
                if len(cl['clause']) == self._UNIT_:
                    literal = cl['clause'][-1]
                    self.log.debug("found unit clause: %s"%cl['clause'])
                    found_literal = literal 
                    #double negation if (-C) then C must be False to get --C ==> C
                     # if literal is (C) then C must be True
                    #(clauses, model) = self._unit_propagation(clauses, model, literal)

        return found_literal

    '''
    Get the most frequently seen literal
    :return: literal
    :rtype: integer
    '''
    def _most_watched(self, clauses, symbols):

        most_watched = None

        if clauses:
            if symbols:
                cl_symbols = [ symbol for clause in clauses for symbol in clause if not isinstance(symbol,bool)]
                count = Counter(cl_symbols)
                most_watched = count.most_common(1)[0][0]
                self.log.debug("most watched literal: %s"%most_watched)

        return most_watched
	
    '''
    Conflict directed backjumping
    re-assign q and see if there are any conflicts
    :return: whether conflict was resolved
    :rtype: boolean
    '''
    def _cbj(self, clauses, symbols, model, q):

        resolved = True

        if symbols.unresolved(q):
            resolved = False

        elif symbols.assign(q):            
            (clauses, model, q) = self._simplify(clauses, model, q)
            empty_clause = [x for x in model if not x.get('clause', None)]
            
            if empty_clause:
                resolved = False

        return resolved

    '''
    undo assignment of literal q and restores previous state
    '''
    def _undo(self, clauses, symbols, model, q):
        #unassign literal q in symbols
        symbols.unassign(q)
        #insert q back in the model
        [x['clause'].append(q) if q in x['original'] else (x['clause'].append(-q) if -q in x['original'] else x) for x in model]


    '''
    Called when a conflict occurs
    Undoes the latest assignment and re-assigns literal with its negation
    e.g.: A=False caused a conflict, reassign to A=True and visa versa
    :param: clauses
    :param: symbols
    :param: model
    :param: q literal to be re-assigned
    :return: whether re assignment is possible
    :rtype: boolean
    '''
    def _backtrack(self, clauses, symbols, model, q):

        self._undo(clauses, symbols, model, q)
        is_assigned = self._cbj(clauses, symbols, model, -q)
        if not is_assigned:
            if not symbols.empty():
                previous_q = symbols.pop()
                return self._backtrack(clauses, symbols, model, previous_q)
            else:
                is_assigned = False

        return is_assigned

    '''
    check if clause is satisfiable with literal assignment
    :return: whether clause is SAT with literal assignment
    :rtype: boolean
    '''
    def _satisfied(self, clause, assignment):
        
        sat = None
        if len(clause) == self._UNIT_:
            if ((assignment or -assignment) < 0 and clause[-1] > 0) or ((assignment or -assignment) > 0 and clause[-1] < 0):   
                sat = False
            elif ((assignment or -assignment) < 0 and clause[-1] < 0) or (assignment or -assignment) > 0 and clause[-1] > 0:
                #double negative is True ==> positive is sat
                sat = True

        return sat

    '''
    param: clauses
    param: P assignment of literal
    :return: updated clauses and model
    :rtype: tuple
    '''
    def _unit_propagation(self, clauses, model, P, conflict=False):

        pp = pprint.PrettyPrinter(indent=4)
        
        pp.pprint(clauses)
        pp.pprint("-->>>> assigning literal: %s"%P)
        self.symbols.assign(P)
	
	remove_clauses = []
	
        for c in clauses:
            if (P in c) or (-P in c):
                if len(c) == self._UNIT_:
                    if self._satisfied(c,P):
                        remove_clauses.append(c)
                    else:
                        c[:] = []
                else:
                    if (P or -P) > 0:
                        negative_literal = [ x for x in c if x < 0]
                        if not negative_literal:
                            remove_clauses.append(c)
                        else:
                            if P in c:
                                c.remove(P)
                            elif -P in c:
                                c.remove(-P)
                    if (P or -P) < 0: 
                        if P in c:                        
                            c.remove(P)
                        elif -P in c and -P > 0:
                            negative_literal = [x for x in c if x < 0]
                            if not negative_literal:
                            	remove_clauses.append(c)
                            	
        [clauses.remove(x) for x in remove_clauses]
        
        self.log.debug("update model")  
        for cl in model:
            
            if not isinstance(cl['clause'], bool):
                if (P or -P) in cl['clause']:
                    if len(cl['clause']) == self._UNIT_:
                        if self._satisfied(cl['clause'], P):
                            cl['clause'] = True
                        else:
                            cl['clause'] = []
                    else:
                        if (P or -P) < 0:
                            cl['clause'].remove((P or -P))
                        else:
                            cl['clause'] = True
        

        self.log.debug(pp.pprint(clauses))
        self.log.debug(pp.pprint(model))

        return (clauses, model)


