from functools import reduce
import abc

class Matchable:
    @abc.abstractmethod
    def decompose(self):
        raise UnimplementedException('decompose unimplemented in class %s' % self.__class__)
    @classmethod
    @abc.abstractmethod
    def pattern(cls, *args):
        raise UnimplementedException('pattern unimplemented in class %s' % cls)
class PureMatchable(Matchable):
    def __new__(typ, *args, **kwargs):
        obj = super().__new__(typ)
        obj.__init__(*args, **kwargs)
        obj.decompose = lambda: ((obj.__class__,) + tuple(args))
        return obj
    def decompose(self):
        return self.decompose() # Looks stupid! But any instance of
                                # PureMatchable will have an object
                                # field of decompose
    @classmethod
    def pattern(cls, *args):
        return (cls,) + args

class PatternException(Exception):
    pass
class UnimplementedException(Exception):
    pass

class Guard:
    def __init__(self, guard):
        self.guard = guard
class Or:
    def __init__(self, pattern):
        self.pattern = pattern

class As:
    def __init__(self, bind, pattern):
        self.bind = bind
        self.pattern = pattern
class Literal:
    def __init__(self, lit):
        self.lit = lit
class PairList:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
class EmptyList:
    pass

def match(target, *cases):
    for pattern, *rest, action in cases:
        validate(rest, action)
        patterns = [pattern] + [p.pattern for p in rest if isinstance(p, Or)]
        guards = [g.guard for g in rest if isinstance(g, Guard)]
        
        for pattern in patterns:
            maps = casematch(target, pattern)
            if maps is not False and all(guard(**maps) for guard in guards):
                return action(**maps)

    raise PatternException('No pattern matches %s' % str(target))

def validate(rest,action):
    if not (callable(action) and \
            all((isinstance(r, Or) or isinstance(r, Guard)) for r in rest)):
        raise PatternException('Malformed pattern')

def merge_maps(m1, m2):
    mf = {}
    if m1 is False or m2 is False:
        return False
    for k in m1:
        if k in m2:
            if m1[k] == m2[k]:
                mf[k] = m1[k]
            else: return False
        else: mf[k] = m1[k]
    for k in m2:
        if k not in m1:
            mf[k] = m2[k]
    return mf

def casematch(target, pattern):
    if pattern == '_':
        return {}
    elif isinstance(pattern, str):
        return {pattern: target}
    elif isinstance(target, Literal):
        return casematch(target.lit, pattern)
    elif isinstance(pattern, Literal) and pattern.lit == target:
        return {}
    elif isinstance(pattern, PairList) and isinstance(target, list) and len(target) > 0:
        return merge_maps(casematch(target[0], pattern.head),
                          casematch(target[1:], pattern.tail))
    elif isinstance(pattern, EmptyList) and target == []:
        return {}
    elif isinstance(pattern, As):
        return merge_maps(casematch(target, pattern.pattern), {pattern.bind: target})
    elif isinstance(pattern, type) and isinstance(target, pattern):
        return {}
    elif isinstance(target, Matchable):
        return casematch(target.decompose(), pattern)
    elif isinstance(pattern, PureMatchable):
        return casematch(target, pattern.decompose())
    elif isinstance(pattern, tuple) and isinstance(target, tuple) and \
         len(pattern) == len(target):
        return reduce(merge_maps, (casematch(t,p) for t,p in zip(target,pattern)), {})
    elif pattern == target:
        return {}
    return False
    
def matchable(*data):
    def parse_patterns_and_guards(data):
        pattern = ()
        rest = ()
        top = True
        for elt in data:
            if isinstance(elt, Guard) or isinstance(elt, Or):
                top = False
                rest += (elt,)
            elif top:
                pattern += (elt,)
            else: raise PatternException('Malformed pattern')
        return pattern, rest
    def owrap(fun):
        def wrap(*args):
            return match(args, *wrap.cases)
        pattern, rest = parse_patterns_and_guards(data)
        wrap.cases = [((pattern,) + rest + (fun,))]
        def case(*data):
            pattern, rest = parse_patterns_and_guards(data)
            def cwrap(cfun):
                wrap.cases.append((pattern,) + rest + (cfun,))
                return wrap
            return cwrap
        wrap.case = case
        return wrap
    return owrap
