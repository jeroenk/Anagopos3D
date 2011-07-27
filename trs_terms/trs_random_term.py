# -*- coding: utf-8 -*-
# Anagopos 3D: A Reduction Graph Visualizer for Term Rewriting and λ-Calculus
#
# Copyright (C) 2010, 2011 Niels Bjørn Bugge Grathwohl,
#                          Jens Duelund Pallesen,
#                          Jeroen Ketema
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
Generate a random TRS term.
'''

from trs_term_parser import Function, Variable

import random

varcount = 0

def random_term(signature):
    '''
    Generate a random first-order term for the given signature.
    '''
    global varcount

    varcount = 0

    def _node(p, sig):
        global varcount

        r = random.uniform(0,1)

        if r < p["functionsymbol"]:
            _p = {}
            _p["variable"]       = p["variable"] + 0.09
            _p["functionsymbol"] = p["functionsymbol"] - 0.02

            i = random.randint(0, len(sig) - 1)
            a = sig[i][1]
            s = []

            for _ in range(a):
                s.append(_node(_p, sig))

            term = Function(sig[i][0], s)
        else:
            name = "v" + str(varcount)
            varcount += 1

            while name in signature:
                name = "v" + str(varcount)
                varcount += 1

            term = Variable(name)

        return term

    p = {"functionsymbol" : 0.9,
         "variable"       : 0.1
        }

    sig = signature.items()

    if len(sig) == 0:
        return "v"
    else:
        return str(_node(p, sig))
