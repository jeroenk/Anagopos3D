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

from LambdaTermClass import LambdaAbs, LambdaApp, LambdaVar

position = None
string   = None
symbol   = None

class LambdaTermParseException(Exception):
    pass

class Term(object):
    def toString(self):
        raise LambdaTermParseException("Not implemented")

    def getFreeVars(self):
        raise LambdaTermParseException("Not implemented")

    def convert(self, free_vars):
        raise LambdaTermParseException("Not implemented")

    def __str__(self):
        return self.toString()

class Application(Term):
    def __init__(self, left, right):
        super(Application, self).__init__()

        self.left  = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " " + self.right.toString() + ")"

    def getFreeVars(self):
        left_free  = self.left.getFreeVars()
        right_free = self.right.getFreeVars()
        return left_free | right_free

    def convert(self, free_vars):
        left  = self.left.convert(free_vars)
        right = self.right.convert(free_vars)
        return LambdaApp(left, right)

class Abstraction(Term):
    def __init__(self, var):
        super(Abstraction, self).__init__()

        self.variable = var
        self.subterm  = None

    def setSubterm(self, subterm):
        self.subterm = subterm

    def toString(self):
        return "(\\" + self.variable.toString() + "." \
            + self.subterm.toString() + ")"

    def getFreeVars(self):
        subterm_free = self.subterm.getFreeVars()
        var_var      = self.variable.toString()
        return subterm_free - set([var_var])

    def convert(self, free_vars):
        free_vars_new = free_vars[:]
        var_var       = self.variable.toString()

        if var_var in free_vars_new:
            free_vars_new.remove(var_var)

        free_vars_new.insert(0, var_var)
        return LambdaAbs(self.subterm.convert(free_vars_new))

class Variable(Term):
    def __init__(self, variable):
        super(Variable, self).__init__()

        self.variable = variable

    def toString(self):
        return self.variable

    def getFreeVars(self):
        return set([self.variable])

    def convert(self, free_vars):
        if self.variable in free_vars:
            return LambdaVar(free_vars.index(self.variable))
        else:
            raise LambdaTermParseException("Non-convertible variable found")

def get_symbol():
    global position, symbol

    while position != len(string) \
            and (string[position] == ' ' \
                     or string[position] == '\t' \
                     or string[position] == '\n' \
                     or string[position] == '\r'):
        position += 1

    if position == len(string):
        symbol = '\0'
        return

    symbol = string[position]
    position += 1

def variable():
    if not (symbol >= 'a' and symbol <= 'z'):
        raise LambdaTermParseException("Invalid symbol on input: " + symbol)

    variable_string = symbol[:]
    get_symbol() # consumes letter

    while (symbol >= '0' and symbol <= '9'):
        variable_string += symbol
        get_symbol() # consumes number

    var = Variable(variable_string)
    return var

def abstraction():
    if symbol != '\\':
        raise LambdaTermParseException("Invalid symbol on input: " + symbol)

    get_symbol() # consumes abstraction symbol
    var = variable()
    top = bottom = Abstraction(var)

    while symbol != '.':
        var   = variable()
        abstr = Abstraction(var)
        bottom.setSubterm(abstr)
        bottom = abstr

    get_symbol() # consumes dot
    subterm = term()
    bottom.setSubterm(subterm)
    return top

def term():
    if symbol != '(' \
            and not (symbol >= 'a' and symbol <= 'z') \
            and symbol != '\\':
        raise LambdaTermParseException("Invalid symbol on input: " + symbol)

    first = True

    while symbol == '(' \
            or (symbol >= 'a' and symbol <= 'z') \
            or symbol == '\\':
        if symbol == '(':
            get_symbol() # consumes open parenthesis
            subterm = term()

            if symbol != ')':
                raise LambdaTermParseException("Invalid symbol on input: " \
                                                   + symbol)

            get_symbol() # consumes closing parenthesis
        elif (symbol >= 'a' and symbol <= 'z'):
            subterm = variable()
        elif symbol == '\\':
            subterm = abstraction()

        if first:
            top = subterm
            first = False
        else:
            top = Application(top, subterm)

    return top

def parse(string_in, _):
    global string, position

    string = string_in
    position = 0
    get_symbol()
    whole_term = term()

    if symbol != '\0':
        raise LambdaTermParseException("Symbols left on input: " \
                                           + string[position:])

    free_vars = []

    for var in whole_term.getFreeVars():
        free_vars.append(var)

    return whole_term.convert(free_vars)
