# -*- coding: utf-8 -*-
# Anagopos 3D: A Reduction Graph Visualizer for Term Rewriting and λ-Calculus
#
# Copyright (C) 2011 Jeroen Ketema
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import deque

class TRSException(Exception):
    pass

class TRSFunctionSymbol:
    def __init__(self, symbol, arity):
        self.symbol = symbol
        self.arity  = arity

    def getSymbol(self):
        return self.symbol

    def getArity(self):
        return self.arity

    def isEqual(self, symbol):
        return self.symbol == symbol.symbol and self.arity == symbol.arity

    def __eq__(self, other):
        if not isinstance(other, TRSFunctionSymbol):
            return False

        return self.isEqual(other)

    def __ne__(self, other):
        if not isinstance(other, TRSFunctionSymbol):
            return True

        return not self.isEqual(other)

    def __hash__(self):
        return self.symbol.__hash__()

    def __str__(self):
        return self.symbol

class TRSTerm:
    def __init__(self):
        raise TRSException("Not implemented")

    def isFun(self):
        return False

    def isVar(self):
        return False

    def match(self, term):
        raise TRSException("Not implemented")

    def getRedexPositions(self, rule_set):
        return []

    def substitute(self, substitution):
        raise TRSException("Not implemented")

    def reduce(self, position, rule):
        raise TRSException("Invalid operation")

    def isEqual(self, term):
        return False

    def copy(self):
        raise Exception("Not implemented")

    def toString(self):
        raise Exception("Not implemented")

    def __eq__(self, other):
        if not isinstance(other, TRSTerm):
            return False

        return self.isEqual(other)

    def __ne__(self, other):
        if not isinstance(other, TRSTerm):
            return True

        return not self.isEqual(other)

    def __hash__(self):
        return self.toString().__hash__()

    def __str__(self):
        return self.toString()

    def addRuleSetForIter(self, rule_set):
        self.rule_set = rule_set

    def __iter__(self):
        return TRSTermIterator(self, self.rule_set)

class TRSFun(TRSTerm):
    def __init__(self, symbol, subterms):
        if len(subterms) != symbol.getArity():
            raise TRSException("Number of subterms different from arity")

        self.symbol   = symbol
        self.subterms = subterms

    def isFun(self):
        return True

    def match(self, term):
        if not term.isFun():
            return None

        if self.symbol != term.symbol:
            return None

        substitution = {}

        for i in range(self.symbol.getArity()):
            subterm_substitution = self.subterms[i].match(term.subterms[i])

            if subterm_substitution == None:
                return None

            for variable in subterm_substitution:
                if variable not in substitution:
                    substitution[variable] = subterm_substitution[variable]
                elif subterm_substitution[variable] != substition[variable]:
                    return None

        return substitution

    def getRedexPositions(self, rule_set):
        redexes = []

        for rule in rule_set:
            substitution = rule.getLeft().match(self)

            if substitution != None:
                redex = ([], rule)
                redexes.append(redex)

        for i in range(self.symbol.getArity()):
            def prepend_i(redex):
                return ([i] + redex[0], redex[1])

            subterm_redexes = self.subterms[i].getRedexPositions(rule_set)
            redexes += map(prepend_i, subterm_redexes)

        return redexes

    def substitute(self, substitution):
        subterms = []

        for subterm in self.subterms:
            subterms.append(subterm.substitute(substitution))

        return TRSFun(self.symbol, subterms)

    def reduce(self, position, rule):
        if position == []:
            substitution = rule.getLeft().match(self)

            if substitution == None:
                raise TRSException("Invalid operation")

            return rule.getRight().substitute(substitution)
        else:
            arity = self.symbol.getArity()

            if position[0] >= arity:
                raise TRSException("Invalid operation")

            subterms = []

            for i in range(arity):
                if i == position[0]:
                    subterm = self.subterms[i].reduce(position[1:], rule)
                else:
                    subterm = self.subterms[i].copy()

                subterms.append(subterm)

            return TRSFun(self.symbol, subterms)

    def isEqual(self, term):
        if not term.isFun():
            return False

        if self.symbol != term.symbol:
            return False

        for i in range(self.symbol.getArity()):
            if not self.subterms[i].isEqual(term.subterms[i]):
                return False

        return True

    def copy(self):
        subterms = []

        for subterm in self.subterms:
            subterms.append(subterm.copy())

        return TRSFun(self.symbol, subterms)

    def toString(self):
        term  = self.symbol.getSymbol()
        count = self.symbol.getArity()

        if count > 0:
            term += "("

            for subterm in self.subterms:
                term += subterm.toString()
                count -= 1

                if count > 0:
                    term += ", "

            term += ")"

        return term

class TRSVar(TRSTerm):
    def __init__(self, variable):
        self.variable = variable

    def isVar(self):
        return True

    def match(self, term):
        return {self.variable : term}

    def substitute(self, substitution):
        if self.variable in substitution:
            return substitution[self.variable].copy()
        else:
            return TRSVar(self.variable)

    def isEqual(self, term):
        if not term.isVar():
            return False

        return self.variable == term.variable

    def copy(self):
        return TRSVar(self.variable)

    def toString(self):
        return self.variable

class TRSRule:
    def __init__(self, left, right):
        self.left  = left
        self.right = right

    def getLeft(self):
        return self.left

    def getRight(self):
        return self.right

    def __str__(self):
        return str(self.left) + " -> " + str(self.right)

class TRSTermIterator:
    def __init__(self, term, rule_set):
        self.term     = term
        self.seen     = {term : 0}
        self.todo     = deque([(term, 0)])
        self.count    = 0
        self.reducts  = deque([(term, 0, -1, True)])
        self.rule_set = rule_set

    def __iter__(self):
        return TRSTermIterator(self.term, self.rule_set)

    def next(self):
        if self.reducts != deque([]):
            reduct = self.reducts.popleft()
            return reduct

        if self.todo == deque([]):
            raise StopIteration

        (term, number) = self.todo.popleft()

        for (position, rule) in term.getRedexPositions(self.rule_set):
            reduct = term.reduce(position, rule)
            new = False

            if reduct not in self.seen:
                self.count += 1
                self.seen[reduct] = self.count
                self.todo.append((reduct, self.count))
                new = True

            self.reducts.append((reduct, self.seen[reduct], number, new))

        return self.next()
