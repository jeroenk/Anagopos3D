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

def omega_test():
    x     = LambdaVar(0)
    xx    = LambdaApp(x.copy(), x.copy())
    delta = LambdaAbs(xx.copy())
    omega = LambdaApp(delta.copy(), delta.copy())

    iterate(omega)

    print "Finished!"

def fixed_point_test():
    x     = LambdaVar(0)
    xx    = LambdaApp(x.copy(), x.copy())
    f     = LambdaVar(1)
    lfxx  = LambdaAbs(LambdaApp(f.copy(), xx.copy()))
    lfxx2 = LambdaApp(lfxx.copy(), lfxx.copy())
    Y     = LambdaAbs(lfxx2.copy())

    iterate(Y)

    raise Exception("Should not be reachable!")

omega_test()
fixed_point_test()
