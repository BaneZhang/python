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
>>> @valid_string("name", empty_allowed=False)
... @valid_string("productid", empty_allowed=False,
...               regex=re.compile(r"[A-Z]{3}\d{4}"))
... @valid_string("category", empty_allowed=False, acceptable=
...         frozenset(["Consumables", "Hardware", "Software", "Media"]))
... @valid_number("price", minimum=0, maximum=1e6)
... @valid_number("quantity", minimum=1, maximum=1000)
... class StockItem:
... 
...     def __init__(self, name, productid, category, price, quantity):
...         self.name = name
...         self.productid = productid
...         self.category = category
...         self.price = price
...         self.quantity = quantity
... 
...     @property
...     def value(self):
...         return self.price * self.quantity
>>> 
>>> pc = StockItem("Computer", "EAA5000", "Hardware", 599, 3)
>>> pc.name == "Computer" and pc.category == "Hardware"
True
>>> pc.productid == "EAA5000"
True
>>> pc.price == 599 and pc.quantity == 3 and pc.value == 1797
True
>>> error = None
>>> try:
...     StockItem("", "ABC1000", "Software", 129, 2)
... except ValueError as e:
...     error = str(e)
>>> error == "name may not be empty"
True
>>> try:
...     StockItem("Printer", "KXV5500", "Vaporware", 129, 2)
... except ValueError as e:
...     error = str(e)
>>> error == "category cannot be set to Vaporware"
True
>>> try:
...     StockItem("Cable", "KXB5001", "Media", -12, 2)
... except ValueError as e:
...     error = str(e)
>>> error == "price -12 is too small"
True
>>> try:
...     StockItem("Socket", "KXY520", "Media", 1e7, 2)
... except ValueError as e:
...     error = str(e)
>>> error == "productid cannot be set to KXY520"
True
>>> try:
...     StockItem("Socket", "KXY5020", "Media", 1e7, 2)
... except ValueError as e:
...     error = str(e)
>>> error == "price 10000000.0 is too big"
True
>>> try:
...     StockItem("Paper", "KXJ5003", "Media", 10, 0)
... except ValueError as e:
...     error = str(e)
>>> error == "quantity 0 is too small"
True
>>> try:
...     StockItem("Ink", "AKX5005", "Media", 10, 1001)
... except ValueError as e:
...     error = str(e)
>>> error == "quantity 1001 is too big"
True
>>> item = StockItem("Toner", "KXV5500", "Media", 10, 100)
>>> item.quantity += 5
>>> item.quantity == 105 and item.value == 1050
True
>>> try:
...     item.quantity = "one"
... except AssertionError as e:
...     error = str(e)
>>> error == "quantity must be a number"
True
"""

import numbers
import re


class GenericDescriptor:

    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter


    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.getter(instance)


    def __set__(self, instance, value):
        return self.setter(instance, value)
        

def valid_string(attr_name, empty_allowed=True, regex=None,
                 acceptable=None):
    def decorator(cls):
        name = "__" + attr_name
        def getter(self):
            return getattr(self, name)
        def setter(self, value):
            assert isinstance(value, str), (attr_name +
                                            " must be a string")
            if not empty_allowed and not value:
                raise ValueError("{0} may not be empty".format(
                                 attr_name))
            if ((acceptable is not None and value not in acceptable) or
                (regex is not None and not regex.match(value))):
                raise ValueError("{attr_name} cannot be set to "
                                 "{value}".format(**locals()))
            setattr(self, name, value)
        setattr(cls, attr_name, GenericDescriptor(getter, setter))
        return cls
    return decorator


def valid_number(attr_name, minimum=None, maximum=None,
                 acceptable=None):
    def decorator(cls):
        name = "__" + attr_name
        def getter(self):
            return getattr(self, name)
        def setter(self, value):
            assert isinstance(value, numbers.Number), (
                    attr_name + " must be a number")
            if minimum is not None and value < minimum:
                raise ValueError("{attr_name} {value} is too small"
                                 .format(**locals()))
            if maximum is not None and value > maximum:
                raise ValueError("{attr_name} {value} is too big"
                                 .format(**locals()))
            if acceptable is not None and value not in acceptable:
                raise ValueError("{attr_name} {value} is unacceptable"
                                 .format(**locals()))
            setattr(self, name, value)
        setattr(cls, attr_name, GenericDescriptor(getter, setter))
        return cls
    return decorator


if __name__ == "__main__":
    import doctest
    doctest.testmod()
