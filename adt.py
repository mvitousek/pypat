from pypat import PureMatchable

class ADTException(Exception): pass

def ADT(name='ADT'):
    class _ADT(PureMatchable):
        def __init__(self):
            self.insts = []
            self.__name__ = name
        def __call__(self, *targs, name='ADTInst'):
            class _ADTInst(_ADT):
                def __init__(self, *args):
                    if len(args) != len(targs):
                        raise ADTException('Incorrect number of arguments to ADT constructor')
                    self.args = args
                def __str__(self):
                    return '%s(%s)' % (self.__class__.__name__, ', '.join(str(x) for x in self.args))
            _ADTInst.__name__ = name
            self.insts.append(_ADTInst(*(x.__name__ for x in targs)))
            return _ADTInst
        def __str__(self):
            return 'ADT %s = %s' % (self.__class__.__name__, ' | '.join(str(x) for x in self.insts))
    _ADT.__name__ = name
    return _ADT()
