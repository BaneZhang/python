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
>>> u = Stack()
>>> u.push(1); u.push(2); u.push(4)
>>> str(u)
'[1, 2, 4]'
>>> u.can_undo
True
>>> while u.can_undo:
...     u.undo()
>>> str(u)
'[]'
>>> for x in list(range(-5, 0)) +  list(range(5)):
...    u.push(x)
>>> str(u)
'[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]'
>>> u.top()
4
>>> total = 0
>>> for x in range(5):
...     total += u.pop()
>>> str(u), total
('[-5, -4, -3, -2, -1]', 10)
>>> while u.can_undo:
...     u.undo()
>>> str(u)
'[]'

>>> import os
>>> import tempfile
>>> filename = os.path.join(tempfile.gettempdir(), "fs.pkl")
>>> fs = FileStack(filename)
>>> for x in list(range(-5, 0)) +  list(range(5)):
...    fs.push(x)
>>> str(fs)
'[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]'
>>> fs.top()
4
>>> total = 0
>>> for x in range(5):
...     total += fs.pop()
>>> str(fs), total
('[-5, -4, -3, -2, -1]', 10)
>>> fs.push(909)
>>> str(fs)
'[-5, -4, -3, -2, -1, 909]'
>>> os.path.basename(fs.filename)
'fs.pkl'
>>> fs.save()
>>> fs2 = FileStack(filename)
>>> str(fs2)
'[]'
>>> fs2.push(-32)
>>> fs2.can_undo
True
>>> fs2.load()
>>> fs2.can_undo
False
>>> str(fs2)
'[-5, -4, -3, -2, -1, 909]'
>>> fs == fs2
True
"""


import abc
import pickle


class Undo(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self):
        self.__undos = []


    @abc.abstractproperty
    def can_undo(self):
        return bool(self.__undos)


    @abc.abstractmethod
    def undo(self):
        assert self.__undos, "nothing left to undo"
        self.__undos.pop()(self)


    def add_undo(self, undo):
        self.__undos.append(undo)


    def clear(self):        # In class Undo
        self.__undos = []


class Stack(Undo):

    def __init__(self):
        super().__init__()
        self.__stack = []


    @property
    def can_undo(self):
        return super().can_undo


    def undo(self):
        super().undo()


    def push(self, item):
        self.__stack.append(item)
        self.add_undo(lambda self: self.__stack.pop())


    def pop(self):
        item = self.__stack.pop()
        self.add_undo(lambda self: self.__stack.append(item))
        return item


    def top(self):
        assert self.__stack, "Stack is empty"
        return self.__stack[-1]


    def __str__(self):
        return str(self.__stack)


class NoFilenameError(Exception): pass


class LoadSave:

    def __init__(self, filename, *attribute_names):
        self.filename = filename
        self.__attribute_names = []
        for name in attribute_names:
            if name.startswith("__"):
                name = "_" + self.__class__.__name__ + name
            self.__attribute_names.append(name)


    def save(self):
        with open(self.filename, "wb") as fh:
            data = []
            for name in self.__attribute_names:
                data.append(getattr(self, name))
            pickle.dump(data, fh, pickle.HIGHEST_PROTOCOL)


    def load(self):
        with open(self.filename, "rb") as fh:
            data = pickle.load(fh)
            for name, value in zip(self.__attribute_names, data):
                setattr(self, name, value)


class FileStack(Undo, LoadSave):

    def __init__(self, filename):
        Undo.__init__(self)
        LoadSave.__init__(self, filename, "__stack")
        self.__stack = []


    def load(self):
        super().load()
        self.clear()


    @property
    def can_undo(self):
        return super().can_undo


    def undo(self):
        super().undo()


    def push(self, item):
        self.__stack.append(item)
        self.add_undo(lambda self: self.__stack.pop())


    def pop(self):
        item = self.__stack.pop()
        self.add_undo(lambda self: self.__stack.append(item))
        return item


    def top(self):
        assert self.__stack, "Stack is empty"
        return self.__stack[-1]


    def __eq__(self, other):
        return self.__stack == other.__stack


    def __str__(self):
        return str(self.__stack)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

