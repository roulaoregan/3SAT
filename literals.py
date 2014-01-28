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
        def __init__(self, literals=[]):
                self.literals = set()
                if literals:
                        self.literals = set(literals)
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
  
