# -*- coding: utf-8 -*-
# Anagopos 3D: A Reduction Graph Visualizer for Term Rewriting and λ-Calculus
#
# Copyright (C) 2010, 2011 Niels Bjørn Bugge Grathwohl,
#                          Jens Duelund Pallesen,
#                          Jeroen Ketema
#
# Reduction Visualizer. A tool for visualization of reduction graphs.
# Copyright (C) 2010 Niels Bjoern Bugge Grathwohl and Jens Duelund Pallesen
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

'''
Choose the reduction "mode". Currently there are two choices: λ-calculus and
a first-order term rewriting. The proxy functions here take care of selecting
the correct reduction mechanisms and the correct parser.
'''

from lambda_parser import parse as lambda_parser

_mode = ""

def set_mode(mode):
    '''
    Set the mode, i.e. choose which parser and associated operations to use:
    "trs" or "lambda".
    '''

    global OPS, PARSER, TPDBPARSER, _mode
    if mode == "lambda":
        #OPS         = lambda_operations
        PARSER      = lambda_parser
        #RULE_PARSER = None
    #elif mode == "trs":
        #OPS         = trs_operations
        #PARSER      = trs_parser
        #RULE_PARSER = tpdb_parser
    #else:
    #    raise Exception("Unsupported mode: " + mode)

    _mode = mode

def get_mode():
    return _mode

def parse_rule_set(rule_string):
    if RULE_PARSER == None:
        raise Exception("Rule set parsing not supported in " + _mode + " mode")

    return RULE_PARSER.parse_rule_set(rule_string)

def parse(term_string):
    '''
    Parse a term.
    '''
    return PARSER(term_string)

def random_term():
    return RANDOM_TERM()
