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
>>> L = SortedList((5, 8, -1, 3, 4, 22))
>>> L[2] = 18 #doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
...
TypeError: use add() to insert a value and rely on the...
>>> list(L)
[-1, 3, 4, 5, 8, 22]
>>> L.add(5)
>>> L.add(5)
>>> L.add(6)
>>> list(L)
[-1, 3, 4, 5, 5, 5, 6, 8, 22]
>>> L.index(4)
2
>>> L.count(5), L.count(2)
(3, 0)
>>> L.insert(2, 9)
Traceback (most recent call last):
...
AttributeError: 'SortedList' object has no attribute 'insert'
>>> L.reverse()
Traceback (most recent call last):
...
AttributeError: 'SortedList' object has no attribute 'reverse'
>>> L.sort()
Traceback (most recent call last):
...
AttributeError: 'SortedList' object has no attribute 'sort'

>>> import collections
>>> isinstance(L, collections.Sequence)
False
"""

_identity = lambda x: x


class SortedList:

    def __init__(self, sequence=None, key=None):
        """Creates a SortedList that orders using < on the items,
        or on the results of using the given key function

        >>> L = SortedList()
        >>> print(L)
        []
        >>> L = SortedList((5, 8, -1, 3, 4, 22))
        >>> print(L)
        [-1, 3, 4, 5, 8, 22]
        >>> L = SortedList({9, 8, 7, 6, -1, -2})
        >>> print(L)
        [-2, -1, 6, 7, 8, 9]
        >>> L = SortedList([-5, 4, -3, 8, -2, 16, -1, 0, -3, 8])
        >>> print(L)
        [-5, -3, -3, -2, -1, 0, 4, 8, 8, 16]
        >>> L2 = SortedList(L)
        >>> print(L2)
        [-5, -3, -3, -2, -1, 0, 4, 8, 8, 16]
        >>> L = SortedList(("the", "quick", "brown", "fox", "jumped"))
        >>> print(L)
        ['brown', 'fox', 'jumped', 'quick', 'the']
        """
        self.__key = key or _identity
        assert hasattr(self.__key, "__call__")
        if sequence is None:
            self.__list = []
        elif (isinstance(sequence, SortedList) and
              sequence.key == self.__key):
            self.__list = sequence.__list[:]
        else:
            self.__list = sorted(list(sequence), key=self.__key)


    @property
    def key(self):
        """Return the key function used by this list
        """
        return self.__key


    def clear(self):
        """Clears the list

        >>> L = SortedList((5, 8, -1, 3, 4, 22))
        >>> print(L)
        [-1, 3, 4, 5, 8, 22]
        >>> L.clear()
        >>> print(L)
        []
        """
        self.__list = []


    def __bisect_left(self, value):
        """Returns value's key and its index position in the list
        (or where value belongs if it isn't in the list)
        """
        key = self.__key(value)
        left, right = 0, len(self.__list)
        while left < right:
            middle = (left + right) // 2
            if self.__key(self.__list[middle]) < key:
                left = middle + 1
            else:
                right = middle
        return key, left


    def add(self, value):
        """Adds a value to the list (duplicates are allowed)

        >>> L = SortedList((5, 8, -1, 3, 4, 22))
        >>> print(L)
        [-1, 3, 4, 5, 8, 22]
        >>> L.add(5)
        >>> L.add(5)
        >>> L.add(7)
        >>> L.add(-18)
        >>> L.add(99)
        >>> print(L)
        [-18, -1, 3, 4, 5, 5, 5, 7, 8, 22, 99]
        """
        index = self.__bisect_left(value)[1]
        if index == len(self.__list):
            self.__list.append(value)
        else:
            self.__list.insert(index, value)


    def pop(self, index=-1):
        """Removes and returns the item the given index

        >>> L = SortedList([-18, -1, 3, 4, 5, 5, 7, 8, 22, 99])
        >>> print(L)
        [-18, -1, 3, 4, 5, 5, 7, 8, 22, 99]
        >>> L.pop()
        99
        >>> L.pop(0)
        -18
        >>> L.pop(5)
        7
        >>> print(L)
        [-1, 3, 4, 5, 5, 8, 22]
        >>> L.pop(12)
        Traceback (most recent call last):
        ...
        IndexError: pop index out of range
        """
        return self.__list.pop(index)


    def remove(self, value):
        """Removes the first occurrence of value from the list

        >>> L = SortedList([-18, -1, 3, 4, 5, 5, 7, 8, 22, 99])
        >>> print(L)
        [-18, -1, 3, 4, 5, 5, 7, 8, 22, 99]
        >>> L.remove(20)
        Traceback (most recent call last):
        ...
        ValueError: SortedList.remove(x): x not in list
        >>> L.remove(5)
        >>> L.remove(-18)
        >>> L.remove(99)
        >>> print(L)
        [-1, 3, 4, 5, 7, 8, 22]
        >>> L = SortedList(["ABC", "X", "abc", "Abc"], lambda x: x.lower())
        >>> print(L)
        ['ABC', 'abc', 'Abc', 'X']
        >>> L.remove("Abca")
        Traceback (most recent call last):
        ...
        ValueError: SortedList.remove(x): x not in list
        >>> print(L)
        ['ABC', 'abc', 'Abc', 'X']
        >>> L.remove("Abc")
        >>> print(L)
        ['ABC', 'abc', 'X']
        >>> L.remove("ABC")
        >>> print(L)
        ['abc', 'X']
        >>> L.remove("X")
        >>> print(L)
        ['abc']
        >>> L.remove("abc")
        >>> print(L)
        []
        """
        key, index = self.__bisect_left(value)
        while (index < len(self.__list) and
                self.__key(self.__list[index]) == key):
            if self.__list[index] == value:
                del self.__list[index]
                return
            index += 1
        raise ValueError("{0}.remove(x): x not in list".format(
                            self.__class__.__name__))


    def remove_every(self, value):
        """Removes every occurrence of value from the list

        Returns the number of occurrences removed (which could be 0).
        >>> L = SortedList([5, 5, -18, -1, 3, 4, 5, 5, 7, 8, 22, 99])
        >>> L.add(5)
        >>> L.add(5)
        >>> print(L)
        [-18, -1, 3, 4, 5, 5, 5, 5, 5, 5, 7, 8, 22, 99]
        >>> L.remove_every(-3)
        0
        >>> L.remove_every(7)
        1
        >>> L.remove_every(5)
        6
        >>> print(L)
        [-18, -1, 3, 4, 8, 22, 99]
        >>> L = SortedList(["ABC", "X", "abc", "Abc"], lambda x: x.lower())
        >>> L.remove_every("abc")
        3
        """
        count = 0
        key, index = self.__bisect_left(value)
        while (index < len(self.__list) and
               self.__key(self.__list[index]) == key):
            del self.__list[index]
            count += 1
        return count


    def count(self, value):
        """Counts every occurrence of value in the list

        >>> L = SortedList([5, 5, -18, -1, 3, 4, 5, 5, 7, 8, 22, 99])
        >>> L.count(5)
        4
        >>> L.count(99)
        1
        >>> L.count(-17)
        0
        >>> L = SortedList(["ABC", "X", "abc", "Abc"], lambda x: x.lower())
        >>> L.count("abc")
        3
        """
        count = 0
        key, index = self.__bisect_left(value)
        while (index < len(self.__list) and
               self.__key(self.__list[index]) == key):
            index += 1
            count += 1
        return count


    def index(self, value):
        """Returns the index position of the first occurrence of value

        >>> L = SortedList([5, 5, -18, -1, 3, 4, 7, 8, 22, 99, 2, 1, 3])
        >>> L.index(5)
        7
        >>> L.index(0)
        Traceback (most recent call last):
        ...
        ValueError: SortedList.index(x): x not in list
        >>> L.index(99)
        12
        >>> L = SortedList(["ABC", "X", "abc", "Abc"], lambda x: x.lower())
        >>> print(L)
        ['ABC', 'abc', 'Abc', 'X']
        >>> L.index("x")
        3
        >>> L.index("abc")
        0
        """
        key, index = self.__bisect_left(value)
        if (index < len(self.__list) and
            self.__key(self.__list[index]) == key):
            return index
        raise ValueError("{0}.index(x): x not in list".format(
                         self.__class__.__name__))


    def __delitem__(self, index):
        """Deletes the value at the given index position

        >>> L = SortedList([9, -5, 3, -7, 8, 14, 0, 8, 3])
        >>> print(L)
        [-7, -5, 0, 3, 3, 8, 8, 9, 14]
        >>> del L[0]
        >>> del L[-1]
        >>> del L[5]
        >>> print(L)
        [-5, 0, 3, 3, 8, 9]
        >>> del L[25]
        Traceback (most recent call last):
        ...
        IndexError: list assignment index out of range
        >>> del L[-3:]
        >>> print(L)
        [-5, 0, 3]
        """
        del self.__list[index]
        

    def __getitem__(self, index):
        """Returns the value at the given index position

        >>> L = SortedList([9, -5, 3, -7, 8, 14, 0, 8, 3])
        >>> L[0], L[3], L[4], L[-1]
        (-7, 3, 3, 14)
        >>> L[15]
        Traceback (most recent call last):
        ...
        IndexError: list index out of range
        >>> L[:3]
        [-7, -5, 0]
        >>> L[4:8]
        [3, 8, 8, 9]
        """
        return self.__list[index]


    def __setitem__(self, index, value):
        raise TypeError("use add() to insert a value and rely on "
                        "the list to put it in the right place")


    def __iter__(self):
        """Returns an iterator for the list

        >>> L = SortedList([5, 5, -18, -1, 3, 4, 7, 8, 22, 99, 2, 1, 3])
        >>> result = []
        >>> for x in L:
        ...     result.append(x)
        >>> print(result)
        [-18, -1, 1, 2, 3, 3, 4, 5, 5, 7, 8, 22, 99]
        """
        return iter(self.__list)


    def __reversed__(self):
        """Returns a reverse iterator for the list

        >>> L = SortedList([5, 5, -18, -1, 3, 4, 7, 8, 22, 99, 2, 1, 3])
        >>> result = []
        >>> for x in reversed(L):
        ...     result.append(x)
        >>> print(result)
        [99, 22, 8, 7, 5, 5, 4, 3, 3, 2, 1, -1, -18]
        """
        return reversed(self.__list)


    def __contains__(self, value):
        """Returns True if value is in the list; otherwise returns False

        >>> L = SortedList([5, 5, -18, -1, 3, 4, 7, 8, 22, 99, 2, 1, 3])
        >>> 5 in L
        True
        >>> 0 in L
        False
        >>> 99 in L
        True
        >>> L = SortedList(["ABC", "X", "Abc"], lambda x: x.lower())
        >>> "abc" in L
        True
        >>> "x" in L
        True
        >>> "ZZ" in L
        False
        """
        key, index = self.__bisect_left(value)
        return (index < len(self.__list) and
                self.__key(self.__list[index]) == key)


    def __len__(self):
        """Returns the length of the list

        >>> L = SortedList([5, 5, -18, -1, 3, 4, 7, 8, 22, 99, 2, 1, 3])
        >>> len(L)
        13
        >>> L = SortedList()
        >>> len(L)
        0
        """
        return len(self.__list)


    def __str__(self):
        """Returns a human readable string version of the list; the
        result could be very long

        >>> L = SortedList([-1, 3, 4, 7, 8, 22, -9, 2, 1, 3])
        >>> str(L)
        '[-9, -1, 1, 2, 3, 3, 4, 7, 8, 22]'
        >>> L = SortedList()
        >>> str(L)
        '[]'
        >>> L = SortedList(("the", "quick", "brown", "fox", "jumped"))
        >>> str(L)
        "['brown', 'fox', 'jumped', 'quick', 'the']"
        """
        return str(self.__list)


    def copy(self):
        """Returns a shallow copy of the list with the same key function
        >>> L = SortedList([-1, 3, 4, 7, 8, 22, -9, 2, 1, 3])
        >>> m = L.copy()
        >>> str(m)
        '[-9, -1, 1, 2, 3, 3, 4, 7, 8, 22]'
        >>> m[:]
        [-9, -1, 1, 2, 3, 3, 4, 7, 8, 22]
        >>> import copy
        >>> n = copy.copy(L)
        >>> str(n)
        '[-9, -1, 1, 2, 3, 3, 4, 7, 8, 22]'
        """
        return SortedList(self, self.__key)
        
    __copy__ = copy

if __name__ == "__main__":
    import doctest
    doctest.testmod()
