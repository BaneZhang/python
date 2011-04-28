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


__all__ = ["Block", "get_root_block", "get_empty_block",
           "get_new_row", "is_new_row"]


class Block:

    def __init__(self, name, color="white"):
        self.name = name
        self.color = color
        self.children = []


    def has_children(self):
        return bool(self.children)


    def __str__(self):
        blocks = []
        if self.name is not None:
            color = "{0}: ".format(self.color) if self.color else ""
            block = "[{0}{1}".format(color, self.name)
            blocks.append(block)
        if self.children:
            blocks.append("\n")
            for block in self.children:
                if is_new_row(block):
                    blocks.append("/\n")
                else:
                    blocks.append(str(block))
        if self.name is not None:
            blocks[-1] += "]\n"
        return "".join(blocks)


get_root_block = lambda: Block(None, None)
get_empty_block = lambda: Block("")
get_new_row = lambda: None
is_new_row = lambda x: x is None
