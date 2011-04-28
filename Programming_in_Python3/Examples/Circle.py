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
AA:
>>> circle = (11, 60, 8)

AB:
>>> circle = (8, 15, 3)
>>> distance = distance_from_origin(*circle[:2])
>>> distance
17.0
>>> distance = edge_distance_from_origin(*circle)
>>> distance
14.0

AC:
>>> import collections
>>> Circle = collections.namedtuple("Circle", "x y radius")
>>> circle = Circle(13, 84, 9)
>>> distance = distance_from_origin(circle.x, circle.y)

there's nothing to stop the data being invalid

AD:
>>> circle = Circle(33, 56, -5)
>>> distance = distance_from_origin(circle.x, circle.y)
>>> distance
65.0

>>> distance = edge_distance_from_origin(*circle)
Traceback (most recent call last):
...
AssertionError

# will be done in-place using: _replace() ?
AE:
>>> circle = circle._replace(radius=12)
>>> edge_distance_from_origin(*circle)
53.0

AF:
>>> circle = [36, 77, 8]
>>> circle.sort()
>>> circle
[8, 36, 77]

"""

import math


def distance_from_origin(x, y):
    return math.hypot(x, y)


def edge_distance_from_origin(x, y, radius):
    assert radius > 0
    return distance_from_origin(x, y) - radius


if __name__ == "__main__":
    import doctest
    doctest.testmod()
