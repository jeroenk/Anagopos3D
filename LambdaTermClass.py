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
        return "\.(" + self.subterm.toString() + ")"

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
        return "(" + self.left.toString() + ")(" + self.right.toString() + ")"

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

def test():
    x  = LambdaVar(0)
    y  = LambdaVar(0)
    ab = LambdaAbs(x)
    t1 = LambdaApp(ab, y)

    print t1

    t2 = t1.copy()

    print t1.isRedex()
    print ab.isRedex()

    print t1 == t2

    t3 = LambdaApp(t1, t2)

    print t3

    print t2.getRedexPositions()
    print t3.getRedexPositions()

    t4 = LambdaApp(t3, LambdaVar(1))

    print t4
    print t4.getRedexPositions()

    t5 = t4.substitute(t1, 0)

    print t5
    print t5.getRedexPositions()

    t6 = t5.reduce([1, 1, 2])

    print t6

    t7 = t6.reduce([1, 2])

    print t7

    t8 = t7.reduce([1, 2])

    print t8

    t9 = t8.reduce([1, 1])

    print t9
    print t9.getRedexPositions()

    print "Dictionary test:"

    x = LambdaVar(0)
    y = LambdaVar(0)
    z = LambdaVar(1)

    dictionary = {}

    dictionary[x] = 1

    print y in dictionary
    print z in dictionary
