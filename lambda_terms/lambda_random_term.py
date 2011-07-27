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
Generate a random lambda term.
'''

from lambda_term_parser import Abstraction, Application, Variable

import random

freevars  = 0
boundvars = 0

def random_term(_):
    '''
    Generate a random lambda term.
    '''
    global freevars, boundvars

    freevars = 0
    boundvars = 0

    def _node(p, boundlist):
        global freevars, boundvars

        r = random.uniform(0,1)

        if r < p["abstraction"]:
            _p = {}
            _p["variable"]    = p["variable"] + 0.09
            _p["abstraction"] = p["abstraction"] - 0.07
            _p["application"] = p["application"] + 0.02

            b = "b" + str(boundvars)
            boundvars += 1
            term = Abstraction(Variable(b))
            term.setSubterm(_node(_p, boundlist + [b]))
        elif r < p["abstraction"] + p["application"]:
            _lp = {}
            _lp["abstraction"] = p["abstraction"] + 0.04
            _lp["application"] = p["application"] - 0.06
            _lp["variable"]    = p["variable"] + 0.02
            _rp = {}
            _rp["abstraction"] = p["abstraction"] + 0.02
            _rp["application"] = p["application"] - 0.02
            _rp["variable"]    = p["variable"]

            term = Application(_node(_lp, boundlist), _node(_rp, boundlist))
        else:
            if random.uniform(0,1) < 0.95 and not len(boundlist) == 0:
                name = boundlist[random.randint(0, len(boundlist) - 1)]
            else:
                name = "f" + str(freevars)
                freevars += 1

            term = Variable(name)

        return term

    p = {"abstraction" : 0.6,
         "application" : 0.4,
         "variable"    : 0.0
         }

    return str(_node(p, []))
