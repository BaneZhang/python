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

>>> f = FuzzyBool()
>>> g = FuzzyBool(.5)
>>> h = FuzzyBool(3.75)
>>> f, g, h
(FuzzyBool(0.0), FuzzyBool(0.5), FuzzyBool(0.0))
>>> h = ~h
>>> print(f, g, h)
0.0 0.5 1.0
>>> f = FuzzyBool(0.2)
>>> f < g
True
>>> h >= g
True
>>> f + g
Traceback (most recent call last):
...
TypeError: unsupported operand type(s) for +: 'FuzzyBool' and 'FuzzyBool'
>>> int(h), int(g)
(1, 0)
>>> d = {f : 1, g : 2, h : 3}
>>> d[g]
2
"""

import Util


@Util.complete_comparisons
class FuzzyBool:

    def __init__(self, value=0.0):
        """
        >>> f = FuzzyBool()
        >>> g = FuzzyBool(.5)
        >>> h = FuzzyBool(3.75)
        >>> f, g, h
        (FuzzyBool(0.0), FuzzyBool(0.5), FuzzyBool(0.0))
        """
        self.__value = value if 0.0 <= value <= 1.0 else 0.0


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
        return FuzzyBool(1.0 - self.__value)


    def __and__(self, other):
        """Returns the logical and of this FuzzyBool and the other one

        >>> FuzzyBool(0.5) & FuzzyBool(0.6)
        FuzzyBool(0.5)
        """
        return FuzzyBool(min(self.__value, other.__value))


    def __iand__(self, other):
        """Applies logical and to this FuzzyBool with the other one

        >>> f = FuzzyBool(0.5)
        >>> f &= FuzzyBool(0.6)
        >>> f
        FuzzyBool(0.5)
        """
        self.__value = min(self.__value, other.__value)
        return self


    @staticmethod
    def conjunction(*fuzzies):
        """Returns the logical and of all the FuzzyBools

        >>> FuzzyBool.conjunction(FuzzyBool(0.5), FuzzyBool(0.6), 0.2, 0.125)
        FuzzyBool(0.125)
        """
        return FuzzyBool(min([float(x) for x in fuzzies]))


    def __or__(self, other):
        """Returns the logical or of this FuzzyBool and the other one

        >>> FuzzyBool(0.5) | FuzzyBool(0.75)
        FuzzyBool(0.75)
        """
        return FuzzyBool(max(self.__value, other.__value))


    def __ior__(self, other):
        """Applies logical or to this FuzzyBool with the other one

        >>> f = FuzzyBool(0.5)
        >>> f |= FuzzyBool(0.75)
        >>> f
        FuzzyBool(0.75)
        """
        self.__value = max(self.__value, other.__value)
        return self


    @staticmethod
    def disjunction(*fuzzies):
        """Returns the logical or of all the FuzzyBools

        >>> FuzzyBool.disjunction(FuzzyBool(0.5), FuzzyBool(0.75), 0.2, 0.1)
        FuzzyBool(0.75)
        """
        return FuzzyBool(max([float(x) for x in fuzzies]))


    def __repr__(self):
        """
        >>> f = FuzzyBool(0.5)
        >>> repr(f)
        'FuzzyBool(0.5)'
        """
        return ("{0}({1})".format(self.__class__.__name__,
                                  self.__value))


    def __str__(self):
        """
        >>> f = FuzzyBool(0.5)
        >>> str(f)
        '0.5'
        """
        return str(self.__value)


    def __bool__(self):
        """
        >>> f = FuzzyBool(.3)
        >>> g = FuzzyBool(.51)
        >>> bool(f), bool(g)
        (False, True)
        """
        return self.__value > 0.5


    def __int__(self):
        return round(self.__value)


    def __float__(self):
        return self.__value


    def __lt__(self, other):
        return self.__value < other.__value


    def __eq__(self, other):
        return self.__value == other.__value


    def __hash__(self):
        return hash(id(self))


    def __format__(self, format_spec):
        """
        >>> f = FuzzyBool(.875)
        >>> "{0:.0%}".format(f)
        '88%'
        >>> "{0:.1%}".format(f)
        '87.5%'
        """
        return format(self.__value, format_spec)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
