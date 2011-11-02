X = 0
Y = 1

X1 = 0
Y1 = 1
X2 = 2
Y2 = 3

YERR = 2

EPSILON = 10e-4

def frange(*args):
    """A float range generator."""
    start = 0.0
    step = 1.0

    l = len(args)
    if l == 1:
        end = args[0]
    elif l == 2:
        start, end = args
    elif l == 3:
        start, end, step = args
        if step == 0.0:
            raise ValueError, "step must not be zero"
    else:
        raise TypeError, "frange expects 1-3 arguments, got %d" % l

    v = start
    while True:
        if (step > 0 and v >= end) or (step < 0 and v <= end):
            raise StopIteration
        yield v
        v += step

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def maximum(iterable, default=None):
    '''Like max(), but returns a default value if the iterable is empty.'''
    try:
        return max(iterable)
    except ValueError:
        return default

def minimum(iterable, default=None):
    '''Like min(), but returns a default value if the iterable is empty.'''
    try:
        return min(iterable)
    except ValueError:
        return default
