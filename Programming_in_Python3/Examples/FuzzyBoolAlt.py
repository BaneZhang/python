#!/usr/bin/env python3
# Copyright (c) 2008-11 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

"""
Implements an immutable FuzzyBool data type that can only have values in
the interval [0.0, 1.0] and which supports the basic logical operations
not (~), and (&), and or (|) using fuzzy logic.

Tests of inherited methods
>>> f = FuzzyBool()
>>> g = FuzzyBool(.5)
>>> h = FuzzyBool(3.75)
>>> print(f, g, h)
0.0 0.5 0.0
>>> h = ~h
>>> f = FuzzyBool(0.2)
>>> f < g
True
>>> h >= g
True
>>> f + g
Traceback (most recent call last):
...
TypeError: unsupported operand type(s) for +: 'FuzzyBool' and 'FuzzyBool'
>>> -f
Traceback (most recent call last):
...
TypeError: bad operand type for unary -: 'FuzzyBool'
>>> int(h), int(g), int(FuzzyBool(0.51))
(1, 0, 1)
>>> f = FuzzyBool(0.5)
>>> str(f)
'0.5'
"""


def conjunction(*fuzzies):
    """Returns the logical and of all the FuzzyBools

    >>> conjunction(FuzzyBool(0.5), FuzzyBool(0.6), 0.2, 0.125)
    FuzzyBool(0.125)
    """
    return FuzzyBool(min(fuzzies))


def disjunction(*fuzzies):
    """Returns the logical or of all the FuzzyBools

    >>> disjunction(FuzzyBool(0.5), FuzzyBool(0.75), 0.2, 0.1)
    FuzzyBool(0.75)
    """
    return FuzzyBool(max(fuzzies))


class FuzzyBool(float):

    def __new__(cls, value=0.0):
        """
        >>> f = FuzzyBool()
        >>> g = FuzzyBool(.5)
        >>> h = FuzzyBool(3.75)
        >>> f, g, h
        (FuzzyBool(0.0), FuzzyBool(0.5), FuzzyBool(0.0))
        """
        return super().__new__(cls,
                value if 0.0 <= value <= 1.0 else 0.0)


    def __invert__(self):
        """Returns the logical not of this FuzzyBool

        >>> f = FuzzyBool(0.125)
        >>> ~f
        FuzzyBool(0.875)
        >>> ~FuzzyBool()
        FuzzyBool(1.0)
        >>> ~FuzzyBool(1)
        FuzzyBool(0.0)
        """
        return FuzzyBool(1.0 - float(self))


    def __and__(self, other):
        """Returns the logical and of this FuzzyBool and the other one

        >>> FuzzyBool(0.5) & FuzzyBool(0.6)
        FuzzyBool(0.5)
        """
        return FuzzyBool(min(self, other))


    def __iand__(self, other):
        """Applies logical and to this FuzzyBool with the other one

        >>> f = FuzzyBool(0.5)
        >>> f &= FuzzyBool(0.6)
        >>> f
        FuzzyBool(0.5)
        """
        return FuzzyBool(min(self, other))


    def __or__(self, other):
        """Returns the logical or of this FuzzyBool and the other one

        >>> FuzzyBool(0.5) | FuzzyBool(0.75)
        FuzzyBool(0.75)
        """
        return FuzzyBool(max(self, other))


    def __ior__(self, other):
        """Applies logical or to this FuzzyBool with the other one

        >>> f = FuzzyBool(0.5)
        >>> f |= FuzzyBool(0.75)
        >>> f
        FuzzyBool(0.75)
        """
        return FuzzyBool(max(self, other))


    def __repr__(self):
        """
        >>> f = FuzzyBool(0.5)
        >>> repr(f)
        'FuzzyBool(0.5)'
        """
        return ("{0}({1})".format(self.__class__.__name__,
                                  super().__repr__()))


    def __bool__(self):
        """
        >>> f = FuzzyBool(.3)
        >>> g = FuzzyBool(.51)
        >>> bool(f), bool(g)
        (False, True)
        """
        return self > 0.5


    def __int__(self):
        """
        >>> f = FuzzyBool(.3)
        >>> g = FuzzyBool(.51)
        >>> int(f), int(g)
        (0, 1)
        """
        return round(self)


    for name, operator in (("__neg__", "-"),
                           ("__index__", "index()")):
        message = ("bad operand type for unary {0}: '{{self}}'"
                   .format(operator))
        exec("def {0}(self): raise TypeError(\"{1}\".format("
             "self=self.__class__.__name__))".format(name, message))

    for name, operator in (("__xor__", "^"), ("__ixor__", "^="),
            ("__add__", "+"), ("__iadd__", "+="), ("__radd__", "+"),
            ("__sub__", "-"), ("__isub__", "-="), ("__rsub__", "-"),
            ("__mul__", "*"), ("__imul__", "*="), ("__rmul__", "*"),
            ("__pow__", "**"), ("__ipow__", "**="),
            ("__rpow__", "**"), ("__floordiv__", "//"),
            ("__ifloordiv__", "//="), ("__rfloordiv__", "//"),
            ("__truediv__", "/"), ("__itruediv__", "/="),
            ("__rtruediv__", "/"), ("__divmod__", "divmod()"),
            ("__rdivmod__", "divmod()"), ("__mod__", "%"),
            ("__imod__", "%="), ("__rmod__", "%"),
            ("__lshift__", "<<"), ("__ilshift__", "<<="),
            ("__rlshift__", "<<"), ("__rshift__", ">>"),
            ("__irshift__", ">>="), ("__rrshift__", ">>")):
        message = ("unsupported operand type(s) for {0}: "
                   "'{{self}}'{{join}} {{args}}".format(operator))
        exec("def {0}(self, *args):\n"
             "    types = [\"'\" + arg.__class__.__name__ + \"'\" "
             "for arg in args]\n"
             "    raise TypeError(\"{1}\".format("
             "self=self.__class__.__name__, "
             "join=(\" and\" if len(args) == 1 else \",\"),"
             "args=\", \".join(types)))".format(name, message))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
