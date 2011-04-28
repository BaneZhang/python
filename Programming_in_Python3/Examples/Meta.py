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
>>> point = Point(-17, 9181)
>>> point.x, point.y        # returns: (0, 1024)
(0, 1024)
>>> point.x = -8
>>> point.y = 3918
>>> point.x, point.y        # returns: (0, 1024)
(0, 1024)
>>> point = Point(91, 181)
>>> point.x, point.y        # returns: (91, 181)
(91, 181)
>>> point.x *= 2
>>> point.y //= 3
>>> point.x, point.y        # returns: (182, 60)
(182, 60)

BE:
>>> product = Product("101110110", "8mm Stapler")
>>> product.barcode, product.description
('101110110', '8mm Stapler')
>>> product.barcode = "XXX"
Traceback (most recent call last):
...
AttributeError: can't set attribute

BF:
>>> product.description = "8mm Stapler (long)"
>>> product.barcode, product.description
('101110110', '8mm Stapler (long)')

>>> point = PointA(-17, 9181, -18)
>>> point.x, point.y        # returns: (0, 1024)
(0, 1024)
>>> point.x = -8
>>> point.y = 3918
>>> point.x, point.y        # returns: (0, 1024)
(0, 1024)
>>> point.a
-18
>>> point.a = 7
>>> point.a
7
>>> point = Point(91, 181)
>>> point.x, point.y        # returns: (91, 181)
(91, 181)
>>> point.x *= 2
>>> point.y //= 3
>>> point.x, point.y        # returns: (182, 60)
(182, 60)

"""

import abc
import collections


class LoadableSaveable(type):

    def __init__(cls, classname, bases, dictionary):
        super().__init__(classname, bases, dictionary)
        assert hasattr(cls, "load") and \
               isinstance(getattr(cls, "load"),
                          collections.Callable), ("class '" +
               classname + "' must provide a load() method")
        assert hasattr(cls, "save") and \
               isinstance(getattr(cls, "save"),
                          collections.Callable), ("class '" +
               classname + "' must provide a save() method")


class AutoSlotProperties(type):

    def __new__(mcl, classname, bases, dictionary):
        slots = list(dictionary.get("__slots__", []))
        for getter_name in [key for key in dictionary
                            if key.startswith("get_")]:
            if isinstance(dictionary[getter_name],
                          collections.Callable):
                name = getter_name[4:]
                slots.append("__" + name)
                getter = dictionary.pop(getter_name)
                setter_name = "set_" + name
                setter = dictionary.get(setter_name, None)
                if (setter is not None and
                    isinstance(setter, collections.Callable)):
                    del dictionary[setter_name]
                dictionary[name] = property(getter, setter)
        dictionary["__slots__"] = tuple(slots)
        return super().__new__(mcl, classname, bases, dictionary)


class Product(metaclass=AutoSlotProperties):

    def __init__(self, barcode, description):
        self.__barcode = barcode
        self.description = description


    def get_barcode(self):
        return self.__barcode


    def get_description(self):
        return self.__description


    def set_description(self, description):
        if description is None or len(description) < 3:
            self.__description = "<Invalid Description>"
        else:
            self.__description = description



class Point(metaclass=AutoSlotProperties):

    def __init__(self, x, y):
        self.x = x
        self.y = y


    def get_x(self):
        return self.__x


    def set_x(self, value):
        self.__x = min(max(0, value), 1024)


    def get_y(self):
        return self.__y


    def set_y(self, value):
        self.__y = min(max(0, value), 1024)



class PointA(metaclass=AutoSlotProperties):

    __slots__ = ("a",)

    def __init__(self, x, y, a):
        self.x = x
        self.y = y
        self.a = a


    def get_x(self):
        return self.__x


    def set_x(self, value):
        self.__x = min(max(0, value), 1024)


    def get_y(self):
        return self.__y


    def set_y(self, value):
        self.__y = min(max(0, value), 1024)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
