import unittest
from pypat import *

class TestExamples(unittest.TestCase):

    # Matching against literal values
    def test_literal(self):
        result = match(42,
                       (234, lambda: False),
                       (True, lambda: False),
                       (42, lambda: True))
        self.assertTrue(result)

    # If no case matches, a PatternException is thrown
    def test_fail(self):
        thunk = lambda: match(999,
                              (234, lambda: False),
                              (True, lambda: False),
                              (42, lambda: True))
        self.assertRaises(PatternException, thunk)

    # Special case: if you want to match against string literals in
    # patterns, you must wrap it in a Literal object (to disambiguate
    # from variable bindings, as shown later)
    def test_explicitliteral1(self):
        result = match('hello world',
                       (Literal('hello world'), lambda: True),
                       (42, lambda: False))
        self.assertTrue(result)

    def test_explicitliteral2(self):
        result = match(42,
                       (Literal('hello world'), lambda: True),
                       (42, lambda: False))
        self.assertFalse(result)

    # Strings that are not wrapped in Literal are variables. The
    # pattern's action function expects parameters with the same names
    # as the variables in the pattern. Variables match anything.
    def test_variables(self):
        class Arbitrary(object):
            def __eq__(self, other):
                return self.__class__ == other.__class__
        result = match(Arbitrary(),
                       (42, lambda: False),
                       ('x', lambda x: x))
        self.assertEqual(result, Arbitrary())

    # If you want to match against any value without binding it to a
    # variable, use the '_' symbol (in a string).
    def test_any(self):
        result = match(4545,
                       (42, lambda: False),
                       (10101, lambda: False),
                       ('_', lambda: True))
        self.assertTrue(result)

    # You can also add guards to cases. The guard is an instance of
    # type Guard, which takes a function, which itself takes variables
    # introduced in its pattern. The guard can go in between the
    # pattern and the action function of the case.
    def test_guards(self):
        result = match('hello world',
                       ('x', Guard(lambda x: isinstance(x, int)), lambda x: x * x),
                       ('x', Guard(lambda x: isinstance(x, str)), lambda x: x))
        self.assertEqual(result, 'hello world')

    # You can match against tuples by putting tuples in your
    # patterns. Tuples can contain any pattern, and variables will be
    # bound appropriately.
    def test_tuple(self):
        def arith(*op):
            return match(op,
                         ((Literal('+'), 'x', 'y'), lambda x, y: x + y),
                         ((Literal('*'), 'x', 'y'), lambda x, y: x * y),
                         ((Literal('pred'), 'x'), lambda x: x - 1))
        self.assertEqual(arith('*', 4, 5), 20)
        self.assertEqual(arith('+', 39, 3), 42)
        self.assertEqual(arith('pred', 4), 3)

    # If the same variable appears more than once in a pattern, it has
    # to be bound to the same value each time for the pattern to match
    def test_multi(self):
        def eq(v1, v2):
            return match((v1, v2),
                         (('x', 'x'), lambda x: True),
                         (('x', 'y'), lambda x,y: False))
        self.assertTrue(eq(3,3))
        self.assertFalse(eq(2,5))

    # If the same action (and variable bindings) will be used for
    # multiple cases, you can add additional patterns to a case with
    # the Or class, which takes a pattern.
    def test_ors(self):
        def timesWillEqZero(n1, n2):
            return match((n1, n2),
                         ((0, 'x'), Or(('x', 0)), lambda x: True),
                         ('_', lambda: False))
        self.assertTrue(timesWillEqZero(0, 43))
        self.assertTrue(timesWillEqZero(42, 0))
        self.assertFalse(timesWillEqZero(42, 2))

    # Lists can be matched against using the PairList and EmptyList
    # classes. PairLists are nonempty lists that have a head and a
    # tail, and EmptyLists are empty lists.
    def test_list(self):
        def mmap(op, lst):
            return match(lst,
                         (PairList('x', 'xs'), lambda x, xs: [op(x)] + mmap(op, xs)),
                         (EmptyList(), lambda: []))
        self.assertEqual(mmap((lambda x: x * x), [1,2,3,4]), [1,4,9,16])

    # You can match based on the runtime type of a matched value by
    # putting types in the patterns.
    def test_types(self):
        result = match('hello world',
                       (int, lambda: False),
                       (str, lambda: True))
        self.assertTrue(result)

    # If you want to bind the target (or a portion of it) to a
    # variable, but you also want to pattern match on something deeper
    # in the target, you can use the As class to do both:
    def test_as(self):
        def expr(*op):
            return match(op,
                         ((Literal('+'), As('x', int), As('y', int)), lambda x, y: x + y),
                         ((Literal('or'), As('x', bool), As('y', bool)), lambda x, y: x or y))
        self.assertEqual(expr('or', True, False), True)
        self.assertEqual(expr('+', 39, 3), 42)
        self.assertRaises(PatternException, lambda: expr('or', 1, 2))

    def test_deepas(self):
        result = match([1,2,3],
                       (PairList('_', As('r', PairList(As('x', int),'_'))),
                        lambda x,r: '%s is in %s' % (x,r)))
        self.assertEqual(result, '2 is in [2, 3]')

    # Objects that do not perform any kind of input checking can be
    # subclassed from PureMatchable and then used as patterns.
    def test_purematch1(self):
        class C(PureMatchable):
            def __init__(self, a, b, c):
                pass
        self.assertEqual(match(C(1,2,'3'),
                               (C(3,'b','c'), lambda b,c: b),
                               (C('a','b',Literal('3')), lambda a,b: a),
                               (C('a','b','c'), lambda a,b,c: c),
                               ('_', lambda: None)),
                         1)

    def test_purematch2(self):
        class Expr(PureMatchable):
            pass
        class Add(Expr):
            def __init__(self, rand1, rand2):
                pass                
        class Mult(Expr):
            def __init__(self, rand1, rand2):
                pass
        class Num(Expr):
            def __init__(self, n):
                pass
        def step(expr):
            return match(expr,
                         (Add(Num('n1'), Num('n2')), 
                          lambda n1, n2: Num(n1 + n2)),
                         (Add(Num('n1'), 'n2'), 
                          lambda n1, n2: Add(Num(n1), step(n2))),
                         (Add('n1', 'n2'), 
                          lambda n1, n2: Add(step(n1), n2)),
                         (Mult(Num('n1'), Num('n2')), 
                          lambda n1, n2: Num(n1 * n2)),
                         (Mult(Num('n1'), 'n2'), 
                          lambda n1, n2: Mult(Num(n1), step(n2))),
                         (Mult('n1', 'n2'), 
                          lambda n1, n2: Mult(step(n1), n2)))
        def eval(expr):
            return match(expr,
                         (Num('n'), lambda n: n),
                         ('e', lambda e: eval(step(e))))
        self.assertEqual(eval(Add(Mult(Num(4), Num(2)), Add(Num(1), Add(Num(0), Num(1))))),
                         10)

    # Objects that can't be PureMatchable (because, for example, they
    # sanitize inputs, or it makes sense to decompose them into
    # something other than their constructor's arguments) can subclass
    # from Matchable, and implement pattern() (which is a class
    # method) and decompose(). decompose() returns the decomposition
    # of the object, which can be anything the user desires as long as
    # it is a valid match target. pattern() should take patterns and
    # return them in such a way that they can match decompose()
    # (including caveats like strings needing to be in
    # Literal). [CLASS].pattern() should then be used in lieu of the
    # classname alone.
    def test_matchable(self):
        class Summer(Matchable):
            def __init__(self, *nums):
                self.sum = sum(nums)
            def decompose(self):
                return ('SUM', self.sum)
            @classmethod
            def pattern(cls, pat):
                return (Literal('SUM'), pat)
        result = match(Summer(1,2,3,4,5),
                       (Summer.pattern(54), lambda: False),
                       (Summer.pattern(As('x', int)), lambda x: x))
        self.assertEqual(result, 15)


    # Functions can be defined as part of a match pattern with the
    # @matchable decorator, and the @[FUN].case decorator (where fun
    # is the name of the actual partially specified function)
    def test_sepdef1(self):
        @matchable(1)
        def factorial():
            return 1
        @factorial.case(0)
        def factorial():
            return 0
        @factorial.case(As('n',int), Guard(lambda n: n > 1))
        def factorial(n):
            return factorial(n-1) * n
        
        self.assertEqual(factorial(5), 120)
        self.assertRaises(PatternException, lambda: factorial(-5))

    def test_sepdef2(self):
        @matchable(As('x',Literal('Dog.')))
        def foo(x):
            return x

        @foo.case(42)
        def foo():
            return 'it\'s 42!!'

        @foo.case('a', int)
        def foo(a):
            return 'cdrnum'

        @foo.case()
        def foo():
            return 'EMPTY'

        self.assertEqual(foo(42), 'it\'s 42!!')
        self.assertEqual(foo(3,2), 'cdrnum')
        self.assertEqual(foo('Dog.'), 'Dog.')
        self.assertEqual(foo(), 'EMPTY')
        self.assertRaises(PatternException, lambda: foo(3,'a'))
        self.assertRaises(PatternException, lambda: foo(22))

    # Match object can be built and cases added to them.
    def test_matchobj(self):
        matcher = Match([(42, lambda: 'yes')])
        matcher.add('x', Guard(lambda x: isinstance(x, int)), lambda x: x)
        matcher.add(('x', 'y'), lambda x,y: x + y)

        self.assertEqual(matcher(42), 'yes')
        self.assertEqual(matcher(120), 120)
        self.assertEqual(matcher((1,2)), 3)
        self.assertRaises(PatternException, lambda: matcher('bluh'))

        matcher.add('_', lambda: 'miss')
        self.assertEqual(matcher('bluh'), 'miss')


    # Lambda calculus
    class LC(PureMatchable):
        pass
    class Abs(LC):
        def __init__(self, x, e): pass
    class App(LC):
        def __init__(self, e1, e2): pass
    class Var(LC):
        def __init__(self, x): pass

    def pp(self, e):
        return match(e, 
                     (self.Var('x'), 
                                lambda x: x),
                     (self.Abs('x', 'e'), 
                                lambda x,e: '(lambda %s: %s)' % (x, self.pp(e))),
                     (self.App('e1', 'e2'), 
                                lambda e1,e2: '%s(%s)' % (self.pp(e1), self.pp(e2))))

    def is_val(self, e):
        return match(e, 
              (self.Abs, lambda: True),
              ('_',      lambda: False))
    def step(self, e):
        return match(e,
                     (self.App(self.Abs('x', 'e1'), 'e2'), 
                          Guard(lambda x,e1,e2: self.is_val(e2)),
                                lambda x,e1,e2: self.subst(e1, x, e2)),
                     (self.App(As('e1', self.Abs), 'e2'), 
                                lambda e1,e2: self.App(e1, self.step(e2))),
                     (self.App('e1', 'e2'), 
                                lambda e1,e2: self.App(self.step(e1), e2)))
    def subst(self, e, x, v):
        return match((e, x),
                     ((self.App('e1', 'e2'), '_'), 
                                lambda e1,e2: self.App(self.subst(e1,x,v), self.subst(e2,x,v))),
                     ((As('e1',self.Abs('x', 'eb')), 'x'), 
                                lambda e1,x,eb: e1),
                     ((self.Abs('y','e'), '_'), 
                                lambda y,e: self.Abs(y,self.subst(e,x,v))),
                     ((self.Var('x'), 'x'), 
                                lambda x: v),
                     ((self.Var('y'), '_'), 
                                lambda y: self.Var(y)))
    def eval(self, e):
        return match(e,
                     ('_', Guard(lambda: self.is_val(e)), lambda: e),
                     ('_',                                lambda: self.eval(self.step(e))))

    def test_lambda(self):
        plus = self.Abs('m', self.Abs('n', self.Abs('f', self.Abs('x',
                                              self.App(
                                                  self.App(self.Var('m'), self.Var('f')),
                                                  self.App(
                                                      self.App(self.Var('n'), self.Var('f')),
                                                      self.Var('x')))))))
        zero = self.Abs('f', self.Abs('x', self.Var('x')))
        one = self.Abs('f', self.Abs('x', self.App(self.Var('f'), self.Var('x'))))
        two = self.Abs('f', self.Abs('x', self.App(self.Var('f'),
                                                   self.App(self.Var('f'), 
                                                            self.Var('x')))))
        three = self.Abs('f', self.Abs('x', self.App(self.Var('f'), 
                                                     self.App(self.Var('f'),
                                                              self.App(self.Var('f'), 
                                                                       self.Var('x'))))))
        threeq = self.eval(self.App(self.App(plus, one), two))
        psucc = lambda x: x + 1

        self.assertEqual(
            eval(self.pp(three))(psucc)(0), 
            eval(self.pp(threeq))(psucc)(0))
                               
if __name__ == '__main__':
    unittest.main()
    
