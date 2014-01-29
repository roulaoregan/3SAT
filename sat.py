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


class SAT(object):
    def __init__(self, logger, clauses=None, symbols=None, model=None):

        self.logger = logger
        self.clauses = clauses
        self.symbols = symbols
        self.model = {}
        
        if model is not None:
            self.model.update(model)

        self._UNIT_ = 1


    '''
    :param: sentence tuple in the form of (clauses, symbols, model)
    :ptype: tuple 
    @returns whether sentence in CNF is SAT
    @rtype boolean
    '''
    def dpll_satisfiable():

            return self._dpll(self.clauses, self.symbols, self.model)

    '''
    :param: model, list of dictionaries
       	e.g. [{'clause':[4, 3, 22], 'original':[4, 3, 22]},{'clause': [7, 2, 3], 'original': [7, 2, 3}]
        if clause is all assigned to "TRUE" change dictionary to:
                {'clause': True, 'original': [7, 2, 3]}
        if clause is False:
                {'clause':[], 'original': [7, 2, 3]}
        if there is a conflict:
                {'clause':[], 'original': [9,5,3], 'conflict': [-9]}
    :param: symbols, set set([7, 15, 8, 4,12])
    :param: clauses --> remains unchanged!!! list of lists: [[7,2,3],[6,-14,2],[7,15,-3]]
    '''
    def _dpll(clauses, symbols, model={}):

        #if every clause in clauses is True in model return True
        if model:
                clause_values = [x for x in model if 'clause' in x and x['clause'] == True]
                self.logger.debug("check if every clause in clauses is True and in model, clause_values: %s"%clause_values)
                if len(clause_values) == len(model):
                        return True

        #if some clause is clauses is False in model return False
        if model:
            empty_clause = [x for x in model if not x.get('clause', None)]
            self.logger.debug("check if some cluse is False in model, empty_clause: %s"%empty_clause)

            if empty_clause:
                self.logger.debug("found empty clause: %s"%empty_clause)
                #call self._backtrack()
                ["found empty clause, original clause: %s conflict with literal: %s"%(x['original'], x['conflict']) for x in empty_clause]
                return False

        #Heuristic 1: Pure Symbol		
        P = self._find_pure_symbol(clauses, symbols, model)
        self.logger("calling heuristic - pure symbol")

        if P is not None:
            self.logger.debug("removing pure literal P: %s"%P)
            self.logger.debug("forward chaining calling unit_prop")
            symbols.remove(P)
            self.unit_propagation(model,P)

            return _dpll(clauses, symbols, model)

        #Heuristic 2: Unit Clause and Unit Propagation
        P = self._find_unit_clause(clauses, model)
        self.logger.debug("calling heuristic unit clause, P: %s" % P)
        if P is not None:
            [symbols.remove(symbol) for symbol in P]
            (clauses, model, assignment) = self._unit_propagation(clauses, model, P)
            symbols.remove(assignment)
            self.logger.debug("removing symbols in P")
            self.logger.debug("assignment: %s" % assignment)
            self.logger.debug("calling forward chaining, clauses: %s\n model: %s\n symbols: %s"%(clauses, symbols,model))
            return self._dpll(clauses, symbols, model)

        #Rest
        P = self._most_watched(clauses,symbols)
        self.logger.debug("rest, calling most watched fn, returns P: %s"%P)
        if P is not None:
            self.logger.debug("removing %s from symbols and calling update_model fn"%P)
            symbols.remove(P)
            self._update_model(model, P)

        return self._dpll(clauses, symbols, model)

    '''
    :param: clauses
    :param: symbols
    :param: model
    :return first pure literal seen
    '''
    def _find_pure_symbol(clauses, symbols, model):
        pure = None
        flatten = [ sublist for x in clauses for sublist in x]
        unique = [ literal for literal in flatten if -literal not in flatten]
            
        if unique:
            self.logger.debug("found unique symbol unique list: %s returning last one found: %s"%(unique,unique[-1]))
            pure = unique[-1]

        return pure

    '''
    :param: clauses
    :param: model
    '''
    def _find_unit_clause(clauses, model):
        found_literals = []
        for cl in model:
                if len(cl['clause']) == self._UNIT_:
                        literal = cl['clause'][-1]
                        found_literals.append(literal)
                        self.logger.debug("found unit clause: %s"%cl['clause'])
                        #double negation if (-C) then C must be False to get --C ==> C
                        # if literal is (C) then C must be True
                        (clauses, model, assignment) = self._unit_propagation(clauses, model, literal)


        return found_literals

    '''
    Get the most frequently seen literal
    :param: clauses
    :param: symbols
    :return literal
    :rtype int
    '''
    def _most_watched(clauses, symbols):

        most_watched = None
        if symbols:
                #count = dict(zip(symbols, [0 for x in range(len(symbols))]))
                cl_symbols = [ symbol for x in clauses for symbol in x['clause']]
                #most_watched = sorted(count.items(), key=lambda (k,v): v, reverse=True)[0]
                count = Counter(cl_symbols)
                most_watched = count.most_common(1)[0][0]

        return most_watched
	
    '''
    Conflict directed backjumping
    re-assign q and see if there are any conflicts
    '''
    def _cbj(clauses, symbols, model, q):

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
    :param: clauses
    :param: symbols
    :param: model
    :param: q - literal to be un-assigned
    '''
    def _undo(clauses, symbols, model, q):
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
    '''
    def _backtrack(clauses, symbols, model, q):

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
    check if clause is satisfiable
    '''
    def _satisfied(clause, assignment):
        sat = False
        if (assignment > 0 and clause[-1] > 0) or (assignment < 0 and clause[-1] < 0):
            sat = True

        return sat

    '''
    :param: model
    :param: P a literal that is assigned either True or False
    '''
    def _update_model(model, P):
        for cl in model:
        #case 1: P is True and in the clause --> we can assign clause as True
            if P > 0 and P in cl['clause']:
                cl['clause'] = True
                    #case 2: P is True and the negation of P is in the clause
            elif P > 0 and ((P *-1) in cl['clause']):
                    cl['clause'].remove(P)
            #case 3: P is False and in the clause --> remove P and keep the other unassigned literals in the clause
            # [-A v -B v -C] and A is assigned False then -(-A) <==> A
            elif P < 0 and P in cl['clause']:
                    cl['clause'] = True
            #case 4: P is False and the negation is in the clause
            # [A v -B v -C] and A is assigned False -A, then remove A and keep the other unassigned literals in the clause
            elif P < 0 and ((P*-1) in cl['clause']:
                    cl['clause'].remove(P)


        #check for an clauses that are empty --> if so assign P as a conflict literal in that clause
        #e.g. P is True and is -9 {'clause':[], 'original':[-9,-10,-41],'conflict':P}
        for cl in model:
            if not cl['clause']:
                self.logger.debug("found empty clause with %s assigning conflict: %s"%(P, cl['original']))
                cl['conflict'] = P


    '''
    Forward Chaining
    '''
    def _unit_propagation(clauses, model, assignment):
        for cl in clauses:
            if len(cl['clause']) == 1:
                if cl['clause'] == assignment or cl['clause'] == -assignment:
                    if _satisfied(cl['clause'], assignment):
                        clauses, model, assignment = _simplify(clauses, model, assignment)
                        return self._unit_propagation(clauses, model, assignment)
                    else:
                        conflict = assignment
                        if cl['clause'] == -assignment:
                            cl['clause'].remove(-assignment)
                            conflict = -assignment
                        else:
                            cl['clause'].remove(assignment)
                            cl['conflict'].append(conflict)

        return (clauses, model, assignment)

    '''
    param: clauses
    param: P assignment of literal
    '''
    def _simplify(clauses, model, P):
        #find clauses to remove
        remove = [i for i in clauses if (P in i and P < 0) or (P in i and P > 0)]

        #remove clauses assigned as True  for both model and clauses
        [clauses.remove(clause) for clause in remove]
        for cl in model:
            if cl['clause'] in remove:
                cl['clause'] = True

        #remove literal from clauses and model
        [ i.remove(-P) for i in clauses if (-P in i and a > 0) or (-P in i and P < 0)]
        [ cl['clause'].remove(-p) for cl in model if (-p in cl['clause'] and p > 0) or (-p in cl['clause'] and p < 0)]

        return (clauses, model, P)







