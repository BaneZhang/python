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
>>> product = Product("Chisel <3cm>", "Chisel & cap", 45.25)
>>> product.name, product.name_as_xml, product.description_as_xml
('Chisel <3cm>', 'Chisel &lt;3cm&gt;', 'Chisel &amp; cap')
>>> product = CachedProduct("Chisel <3cm>", "Chisel & cap", 45.25)
>>> product.name, product.name_as_xml, product.description_as_xml
('Chisel <3cm>', 'Chisel &lt;3cm&gt;', 'Chisel &amp; cap')
"""

import xml.sax.saxutils


class XmlShadow:

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name


    def __get__(self, instance, owner=None):
        return xml.sax.saxutils.escape(
                            getattr(instance, self.attribute_name))


class Product:

    __slots__ = ("__name", "__description", "__price")

    name_as_xml = XmlShadow("name")
    description_as_xml = XmlShadow("description")

    def __init__(self, name, description, price):
        self.__name = name
        self.description = description
        self.price = price


    @property
    def name(self):
        return self.__name


    @property
    def description(self):
        return self.__description


    @description.setter
    def description(self, description):
        self.__description = description


    @property
    def price(self):
        return self.__price


    @price.setter
    def price(self, price):
        self.__price = price


class CachedXmlShadow:

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name
        self.cache = {}


    def __get__(self, instance, owner=None):
        xml_text = self.cache.get(id(instance))
        if xml_text is not None:
            return xml_text
        return self.cache.setdefault(id(instance),
                xml.sax.saxutils.escape(
                            getattr(instance, self.attribute_name)))


class CachedProduct:

    __slots__ = ("__name", "__description", "__price")

    name_as_xml = CachedXmlShadow("name")
    description_as_xml = CachedXmlShadow("description")

    def __init__(self, name, description, price):
        self.__name = name
        self.description = description
        self.price = price


    @property
    def name(self):
        return self.__name


    @property
    def description(self):
        return self.__description


    @description.setter
    def description(self, description):
        self.__description = description


    @property
    def price(self):
        return self.__price


    @price.setter
    def price(self, price):
        self.__price = price




if __name__ == "__main__":
    import doctest
    doctest.testmod()

