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

from TRSTermClass import TRSFunctionSymbol, TRSFun, TRSVar

position  = None
string    = None
symbol    = None
signature = None

class TRSTermParseException(Exception):
    pass

class Term:
    def toString(self):
        raise LambdaParseException("Not implemented")

    def convert(self):
        raise LambdaParseException("Not implemented")

    def __str__(self):
        return self.toString()

class Function(Term):
    def __init__(self, symbol, subterms):
        self.symbol   = symbol
        self.subterms = subterms

    def toString(self):
        term  = self.symbol
        count = len(self.subterms)

        if count > 0:
            term += "("

            for subterm in self.subterms:
                term += subterm.toString()
                count -= 1

                if count > 0:
                    term += ", "

            term += ")"

        return term

    def convert(self):
        symbol = TRSFunctionSymbol(self.symbol, len(self.subterms))

        subterms = []

        for subterm in self.subterms:
            subterms.append(subterm.convert())

        return TRSFun(symbol, subterms)

class Variable(Term):
    def __init__(self, variable):
        self.variable = variable

    def toString(self):
        return self.variable

    def convert(self):
        return TRSVar(self.variable)

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

def get_identifier():
    global position

    identifier = ""
    identifier += symbol

    while position != len(string) \
            and ((string[position] >= 'a' and string[position] <= 'z') \
                     or (string[position] >= 'A' and string[position] <= 'Z') \
                     or (string[position] >= '0' and string[position] <= '9')):
            identifier += string[position]
            position += 1

    get_symbol()
    return identifier

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

def term():
    if not (symbol >= 'a' and symbol <= 'z') \
            and not (symbol >= 'A' and symbol <= 'Z') \
            and not (symbol >= '0' and symbol <= '9'):
        raise TRSTermParseException("Invalid symbol on input: " + symbol)

    identifier = get_identifier()

    if identifier in signature:
        arity = signature[identifier]

        if arity == 0:
            return Function(identifier, [])

        if symbol != '(':
            raise TRSTermParseException("Invalid symbol on input: " + symbol)

        get_symbol() # consumes open parenthesis
        subterms = []
        subterms.append(term())

        while symbol == ",":
            get_symbol() # consumes the comma
            subterms.append(term())

        if symbol != ')':
            raise TRSTermParseException("Invalid symbol on input: " + symbol)

        get_symbol() # consumes closing parenthesis

        if len(subterms) != arity:
            print signature
            print arity
            raise TRSTermParseException("Arity wrong for: " + identifier)

        return Function(identifier, subterms)
    else:
        return Variable(identifier)

def parse(string_in, signature_in):
    global string, position, signature

    string = string_in
    signature = signature_in
    position = 0
    get_symbol()
    whole_term = term()

    if symbol != '\0':
        raise TRSTermParseException("Symbols left on input: " \
                                        + string[position:])

    return whole_term.convert()
