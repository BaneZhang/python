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

class Const:

    """
    >>> const = Const()
    >>> const.text = "verified"
    >>> const.limit = 591
    >>> const.text, const.limit
    ('verified', 591)
    >>> const.limit -= 12
    Traceback (most recent call last):
    ...
    ValueError: cannot change a const attribute
    >>> const.x
    Traceback (most recent call last):
    ...
    AttributeError: 'Const' object has no attribute 'x'
    >>> del const.text
    Traceback (most recent call last):
    ...
    ValueError: cannot delete a const attribute
    >>> del const.x
    Traceback (most recent call last):
    ...
    AttributeError: 'Const' object has no attribute 'x'
    """

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise ValueError("cannot change a const attribute")
        self.__dict__[name] = value


    def __delattr__(self, name):
        if name in self.__dict__:
            raise ValueError("cannot delete a const attribute")
        raise AttributeError("'{0}' object has no attribute '{1}'"
                             .format(self.__class__.__name__, name))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
