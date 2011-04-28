#!/usr/bin/env python3
# Copyright (c) 20011 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import unittest
import Atomic


class TestAtomic(unittest.TestCase):

    def setUp(self):
        self.original_list = list(range(10))

    
    def test_list_succeed(self):
        items = self.original_list[:]
        with Atomic.Atomic(items) as atomic:
            atomic.append(1999)
            atomic.insert(2, -915)
            del atomic[5]
            atomic[4] = -782
            atomic.insert(0, -9)
        self.assertEqual(items,
                [-9, 0, 1, -915, 2, -782, 5, 6, 7, 8, 9, 1999])


    def test_list_fail(self):
        def process():
            nonlocal items
            with Atomic.Atomic(items) as atomic:
                atomic.append(1999)
                atomic.insert(2, -915)
                del atomic[5]
                atomic[4] = -782
                atomic.poop() # Typo

        items = self.original_list[:]
        self.assertRaises(AttributeError, process)
        self.assertEqual(items, self.original_list)


if __name__ == "__main__":
    unittest.main()
