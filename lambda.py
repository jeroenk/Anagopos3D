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

import sys
import lambda_parser
import ubigraph

from collections import deque
from LambdaTermClass import LambdaAbs, LambdaApp, LambdaVar

#LambdaTermClass.test()

def iterate(term):
    seen = {term : 0}
    todo = deque([(term, 0)])

    while todo != deque([]):
        (term, level) = todo.popleft()
        print str(level) + ": " + str(term)
        for position in term.getRedexPositions():
            reduct = term.reduce(position)
            if reduct not in seen:
                seen[reduct] = level + 1
                todo.append((reduct, level + 1))

def ubi_iterate(term):
    U = ubigraph.Ubigraph()
    U.clear();

    smallRed = U.newVertexStyle(shape="sphere", color="#ff0000", size="1.0")
    x = U.newVertex(style = smallRed, label = str(term))

    seen = {term : x}
    todo = deque([(term, x)])

    while todo != deque([]):
        (term, x_old) = todo.popleft()
        for position in term.getRedexPositions():
            reduct = term.reduce(position)

            if reduct == term:
                continue

            if reduct not in seen:
                x = U.newVertex(style = smallRed)
                U.newEdge(x_old, x, width = "2.0", color = "#ffffff")
                seen[reduct] = x
                todo.append((reduct, x))
            else:
                x = seen[reduct]
                U.newEdge(x_old, x, width = "2.0", color = "#ffffff")

def omega_test():
    x     = LambdaVar(0)
    xx    = LambdaApp(x.copy(), x.copy())
    delta = LambdaAbs(xx.copy())
    omega = LambdaApp(delta.copy(), delta.copy())

    for t in omega:
        print t

    #iterate(omega)
    #ubi_iterate(omega)

    print "Finished!"

def fixed_point_test():
    x     = LambdaVar(0)
    xx    = LambdaApp(x.copy(), x.copy())
    f     = LambdaVar(1)
    lfxx  = LambdaAbs(LambdaApp(f.copy(), xx.copy()))
    lfxx2 = LambdaApp(lfxx.copy(), lfxx.copy())
    Y     = LambdaAbs(lfxx2.copy())

    for t in Y:
        print t

    #ubi_iterate(Y)

    raise Exception("Should not be reachable!")

#omega_test()
fixed_point_test()

#print "Please input a lambda term: "
#line = sys.stdin.readline()
#term = lambda_parser.parse(line)
#iterate(term)
#ubi_iterate(term)
print "Finished"
