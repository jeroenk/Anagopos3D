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

position  = None
string_in = None
symbol    = None

class LambdaParseException(Exception):
    pass

class Term:
    def toString(self):
        raise LambdaParseException("Not implemented")

    def getFreeVars(self):
        raise LambdaParseException("Not implemented")

    def convert(self, free_vars):
        raise LambdaParseException("Not implemented")

    def __str__(self):
        return self.toString()

class Application(Term):
    def __init__(self, left, right):
        self.left  = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + ")(" + self.right.toString() + ")"

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
        self.variable = var
        self.subterm  = None

    def setSubterm(self, subterm):
        self.subterm = subterm

    def toString(self):
        return "\\" + self.variable.toString() + ".(" \
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
    def __init__(self, string):
        self.string = string

    def toString(self):
        return self.string

    def getFreeVars(self):
        return set([self.string])

    def convert(self, free_vars):
        if self.string in free_vars:
            return LambdaVar(free_vars.index(self.string))
        else:
            raise LambdaParseException("Non-convertible variable found")

def get_symbol():
    global position, symbol

    while position != len(string_in) \
            and (string_in[position] == ' ' \
                     or string_in[position] == '\t' \
                     or string_in[position] == '\n' \
                     or string_in[position] == '\r'):
        position += 1

    if position == len(string_in):
       symbol = '\0'
       return

    symbol = string_in[position]
    position += 1

def variable():
    if not (symbol >= 'a' and symbol <= 'z'):
        raise LambdaParseException("Invalid symbol on input: " + symbol)

    string = symbol[:]
    get_symbol() # consumes letter

    while (symbol >= '0' and symbol <= '9'):
        string += symbol
        get_symbol() # consumes number

    var = Variable(string)
    return var

def abstraction():
    if symbol != '\\':
        raise LambdaParseException("Invalid symbol on input: " + symbol)

    get_symbol() # consumes abstraction symbol
    var = variable()
    top = bottom = Abstraction(var)

    while symbol != '.':
        var = variable()
        ab  = Abstraction(var)
        bottom.setSubterm(ab)
        bottom = ab

    get_symbol() # consumes dot
    subterm = term()
    bottom.setSubterm(subterm)
    return top

def term():
    if symbol != '(' \
            and not (symbol >= 'a' and symbol <= 'z') \
            and symbol != '\\':
        raise LambdaParseException("Invalid symbol on input: " + symbol)

    first = True

    while symbol == '(' \
            or (symbol >= 'a' and symbol <= 'z') \
            or symbol == '\\':
        if symbol == '(':
            get_symbol() # consumes open parenthesis
            subterm = term()

            if symbol != ')':
                raise LambdaParseException("Invalid symbol on input: " + symbol)

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

def parse(string):
    global string_in, position

    string_in = string
    position = 0
    get_symbol()
    whole_term = term()

    if symbol != '\0':
        raise LambdaParseException("Symbols left on input: " \
                                       + string_in[position:])

    free_vars = []

    for var in whole_term.getFreeVars():
        free_vars.append(var)

    return whole_term.convert(free_vars)
