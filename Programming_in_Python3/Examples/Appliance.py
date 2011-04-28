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
>>> cooker = Cooker("C412", 895.50, "coal/wood")
>>> cooker.model, cooker.price, cooker.fuel
('C412', 895.5, 'coal/wood')
>>> cooker.price = 1265
>>> cooker.price
1265
>>> fridge = Fridge("F31", 426, 290)
>>> fridge.model, fridge.price, fridge.capacity
('F31', 426, 290)
>>> fridge.price = 399
>>> fridge.capacity = 275
>>> fridge.model, fridge.price, fridge.capacity
('F31', 399, 275)
"""

import abc


class Appliance(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, model, price):
        self.__model = model
        self.price = price


    def get_price(self):
        return self.__price

    def set_price(self, price):
        self.__price = price

    price = abc.abstractproperty(get_price, set_price)


    @property
    def model(self):
        return self.__model


class Cooker(Appliance):

    def __init__(self, model, price, fuel):
        super().__init__(model, price)
        self.fuel = fuel

    price = property(lambda self: super().price,
                     lambda self, price: super().set_price(price))


class Fridge(Appliance):

    def __init__(self, model, price, capacity):
        super().__init__(model, price)
        self.capacity = capacity

    price = property(lambda self: super().price,
                     lambda self, price: super().set_price(price))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
