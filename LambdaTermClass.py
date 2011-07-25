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

class LambdaTermIterator:
    def __init__(self, term):
        self.term    = term
        self.seen    = {term : 0}
        self.todo    = deque([(term, 0)])
        self.count   = 0
        self.reducts = deque([(term, 0, -1)])

    def __iter__(self):
        return LambdaTermIterator(term)

    def next(self):
        if self.reducts != deque([]):
            reduct = self.reducts.popleft()
            return reduct

        if self.todo == deque([]):
            raise StopIteration

        (term, number) = self.todo.popleft()

        for position in term.getRedexPositions():
            reduct = term.reduce(position)

            if reduct not in self.seen:
                self.count += 1
                self.seen[reduct] = self.count
                self.todo.append((reduct, self.count))

            self.reducts.append((reduct, self.seen[reduct], number))

        return self.next()

class LambdaTerm:
    def __init__(self):
        raise Exception("Not implemented")

    def isAbs(self):
        return False

    def isApp(self):
        return False

    def isVar(self):
        return False

    def isRedex(self):
        return False

    def getRedexPositions(self):
        return []

    def substitute(self, term, i):
        raise Exception("Not implemented")

    def renumber(self, i, j):
        raise Exception("Not implemented")

    def reduce(self, position):
        raise Exception("Invalid operation")

    def isEqual(self, term):
        return False

    def copy(self):
        raise Exception("Not implemented")

    def toString(self):
        raise Exception("Not implemented")

    def __eq__(self, other):
        return self.isEqual(other)

    def __hash__(self):
        return self.toString().__hash__()

    def __str__(self):
        return self.toString()

    def __iter__(self):
        return LambdaTermIterator(self)

class LambdaAbs(LambdaTerm):
    def __init__(self, subterm):
        self.subterm = subterm

    def setSubterm(self, subterm):
        self.subterm = subterm

    def getSubterm(self):
        return self.subterm

    def isAbs(self):
        return True

    def getRedexPositions(self):
        def prepend_zero(position):
            return [0] + position

        positions = map(prepend_zero, self.subterm.getRedexPositions())
        return positions

    def substitute(self, term, i):
        subterm = self.subterm.substitute(term, i + 1)
        return LambdaAbs(subterm)

    def renumber(self, i, j):
        subterm = self.subterm.renumber(i, j + 1)
        return LambdaAbs(subterm)

    def reduce(self, position):
        if position == [] or position[0] != 0:
            raise Exception("Invalid operation")
        else:
            subterm = self.subterm.reduce(position[1:])
            return LambdaAbs(subterm)

    def isEqual(self, term):
        if not term.isAbs():
            return False

        return self.subterm.isEqual(term.getSubterm())

    def copy(self):
        subterm = self.subterm.copy()
        term = LambdaAbs(subterm)
        return term

    def toString(self):
        return "(\\" + self.subterm.toString() + ")"

class LambdaApp(LambdaTerm):
    def __init__(self, left, right):
        self.left  = left
        self.right = right

    def setLeft(self, subterm):
        self.left = subterm

    def setRight(self, subterm):
        self.right = subterm

    def getLeft(self):
        return self.left

    def getRight(self):
        return self.right

    def isApp(self):
        return True

    def isRedex(self):
        return self.left.isAbs()

    def getRedexPositions(self):
        def prepend_one(position):
            return [1] + position

        def prepend_two(position):
            return [2] + position

        left_positions  = map(prepend_one, self.left.getRedexPositions())
        right_positions = map(prepend_two, self.right.getRedexPositions())
        top_position    = [[]] if self.isRedex() else []
        positions       = top_position + left_positions + right_positions
        return positions

    def substitute(self, term, i):
        left  = self.left.substitute(term, i)
        right = self.right.substitute(term, i)
        return LambdaApp(left, right)

    def renumber(self, i, j):
        left  = self.left.renumber(i, j)
        right = self.right.renumber(i, j)
        return LambdaApp(left, right)

    def reduce(self, position):
        if position == []:
            if not self.isRedex():
                raise Exception("Invalid operation")
            else:
                subterm = self.left.getSubterm()
                return subterm.substitute(self.right, 0)
        elif position[0] == 1:
            left  = self.left.reduce(position[1:])
            right = self.right.copy()
            return LambdaApp(left, right)
        elif position[0] == 2:
            left  = self.left.copy()
            right = self.right.reduce(position[1:])
            return LambdaApp(left, right)
        else:
            raise Exception("Invalid operation")

    def isEqual(self, term):
        if not term.isApp():
            return False

        return self.left.isEqual(term.getLeft()) \
            and self.right.isEqual(term.getRight())

    def copy(self):
        left  = self.left.copy()
        right = self.right.copy()
        term  = LambdaApp(left, right)
        return term

    def toString(self):
        return "(" + self.left.toString() + self.right.toString() + ")"

class LambdaVar(LambdaTerm):
    def __init__(self, value):
        self.value = value

    def setValue(self, value):
        self.value = value

    def getValue(self):
        return self.value

    def isVar(self):
        return True

    def substitute(self, term, i):
        if self.value < i:
            return LambdaVar(self.value)
        elif self.value == i:
            return term.renumber(i, 0)
        else: # self.value > i
            return LambdaVar(self.value - 1)

    def renumber(self, i, j):
        if self.value < j:
            return LambdaVar(self.value)
        else: # self.value >= j
            return LambdaVar(self.value + i)

    def isEqual(self, term):
        if not term.isVar():
            return False

        return self.value == term.getValue()

    def copy(self):
        term = LambdaVar(self.value)
        return term

    def toString(self):
        return str(self.value)
