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


class SAT(object):
    def __init__(self, logger=None, clauses=None, symbols=None, model=None):

        self.log = logger
        print "self.log: %s"%self.log
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
    @returns whether sentence in CNF is SAT
    @rtype boolean
    '''
    def dpll_satisfiable(self):
        print "inside dpll_satisfiable function"
        result = self._dpll(self.clauses, self.symbols, self.model)
        print "result: %s"%result
        return result

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
    def _dpll(self, clauses, symbols, model={}):
        self.log.debug("--->>>>>>> ENTER DPLL")
        self.log.debug("symbols: %s"%symbols.literals)

        #if every clause in clauses is True in model return True
        if model:
            self.log.debug("CHECK IF EVERY CLAUSE IS TRUE!!!")
            clause_values = [x for x in model if 'clause' in x and x['clause'] == True]
            self.log.debug("!!!!!!!!!!!!!!check if every clause in clauses is True and in model, clause_values: %s"%clause_values)
            self.log.debug("!!!!!!!!!!!!!!len of model: %s len of clause_values: %s"%(len(model), len(clause_values)))
            if len(clause_values) == len(model):
                return True

        #if some clause is clauses is False in model return False
        if model:
            empty_clause = [x for x in model if not x.get('clause', None)]
            self.log.debug("check if some cluse is False in model, empty_clause: %s"%empty_clause)

            if empty_clause:
                self.log.debug("found empty clause: %s"%empty_clause)
                #call self._backtrack()
                ["found empty clause, original clause: %s conflict with literal: %s"%(x['original'], x['conflict']) for x in empty_clause]
                return False

        #Heuristic 1: Pure Symbol		
        P = self._find_pure_symbol(clauses, symbols, model)
        self.log.debug("calling heuristic - pure symbol")

        if P is not None:
            self.log.debug("removing pure literal P: %s"%P)
            self.log.debug("forward chaining calling unit_prop")
            symbols.remove(P)
            clauses, model = self._unit_propagation(clauses, model, P) #clauses, model, assignment
            #
            self.log.debug( "revised symbols.literals %s"%symbols.literals)
            self.log.debug("RECURSIVE CALL TO DPLL (inside pure symbol if statement")
            return self._dpll(clauses, symbols, model)

        #Heuristic 2: Unit Clause and Unit Propagation
        P = self._find_unit_clause(clauses, model)
        self.log.debug("calling heuristic unit clause, P: %s" % P)
        if P is not None:            
            self.log.debug("removing symbols in P")
            symbols.remove(P)
            self.log.debug("calling forward chaining, clauses: %s\n model: %s\n symbols: %s"%(clauses, symbols,model))
            clauses, model = self._unit_propagation(clauses, model, P)           
            self.log.debug("RECURSIVE CALL: calling dpll function")
            return self._dpll(clauses, symbols, model)

        #Rest
        P = self._most_watched(clauses,symbols)
        self.log.debug("!!!!!!!!!!!!REST part: calling most watched fn, returns P: %s"%P)
        if P is not None:
            self.log.debug("removing %s from symbols and calling _unit_propagation fn"%P)
            symbols.remove(P)
            clauses, model = self._unit_propagation(clauses, model, P)

        self.log.debug("EXITING DPLL")

        return self._dpll(clauses, symbols, model)

    '''
    :param: clauses
    :param: symbols
    :param: model
    :return first pure literal seen
    '''
    def _find_pure_symbol(self, clauses, symbols, model):
        self.log.debug("-->>>> inside _find_pure_symbol function")
        self.log.debug("-->>>> symbols: %s"%symbols.literals)
        pure = None
        flatten = [ sublist for x in clauses for sublist in x]
        unique = [ literal for literal in flatten if -literal not in flatten]
        self.log.debug("-->>>> flatten: %s"%flatten)
        self.log.debug("-->>>> unique: %s"%unique)
        if unique:
            self.log.debug("found unique symbol unique list: %s returning last one found: %s"%(unique,unique[-1]))
            pure = unique[-1]
        self.log.debug("returning pure literal: %s"%pure)
        return pure

    '''
    :param: clauses
    :param: model
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
    :param: clauses
    :param: symbols
    :return literal
    :rtype int
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
    :param: clauses
    :param: symbols
    :param: model
    :param: q - literal to be un-assigned
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
    check if clause is satisfiable
    '''
    def _satisfied(clause, assignment):
        sat = False
        if (assignment > 0 and clause[-1] > 0) or (assignment < 0 and clause[-1] < 0):
            sat = True

        return sat

    '''
    Forward Chaining
    @todo - test
    '''
    def _unit_propagation(self, clauses, model, assignment):
        return self._simplify(clauses, model, assignment)
        '''
        self.log.debug("!!!!!!!!!!ENTERING _unit_propagation function")
        self.log.debug("inside _unit_propagation function ->>>> assigning: %s"%assignment)
        conflict = False
        for clause in clauses:
            print "!!!!!!!!!!!!!!"
            print "clause: %s"%clause
            #case 1: unit clause
            print "--->>>>!!!!!!assignment: %s"%assignment
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> %s"%((assignment or -assignment) in clause)
            if (assignment or -assignment) in clause:
                print "inside the if statement"
                if len(clause) == self._UNIT_:
                
                    if not (self._satisfied(clause, assignment) or self._satisfied(clause, -assignment)):
                        conflict = True
                        self.log.debug("conflict literal: %s"%conflict)                
                
                (updated_clauses, updated_model) = self._simplify(clauses, model, assignment)
                self.log.debug("updated_clauses: %s"%updated_clauses)
                self.log.debug("updated_model: %s"%updated_model)
        self.log.debug("-->>>> literal should now be removed!!, check clauses:")
        self.log.debug("clauses: %s"%clauses)

        self.log.debug("model: %s"% model)
        self.log.debug("!!!!!!!!!!!!EXITING _unit_propagation function")
        return (clauses, model)
        '''

    '''
    param: clauses
    param: P assignment of literal
    @todo - BUG FIX!!! not working!
    '''
    def _simplify(self, clauses, model, P, conflict=False):

        pp = pprint.PrettyPrinter(indent=4)
        remove_p = []
        pp.pprint(clauses)
        pp.pprint("-->>>> assigning literal: %s"%P)
        self.symbols.assign(P)

        for c in clauses:
            if (P in c) or (-P in c):
                if len(c) == self._UNIT_:
                    if ((P or -P) < 0 and c[-1] > 0) or ((P or -P) > 0 and c[-1] < 0):                        
                        #unsat! this is bad, set to empty clause
                        c[:] = []
                    elif ((P or -P) < 0 and c[-1] < 0) or (P or -P) > 0 and c[-1] > 0: 
                        #double negative is True ==> positive is sat
                        #sat! remove from clauses
                        clauses.remove(c)
                else:
                    if (P or -P) > 0:
                        negative_literal = [ x for x in c if x < 0]
                        if not negative_literal:
                            clauses.remove(c)
                        else:
                            if P in c:
                                c.remove(P)
                            elif -P in c:
                                c.remove(-P)
                    if (P or -P) < 0:
                        if P in c:                        
                            c.remove(P)
                        else:
                            c.remove(-P)

            else:
                print "(%s or %s) is not in clause: %s"%(P, -P, ((P or -P) in c))
    
        pp.pprint(clauses)
        '''
        # Find clauses to remove
        #
        remove_p = [i for i in clauses if (P in i and P < 0) or (P in i and P > 0)]
        self.log.debug("--->>>>>>>>>>>>>>>remove P in following list: %s"%remove_p)
        print "remove_p: %s"%remove_p
        # remove clauses assigned as True  for both model and clauses
        #
        [clauses.remove(clause) for clause in remove_p if len(clause) == self._UNIT_]
        [ i.remove(-P) for i in clauses if (-P in i and P > 0) or (-P in i and P < 0)]
        print "clauses: %s"%clauses
        '''
        print "--->>>> remove from model!!"    
        for cl in model:
            print cl['clause']
            print "-->>>>>>P: %s -P:%s"%(P, -P)
            
            if not isinstance(cl['clause'], bool):
                print "--->>>> --->>>> is P or -P in cl['clause']????%s"%((P or -P) in cl['clause'])
                if (P or -P) in cl['clause']:
                #if cl['clause'] == remove_p:
                   # print "inside first if statement"
                    if len(cl['clause']) == self._UNIT_:
                        if (P or -P) > 0:
                            cl['clause'] = True
                        else:
                            cl['clause'] = []
                    else:
                        print "in side else (not unit clause)"
                        if (P or -P) < 0:
                            print "inside if"
                            cl['clause'].remove((P or -P))
                        else:
                            print "inside else"
                            cl['clause'] = True
            else:
                print "cl['clause'] not in remove_p"

                
                if cl['clause'] in remove_p and len(cl['clause']) == self._UNIT_:
                    cl['clause'] = True
                    self.log.debug("assigning clause: %s to TRUE!!"%cl['clause'])
                

        
        # remove literal from clauses and model
        #
        
        #[ cl['clause'].remove(-P) for cl in model if (-P in cl['clause'] and P > 0) or (-P in cl['clause'] and P < 0)]

        #if conflict:
        empty_clause = [cl['conflict'].append(P) for cl in model if not cl['clause']]
        if empty_clause:
            print "found empty_clause"
            self.log.debug("found empty clause with %s assigning conflict: "%(P, empty_clause))


        pp.pprint(model)
        self.log.debug("-->>>>>>>>>>>>>> exiting _simplify function!!!!")
        return (clauses, model)


