'''
Maintains a set of literals in a sentence (in Conjunctive Normal Form) as well as the assigned literals used during
the DPLL procedure
Also maintains all the conflicts (resolved and unresolved)

Note:
we need to monitor whether this literal as been assigned twice. the stack will push assigned literals, need to check
if the literal and it's negation are in the stack
So: first pass, "assign" literal as either T or F, if this causes a conflict, reassigned will be called and
cbj() will try the negation of the literal. If there is a conflict with the negation, the next iteration will check
 if this literal as been already reassigned, if it returns TRUE then the procedure has tried both TRUE and FALSE and
therefore we can no longer continue and will have to report UNSAT.

'''
class Literals(object):
        def __init__(self):
                self.literals = set()
                self.assigned_stack = []
                #maintain a current stack of conflicts, push and pop conflicts
                self.conflicts = []
                #is a record/memo of all the conflicts that are resolved
                self.prev_assigned = []

        def add(self, literal):
                if literal not in self.literals:
                        self.literals.add(literal)

        def unassign(self, literal):
                if literal in self.assigned_stack:
                        self.assigned_stack.remove(literal)
                if literal in self.conflicts:
                        sell=f.conflicts.remove(literal)
                #add to record
                if literal not in self.prev_assigned:
                        self.prev_assigned.append(literal)

        def conflict(self, literal):
                self.conflicts.append(literal)
                

        def unresolved(self, literal):
                return ((literal and -literal) in self.conflicts)

        def previously_assigned(self, literal):
                return ((literal or -literal) in self.prev_assigned)

        def assign(self, literal):
                assign = False
                if ((literal or -literal) not in self.assigned_stack) and not self.unresolved(literal):
                        self.assigned_stack.append(literal)
                        assign = True

                return assign

        def pop(self):
                unassign = self.assigned_stack.pop()
                self.prev_assigned.append(unassign)
                return unassign

        
        def remove(self, literal):
                print self.literals
                if literal in self.literals:
                        self.literals.remove(literal)

        #check if stack is empty, ie check if we have backtracked to the beginning
        def empty(self):
                empty = False
                if not self.assigned_stack:
                        empty = True
                return empty

