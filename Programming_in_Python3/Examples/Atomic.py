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
Atomic is a context manager for mutable collections.

Atomic ensures that either all the changes are applied or none of them are
(i.e., in the face of an exception occurring). Atomic makes a private copy
of the collection (a deep copy if deep_copy is set True), so could be
expensive for large collections.

>>> items = list(range(10))
>>> try:
...     with Atomic(items) as atomic:
...         atomic.append(1999)
...         del atomic[3]
...         atomic[8] = -999
... except (AttributeError, IndexError, ValueError) as err:
...    pass
>>> items
[0, 1, 2, 4, 5, 6, 7, 8, -999, 1999]

>>> items = list(range(10))
>>> try:
...     with Atomic(items) as atomic:
...         atomic.append(10)
...         del atomic[3]
...         atomic[8] = -99
...         atomic.poop() # force failure
... except (AttributeError, IndexError, ValueError) as err:
...    pass
>>> items
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

>>> index = 19
>>> items = list(range(10))
>>> try:
...     with Atomic(items) as atomic:
...         atomic.append(58289)
...         del atomic[3]
...         atomic[8] = 81738
...         atomic[index] = 38172
... except (AttributeError, IndexError, ValueError) as err:
...    pass
>>> items
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

>>> items = set(range(10))
>>> try:
...     with Atomic(items) as atomic:
...         atomic.add(1999)
...         atomic.discard(3)
...         atomic |= {-999}
... except (AttributeError, IndexError, ValueError) as err:
...    pass
>>> list(sorted(items)), type(items) == type(set())
([-999, 0, 1, 2, 4, 5, 6, 7, 8, 9, 1999], True)

>>> items = set(range(10))
>>> try:
...     with Atomic(items) as atomic:
...         atomic.append(10)
...         atomic.discard(3)
...         atomic |= {-99}
...         atomic.poop() # force failure
... except (AttributeError, IndexError, ValueError) as err:
...    pass
>>> list(sorted(items)), type(items) == type(set())
([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], True)

>>> items = {chr(x): x for x in range(ord("A"), ord("E"))}
>>> try:
...     with Atomic(items) as atomic:
...         atomic["E"] = ord("E")
...         del atomic["B"]
... except (AttributeError, IndexError, ValueError) as err:
...    pass
>>> list(sorted(items.items())), type(items) == type({})
([('A', 65), ('C', 67), ('D', 68), ('E', 69)], True)

>>> items = {chr(x): x for x in range(ord("A"), ord("E"))}
>>> try:
...     with Atomic(items) as atomic:
...         atomic["E"] = ord("E")
...         del atomic["B"]
...         atomic.poop() # force failure
... except (AttributeError, IndexError, ValueError) as err:
...    pass
>>> list(sorted(items.items())), type(items) == type({})
([('A', 65), ('B', 66), ('C', 67), ('D', 68)], True)

>>> import abc
>>> import collections
>>> class A:
...     pass
>>> collections.MutableSet.register(A) # This class is lying about its API
>>> a = A()
>>> with Atomic(a) as atomic:
...     a.add(1)
Traceback (most recent call last):
...
AssertionError: Atomic mappings/sets must provide clear() and update()

>>> items = frozenset({1, 2, 3})
>>> with Atomic(items) as atomic:
...     a.add(1)
Traceback (most recent call last):
...
AssertionError: Atomic requires a mutable collection
"""

import collections
import copy


class Atomic:

    def __init__(self, container, deep_copy=False):
        assert (isinstance(container, collections.MutableSequence) or
                isinstance(container, collections.MutableSet) or
                isinstance(container, collections.MutableMapping)), (
                "Atomic requires a mutable collection")
        # if __debug__ ensures this is not executed when optimized with -O
        if (__debug__ and
            isinstance(container, collections.MutableSet) or
            isinstance(container, collections.MutableMapping)):
            assert (hasattr(container, "clear") and
                    hasattr(container, "update")), ("Atomic "
                    "mappings/sets must provide clear() and update()")
        self.original = container
        self.copy = copy.deepcopy if deep_copy else copy.copy


    def __enter__(self):
        self.modified = self.copy(self.original)
        return self.modified


    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            if isinstance(self.original, collections.MutableSequence):
                self.original[:] = self.modified
            elif (isinstance(self.original, collections.MutableSet) or
                  isinstance(self.original, collections.MutableMapping)):
                self.original.clear()
                self.original.update(self.modified)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
