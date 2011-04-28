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


def indented_list_sort(indented_list, indent="    "):
    """Returns an alphabetically sorted copy of the given list

    The indented list is assumed to be a list of strings in a
    hierarchy with indentation used to indicate child items.
    The indent parameter specifies the characters that constitute
    one level of indent.

    The function copies the list, and returns it sorted in
    case-insensitive alphabetical order, with child items sorted
    underneath their parent items, and so on with grandchild items,
    and so on recursively to any level of depth.

    >>> indented_list = ["M", " MX", " MG", "D", " DA", " DF",\
    "  DFX", "  DFK", "  DFB", " DC", "K", "X", "H", " HJ",\
    " HB", "A"]
    >>> 
    >>> indented_list = indented_list_sort(indented_list, " ")
    >>> indented_list[:8]
    ['A', 'D', ' DA', ' DC', ' DF', '  DFB', '  DFK', '  DFX']
    >>> indented_list[8:]
    ['H', ' HB', ' HJ', 'K', 'M', ' MG', ' MX', 'X']
    """
    KEY, ITEM, CHILDREN = range(3)

    def add_entry(level, key, item, children):
        if level == 0:
            children.append((key, item, []))
        else:
            add_entry(level - 1, key, item, children[-1][CHILDREN])

    def update_indented_list(entry):
        indented_list.append(entry[ITEM])
        for subentry in sorted(entry[CHILDREN]):
            update_indented_list(subentry)

    entries = []
    for item in indented_list:
        level = 0
        i = 0
        while item.startswith(indent, i):
            i += len(indent)
            level += 1
        key = item.strip().lower()
        add_entry(level, key, item, entries)

    indented_list = []
    for entry in sorted(entries):
        update_indented_list(entry)
    return indented_list


def indented_list_sort_local(indented_list, indent="    "):
    """
    Given an indented list, i.e., a list of items with indented
    subitems, sorts the items, and the subitems within each item (and so
    on recursively) in case-insensitive alphabetical order.

    >>> indented_list = ["M", " MX", " MG", "D", " DA", " DF", "  DFX", \
    "  DFK", "  DFB", " DC", "K", "X", "H", " HJ", " HB", "A"]
    >>> 
    >>> indented_list = indented_list_sort_local(indented_list, " ")
    >>> indented_list[:8]
    ['A', 'D', ' DA', ' DC', ' DF', '  DFB', '  DFK', '  DFX']
    >>> indented_list[8:]
    ['H', ' HB', ' HJ', 'K', 'M', ' MG', ' MX', 'X']
    """
    KEY, ITEM, CHILDREN = range(3)

    def add_entry(key, item, children):
        nonlocal level
        if level == 0:
            children.append((key, item, []))
        else:
            level -= 1
            add_entry(key, item, children[-1][CHILDREN])

    def update_indented_list(entry):
        indented_list.append(entry[ITEM])
        for subentry in sorted(entry[CHILDREN]):
            update_indented_list(subentry)

    entries = []
    for item in indented_list:
        level = 0
        i = 0
        while item.startswith(indent, i):
            i += len(indent)
            level += 1
        key = item.strip().lower()
        add_entry(key, item, entries)

    indented_list = []
    for entry in sorted(entries):
        update_indented_list(entry)
    return indented_list


if __name__ == "__main__":
    before = ["Nonmetals", 
              "    Hydrogen", 
              "    Carbon", 
              "    Nitrogen", 
              "    Oxygen", 
              "Inner Transitionals", 
              "    Lanthanides", 
              "        Cerium", 
              "        Europium", 
              "    Actinides", 
              "        Uranium", 
              "        Curium", 
              "        Plutonium", 
              "Alkali Metals", 
              "    Lithium", 
              "    Sodium", 
              "    Potassium"]
    result1 = indented_list_sort(before)
    result2 = indented_list_sort_local(before)
    after = ["Alkali Metals",
             "    Lithium",
             "    Potassium",
             "    Sodium",
             "Inner Transitionals",
             "    Actinides",
             "        Curium",
             "        Plutonium",
             "        Uranium",
             "    Lanthanides",
             "        Cerium",
             "        Europium",
             "Nonmetals",
             "    Carbon",
             "    Hydrogen",
             "    Nitrogen",
             "    Oxygen"]
    assert result1 == result2 == after

    import doctest
    doctest.testmod()
