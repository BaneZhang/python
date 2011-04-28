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

_file_type_magic_pairs = [
    ("Microsoft Access", b"\x00\x01\x00\x00Standard Jet DB", 0),
    ("Microsoft Word", b"ECA5C100", 512),
    ("Microsoft Write", bytes.fromhex("31BE"), 0),
    ("Microsoft Write", bytes.fromhex("32BE"), 0),
    ("Photoshop Image", bytes.fromhex("38425053"), 0),
    ("Windows BMP Image", bytes.fromhex("424D"), 0),
    ("Windows Compiled Help", bytes.fromhex("49545346"), 0),
    ("Windows Cursor", bytes.fromhex("00000200"), 0),
    ("Windows Help", bytes.fromhex("0000FFFFFFFF"), 7),
    ("Windows Help", bytes.fromhex("3F5F03"), 0),
    ("Windows Help",
     bytes.fromhex("4C4E02004C4E02004C4E02004C4E0200"), 0),
    ("Windows Icon", bytes.fromhex("00000100"), 0),
    ("Windows Metafile Image", bytes.fromhex("D7CDC69A"), 0),
    ("Windows Shortcut", bytes.fromhex("4C00000001140200"), 0),
    ]


for x in range(16):
    _file_type_magic_pairs.append(("MPEG Video",
                        bytes.fromhex("000001B{0:x}".format(x)), 0))


def get_file_type(text, extension):
    for file_type, magic, offset in _file_type_magic_pairs:
        if magic == text[offset:offset + len(magic)]:
            return file_type
    
