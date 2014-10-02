import unittest
from adt import ADT
from pypat import *

class TestADT(unittest.TestCase):
    def test_print(self):
        expr = ADT(name='expr')
        Abs = expr(str, expr, name='Abs')
        App = expr(expr, expr, name='App')
        Var = expr(str, name='Var')

        self.assertEqual('App(Abs(x, App(Var(x), Var(x))), Abs(x, App(Var(x), Var(x))))',
                         str(App(Abs('x', App(Var('x'), Var('x'))), 
                                 Abs('x', App(Var('x'), Var('x'))))))
        self.assertEqual('ADT expr = Abs(str, expr) | App(expr, expr) | Var(str)',
                         str(expr))

    def test_lambda(self):
        expr = ADT(name='expr')
        Abs = expr(str, expr, name='Abs')
        App = expr(expr, expr, name='App')
        Var = expr(str, name='Var')

        # Lambda calculus

        def pp(e):
            return match(e, 
                         (Var('x'), lambda x: x),
                         (Abs('x', 'e'), 
                                    lambda x,e: '(lambda %s: %s)' % (x, pp(e))),
                         (App('e1', 'e2'), 
                                    lambda e1,e2: '%s(%s)' % (pp(e1), pp(e2))))

        def is_val(e):
            return match(e, 
                  (Abs, lambda: True),
                  ('_',      lambda: False))
        def step(e):
            return match(e,
                         (App(Abs('x', 'e1'), 'e2'), 
                              Guard(lambda x,e1,e2: is_val(e2)),
                                    lambda x,e1,e2: subst(e1, x, e2)),
                         (App(As('e1', Abs), 'e2'), 
                                    lambda e1,e2: App(e1, step(e2))),
                         (App('e1', 'e2'), 
                                    lambda e1,e2: App(step(e1), e2)),
                         name='step')
        def subst(e, x, v):
            return match((e, x),
                         ((App('e1', 'e2'), '_'), 
                                    lambda e1,e2: App(subst(e1,x,v), subst(e2,x,v))),
                         ((As('e1',Abs('x', 'eb')), 'x'), 
                                    lambda e1,x,eb: e1),
                         ((Abs('y','e'), '_'), 
                                    lambda y,e: Abs(y,subst(e,x,v))),
                         ((Var('x'), 'x'), 
                                    lambda x: v),
                         ((Var('y'), '_'), 
                                    lambda y: Var(y)))
        def leval(e):
            return match(e,
                         ('_', Guard(lambda: is_val(e)), lambda: e),
                         ('_',                           lambda: leval(step(e))))

        plus = Abs('m', Abs('n', Abs('f', Abs('x',
                                              App(
                                                  App(Var('m'), Var('f')),
                                                  App(
                                                      App(Var('n'), Var('f')),
                                                      Var('x')))))))
        zero = Abs('f', Abs('x', Var('x')))
        one = Abs('f', Abs('x', App(Var('f'), Var('x'))))
        two = Abs('f', Abs('x', App(Var('f'),
                                    App(Var('f'), 
                                        Var('x')))))
        three = Abs('f', Abs('x', App(Var('f'), 
                                      App(Var('f'),
                                          App(Var('f'), 
                                              Var('x'))))))
        threeq = leval(App(App(plus, one), two))
        psucc = lambda x: x + 1

        self.assertEqual(
            eval(pp(three))(psucc)(0), 
            eval(pp(threeq))(psucc)(0))


if __name__ == '__main__':
    unittest.main()
    
