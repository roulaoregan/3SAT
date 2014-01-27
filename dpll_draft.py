
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

'''
Handles file input errors
'''
class FileInputError(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)

'''
maintains a list of all literals and a stack of the assigned literals
maintain all the conflicts

we need to monitor whether this literal as been assigned twice. the stack will push assigned literals, need to check
        if the literal and it's negation are in the stack
        So: first pass, "assign" literal as either T or F, if this causes a conflict, reassigned will be called and
        cbj() will try the negation of the literal. If there is a conflict with the negation, the next iteration will check
        if this literal as been already reassigned, if it returns TRUE then the procedure has tried both TRUE and FALSE and
        therefore we can no longer continue and will have to report UNSAT.
Maintains a set of literals in a sentence (in Conjunctive Normal Form) as well as the assigned literals used during
the DPLL procedure
'''
class Literals(object):
        def __init__(self):
                self.literals = set()
                self.stack = []
                #maintain a current stack of conflicts, push and pop conflicts
                self.conflicts = []
                #is a record/memo of all the conflicts that are resolved
                self.prev_assigned = []

        def add(literal):
                if literal not in self.literals:
                        self.literals.append(literal)

        #def is_reassigned(literal):
        #       return (literal in self.reassigned)

        '''
        def reassign(literal):
                reassigned = False
                if (literal and -literal) in self.stack:
                        reassigned = True
                else:
                        self.unresolved.append(abs(literal))

                return reassigned
        '''
        def unassign(literal):
                if literal in self.stack:
                        self.stack.remove(literal)
                if literal in self.conflicts:
                        sell=f.conflicts.remove(literal)
                #add to record
                if literal not in self.prev_assigned:
                        self.prev_assigned.append(literal)

        def conflict(literal):
                self.conflicts.append(literal)
                

        def unresolved(literal):
                return ((literal and -literal) in self.conflicts)

        def previously_assigned(literal):
                return ((literal or -literal) in self.prev_assigned)
        '''

        '''
        def assign(literal):
                assign = True
                if ((literal or -literal) not in self.stack and not in self.unresolved(literal):
                        self.stack.append((literal)
                else:
                        assign = False

                return assign

        def pop():
                unassign = self.stack.pop()
                self.prev_assigned.append(unassign)
                return unassign

        #check if stack is empty, ie check if we have backtracked to the beginning
        def empty():
                empty = False
                if not self.stack:
                        empty = True
                return empty
                
                
'''
Parse the Dimacs file which is in Conjunctive Normal Form

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

'''
@param sentence tuple in the form of (clauses, symbols, model)
@returns whether sentence in CNF is SAT
@rtype boolean
'''
def dpll_satisfiable(sentence):

        return dpll(sentence[0], sentence[1], sentence[2])


'''
Get the most frequently seen literal
@param clauses
@param symbols
@return literal
@rtype int
'''
def most_watched(clauses, symbols):

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
def cbj(clauses, symbols, model, q):

        resolved = True
        if symbols.unresolved(q):
                resolved = False
        elif symbols.assign(q):
                (clauses, model, q) = simplify(clauses, model, q)
                empty_clause = [x for x in model if not x.get('clause', None)]
                if empty_clause:
                        resolved = False

        return resolved
'''
undo assignment of literal q and restores previous state
@param clauses
@param symbols
@param model
@param q - literal to be un-assigned
'''
def undo(clauses, symbols, model, q):
        #unassign literal q in symbols
        symbols.unassign(q)
        #insert q back in the model
        [x['clause'].append(q) if q in x['original'] else (x['clause'].append(-q) if -q in x['original'] else x) for x in model]


'''
Called when a conflict occurs
Undoes the latest assignment and re-assigns literal with its negation
e.g.: A=False caused a conflict, reassign to A=True and visa versa
@param clauses
@param symbols
@param model
@param q literal to be re-assigned
'''
def backtrack(clauses, symbols, model, q):

        undo(clauses, symbols, model, q)
        is_assigned = cbj(clauses, symbols, model, -q)
        if not is_assigned:
                if not symbols.empty():
                        previous_q = symbols.pop()
                        return backtrack(clauses, symbols, model, previous_q)
                else:
                        is_assigned = False

        return is_assigned


'''
@param: clauses
@param: symbols
@param: model
@return first pure literal seen
'''
def find_pure_symbol(clauses, symbols, model):
        pure = None
        flatten = [ sublist for x in clauses for sublist in x]
        unique = [ literal for literal in flatten if -literal not in flatten]
        if unique:
                pure = unique[-1]
        return pure

'''
@param: clauses
@param: model
'''
def find_unit_clause(clauses, model):

        found_literals = []
        for cl in model:
                if len(cl['clause']) == 1:
                        literal = cl['clause'][-1]
                        found_literals.append(literal)

                        #double negation if (-C) then C must be False to get --C ==> C
                        # if literal is (C) then C must be True
                        (clauses, model, assignment) = unit_propagation2(clauses, model, literal)


        return found_literals

'''
Forward Chaining

@param: model
@param: P a literal that is assigned either True or False
'''
def update_model(model, P):
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
                        cl['conflict'] = P


'''
check if clause is satisfiable
'''
def satisfied(clause, assignment):

        sat = False
        if (assignment > 0 and clause[-1] > 0) or (assignment < 0 and clause[-1] < 0):
                sat = True

        return sat

'''
'''
def unit_propagation2(clauses, model, assignment):

        for cl in clauses:
                if len(cl['clause']) == 1:
                        if cl['clause'] == assignment or cl['clause'] == -assignment:
                                if satisfied(cl['clause'], assignment):
                                        clauses, model, assignment = simplify(clauses, model, assignment)
                                        return unit_propagation2(clauses, model, assignment)
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
def simplify(clauses, model, P):

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

'''
@param: model, list of dictionaries
        e.g. [{'clause':[4, 3, 22], 'original':[4, 3, 22]},{'clause': [7, 2, 3], 'original': [7, 2, 3}]
        if clause is all assigned to "TRUE" change dictionary to:
                {'clause': True, 'original': [7, 2, 3]}
        if clause is False:
                {'clause':[], 'original': [7, 2, 3]}
        if there is a conflict:
                {'clause':[], 'original': [9,5,3], 'conflict': [-9]}
@param: symbols, set set([7, 15, 8, 4,12])
@param: clauses --> remains unchanged!!! list of lists: [[7,2,3],[6,-14,2],[7,15,-3]]
'''
def dpll(clauses, symbols, model={}):

        #if every clause in clauses is True in model return True
        if model:
                clause_values = [x for x in model if 'clause' in x and x['clause'] == True]
                if len(clause_values) == len(model):
                        return True
                        
        #if some clause is clauses is False in model return False
        if model:
                empty_clause = [x for x in model if not x.get('clause', None)]

                if empty_clause:
                        #call backtrack()
                        ["found empty clause, original clause: %s conflict with literal: %s"%(x['original'], x['conflict']) for x in empty_clause]
                        return False

        #Heuristic 1: Pure Symbol
        P = find_pure_symbol(clauses, symbols, model)

        if P is not None:

                symbols.remove(P)
                unit_propagation(model,P)

                return dpll(clauses, symbols, model)

        #Heuristic 2: Unit Clause and Unit Propagation
        P = find_unit_clause(clauses, model)
        if P is not None:
                [symbols.remove(symbol) for symbol in P]
                (clauses, model, assignment) = unit_propagation2(clauses, model, P)
                symbols.remove(assignment)
                return dpll(clauses, symbols, model)

        #Rest
        P = most_watched(clauses,symbols)
        #if P is not None:
        symbols.remove(P)
        update_model(model, P)

        return dpll(clauses, symbols, model)


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

'''
Handles file input errors
'''
class FileInputError(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)

'''
maintains a list of all literals and a stack of the assigned literals
maintain all the conflicts

we need to monitor whether this literal as been assigned twice. the stack will push assigned literals, need to check
        if the literal and it's negation are in the stack
        So: first pass, "assign" literal as either T or F, if this causes a conflict, reassigned will be called and
        cbj() will try the negation of the literal. If there is a conflict with the negation, the next iteration will check
        if this literal as been already reassigned, if it returns TRUE then the procedure has tried both TRUE and FALSE and
        therefore we can no longer continue and will have to report UNSAT.
Maintains a set of literals in a sentence (in Conjunctive Normal Form) as well as the assigned literals used during
the DPLL procedure
'''
class Literals(object):
        def __init__(self):
                self.literals = set()
                self.stack = []
                #maintain a current stack of conflicts, push and pop conflicts
                self.conflicts = []
                #is a record/memo of all the conflicts that are resolved
                self.prev_assigned = []

        def add(literal):
                if literal not in self.literals:
                        self.literals.append(literal)

        #def is_reassigned(literal):
        #       return (literal in self.reassigned)

        '''
        def reassign(literal):
                reassigned = False
                if (literal and -literal) in self.stack:
                        reassigned = True
                else:
                        self.unresolved.append(abs(literal))

                return reassigned
        '''
        def unassign(literal):
                if literal in self.stack:
                        self.stack.remove(literal)
                if literal in self.conflicts:
                        sell=f.conflicts.remove(literal)
                #add to record
                if literal not in self.prev_assigned:
                        self.prev_assigned.append(literal)

        def conflict(literal):
                self.conflicts.append(literal)
                

        def unresolved(literal):
                return ((literal and -literal) in self.conflicts)

        def previously_assigned(literal):
                return ((literal or -literal) in self.prev_assigned)
        '''

        '''
        def assign(literal):
                assign = True
                if ((literal or -literal) not in self.stack and not in self.unresolved(literal):
                        self.stack.append((literal)
                else:
                        assign = False

                return assign

        def pop():
                unassign = self.stack.pop()
                self.prev_assigned.append(unassign)
                return unassign

        #check if stack is empty, ie check if we have backtracked to the beginning
        def empty():
                empty = False
                if not self.stack:
                        empty = True
                return empty
                
                
'''
Parse the Dimacs file which is in Conjunctive Normal Form

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

'''
@param sentence tuple in the form of (clauses, symbols, model)
@returns whether sentence in CNF is SAT
@rtype boolean
'''
def dpll_satisfiable(sentence):

        return dpll(sentence[0], sentence[1], sentence[2])


'''
Get the most frequently seen literal
@param clauses
@param symbols
@return literal
@rtype int
'''
def most_watched(clauses, symbols):

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
def cbj(clauses, symbols, model, q):

        resolved = True
        if symbols.unresolved(q):
                resolved = False
        elif symbols.assign(q):
                (clauses, model, q) = simplify(clauses, model, q)
                empty_clause = [x for x in model if not x.get('clause', None)]
                if empty_clause:
                        resolved = False

        return resolved
'''
undo assignment of literal q and restores previous state
@param clauses
@param symbols
@param model
@param q - literal to be un-assigned
'''
def undo(clauses, symbols, model, q):
        #unassign literal q in symbols
        symbols.unassign(q)
        #insert q back in the model
        [x['clause'].append(q) if q in x['original'] else (x['clause'].append(-q) if -q in x['original'] else x) for x in model]


'''
Called when a conflict occurs
Undoes the latest assignment and re-assigns literal with its negation
e.g.: A=False caused a conflict, reassign to A=True and visa versa
@param clauses
@param symbols
@param model
@param q literal to be re-assigned
'''
def backtrack(clauses, symbols, model, q):

        undo(clauses, symbols, model, q)
        is_assigned = cbj(clauses, symbols, model, -q)
        if not is_assigned:
                if not symbols.empty():
                        previous_q = symbols.pop()
                        return backtrack(clauses, symbols, model, previous_q)
                else:
                        is_assigned = False

        return is_assigned


'''
@param: clauses
@param: symbols
@param: model
@return first pure literal seen
'''
def find_pure_symbol(clauses, symbols, model):
        pure = None
        flatten = [ sublist for x in clauses for sublist in x]
        unique = [ literal for literal in flatten if -literal not in flatten]
        if unique:
                pure = unique[-1]
        return pure

'''
@param: clauses
@param: model
'''
def find_unit_clause(clauses, model):

        found_literals = []
        for cl in model:
                if len(cl['clause']) == 1:
                        literal = cl['clause'][-1]
                        found_literals.append(literal)

                        #double negation if (-C) then C must be False to get --C ==> C
                        # if literal is (C) then C must be True
                        (clauses, model, assignment) = unit_propagation2(clauses, model, literal)


        return found_literals

'''
Forward Chaining

@param: model
@param: P a literal that is assigned either True or False
'''
def update_model(model, P):
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
                        cl['conflict'] = P


'''
check if clause is satisfiable
'''
def satisfied(clause, assignment):

        sat = False
        if (assignment > 0 and clause[-1] > 0) or (assignment < 0 and clause[-1] < 0):
                sat = True

        return sat

'''
'''
def unit_propagation2(clauses, model, assignment):

        for cl in clauses:
                if len(cl['clause']) == 1:
                        if cl['clause'] == assignment or cl['clause'] == -assignment:
                                if satisfied(cl['clause'], assignment):
                                        clauses, model, assignment = simplify(clauses, model, assignment)
                                        return unit_propagation2(clauses, model, assignment)
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
def simplify(clauses, model, P):

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

'''
@param: model, list of dictionaries
        e.g. [{'clause':[4, 3, 22], 'original':[4, 3, 22]},{'clause': [7, 2, 3], 'original': [7, 2, 3}]
        if clause is all assigned to "TRUE" change dictionary to:
                {'clause': True, 'original': [7, 2, 3]}
        if clause is False:
                {'clause':[], 'original': [7, 2, 3]}
        if there is a conflict:
                {'clause':[], 'original': [9,5,3], 'conflict': [-9]}
@param: symbols, set set([7, 15, 8, 4,12])
@param: clauses --> remains unchanged!!! list of lists: [[7,2,3],[6,-14,2],[7,15,-3]]
'''
def dpll(clauses, symbols, model={}):

        #if every clause in clauses is True in model return True
        if model:
                clause_values = [x for x in model if 'clause' in x and x['clause'] == True]
                if len(clause_values) == len(model):
                        return True
                        
        #if some clause is clauses is False in model return False
        if model:
                empty_clause = [x for x in model if not x.get('clause', None)]

                if empty_clause:
                        #call backtrack()
                        ["found empty clause, original clause: %s conflict with literal: %s"%(x['original'], x['conflict']) for x in empty_clause]
                        return False

        #Heuristic 1: Pure Symbol
        P = find_pure_symbol(clauses, symbols, model)

        if P is not None:

                symbols.remove(P)
                unit_propagation(model,P)

                return dpll(clauses, symbols, model)

        #Heuristic 2: Unit Clause and Unit Propagation
        P = find_unit_clause(clauses, model)
        if P is not None:
                [symbols.remove(symbol) for symbol in P]
                (clauses, model, assignment) = unit_propagation2(clauses, model, P)
                symbols.remove(assignment)
                return dpll(clauses, symbols, model)

        #Rest
        P = most_watched(clauses,symbols)
        #if P is not None:
        symbols.remove(P)
        update_model(model, P)

        return dpll(clauses, symbols, model)


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
















































                
                
                
                
                
                
                










                
                
                
                
                
                
                
