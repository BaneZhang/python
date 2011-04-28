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
>>> forenames = ("Warisha", "Elysha", "Liona", "Kassandra", "Simone",
... "Halima", "Liona", "Zack", "Josiah", "Sam", "Braedon", "Eleni")
>>> surnames = ("Chandler", "Drennan", "Stead", "Doole", "Reneau", "Dent",
... "Sheckles", "Dent", "Reddihough", "Dodwell", "Conner", "Abson")
>>> people = []
>>> for forename, surname in zip(forenames, surnames):
...     people.append(Person(forename, surname, forename.lower() +
...             "." + surname.lower() + "@eg.com"))
>>> [x.email[:-7] for x in people]
['warisha.chandler', 'elysha.drennan', 'liona.stead', 'kassandra.doole', 'simone.reneau', 'halima.dent', 'liona.sheckles', 'zack.dent', 'josiah.reddihough', 'sam.dodwell', 'braedon.conner', 'eleni.abson']

>>> [x.email[:-7] for x in sorted(people, key=SortKey("surname"))]
['eleni.abson', 'warisha.chandler', 'braedon.conner', 'halima.dent', 'zack.dent', 'sam.dodwell', 'kassandra.doole', 'elysha.drennan', 'josiah.reddihough', 'simone.reneau', 'liona.sheckles', 'liona.stead']

>>> [x.email[:-7] for x in sorted(people, key=SortKey("surname", "forename"))]
['eleni.abson', 'warisha.chandler', 'braedon.conner', 'halima.dent', 'zack.dent', 'sam.dodwell', 'kassandra.doole', 'elysha.drennan', 'josiah.reddihough', 'simone.reneau', 'liona.sheckles', 'liona.stead']

>>> [x.email[:-7] for x in sorted(people, key=SortKey("forename"))]
['braedon.conner', 'eleni.abson', 'elysha.drennan', 'halima.dent', 'josiah.reddihough', 'kassandra.doole', 'liona.stead', 'liona.sheckles', 'sam.dodwell', 'simone.reneau', 'warisha.chandler', 'zack.dent']

>>> [x.email[:-7] for x in sorted(people, key=SortKey("forename", "surname"))]
['braedon.conner', 'eleni.abson', 'elysha.drennan', 'halima.dent', 'josiah.reddihough', 'kassandra.doole', 'liona.sheckles', 'liona.stead', 'sam.dodwell', 'simone.reneau', 'warisha.chandler', 'zack.dent']

>>> import operator
>>> [x.email[:-7] for x in sorted(people, key=operator.attrgetter("surname"))]
['eleni.abson', 'warisha.chandler', 'braedon.conner', 'halima.dent', 'zack.dent', 'sam.dodwell', 'kassandra.doole', 'elysha.drennan', 'josiah.reddihough', 'simone.reneau', 'liona.sheckles', 'liona.stead']

>>> [x.email[:-7] for x in sorted(people, key=operator.attrgetter("surname", "forename"))]
['eleni.abson', 'warisha.chandler', 'braedon.conner', 'halima.dent', 'zack.dent', 'sam.dodwell', 'kassandra.doole', 'elysha.drennan', 'josiah.reddihough', 'simone.reneau', 'liona.sheckles', 'liona.stead']

>>> [x.email[:-7] for x in sorted(people, key=operator.attrgetter("forename"))]
['braedon.conner', 'eleni.abson', 'elysha.drennan', 'halima.dent', 'josiah.reddihough', 'kassandra.doole', 'liona.stead', 'liona.sheckles', 'sam.dodwell', 'simone.reneau', 'warisha.chandler', 'zack.dent']

>>> [x.email[:-7] for x in sorted(people, key=operator.attrgetter("forename", "surname"))]
['braedon.conner', 'eleni.abson', 'elysha.drennan', 'halima.dent', 'josiah.reddihough', 'kassandra.doole', 'liona.sheckles', 'liona.stead', 'sam.dodwell', 'simone.reneau', 'warisha.chandler', 'zack.dent']

"""

class Person:

    def __init__(self, forename, surname, email):
        self.forename = forename
        self.surname = surname
        self.email = email


    def __str__(self):
        return "{0.forename} {0.surname} <{0.email}>".format(self)


class SortKey:

    def __init__(self, *attribute_names):
        self.attribute_names = attribute_names


    def __call__(self, instance):
        values = []
        for attribute_name in self.attribute_names:
            values.append(getattr(instance, attribute_name))
        return values


if __name__ == "__main__":
    import doctest
    doctest.testmod()
