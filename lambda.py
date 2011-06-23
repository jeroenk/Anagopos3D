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

    iterate(omega)
    ubi_iterate(omega)

    print "Finished!"

def fixed_point_test():
    x     = LambdaVar(0)
    xx    = LambdaApp(x.copy(), x.copy())
    f     = LambdaVar(1)
    lfxx  = LambdaAbs(LambdaApp(f.copy(), xx.copy()))
    lfxx2 = LambdaApp(lfxx.copy(), lfxx.copy())
    Y     = LambdaAbs(lfxx2.copy())

    ubi_iterate(Y)

    raise Exception("Should not be reachable!")

#omega_test()
#fixed_point_test()

print "Please input a lambda term: "
line = sys.stdin.readline()
term = lambda_parser.parse(line)
#iterate(term)
ubi_iterate(term)
print "Finished"
