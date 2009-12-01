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

    def isEqual(self, term):
        return False

    def copy(self):
        raise Exception("Not implemented")

    def toString(self):
        raise Exception("Not implemented")

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

    print t1.toString()

    t2 = t1.copy()

    print t1.isRedex()
    print ab.isRedex()

    print t1.isEqual(t2)

    t3 = LambdaApp(t1, t2)

    print t3.toString()

    print t2.getRedexPositions()
    print t3.getRedexPositions()

    t4 = LambdaApp(t3, LambdaVar(1))

    print t4.toString()
    print t4.getRedexPositions()
