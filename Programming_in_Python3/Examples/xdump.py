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

import optparse
import os
import sys


def main():
    parser = optparse.OptionParser(
                usage="usage: %prog [options] file1 [file2 [... fileN]]")
    parser.add_option("-b", "--blocksize", dest="blocksize", type="int",
            help="block size (8..80) [default: %default]")
    parser.add_option("-d", "--decimal", dest="decimal",
            action="store_true",
            help="decimal block numbers [default: hexadecimal]")
    parser.add_option("-e", "--encoding", dest="encoding",
            help="encoding (ASCII..UTF-32) [default: %default]")
    parser.set_defaults(blocksize=16, decimal=False, encoding="UTF-8")
    opts, files = parser.parse_args()
    if not (8 <= opts.blocksize <= 80):
        parser.error("invalid blocksize")
    if not files:
        parser.error("no files specified")

    for i, filename in enumerate(files):
        if i:
            print()
        if len(files) > 1:
            print("File:", filename)
        xdump(filename, opts.blocksize, opts.encoding, opts.decimal)


def xdump(filename, blocksize, encoding, decimal):
    encoding_text = "{0} characters".format(encoding.upper())
    width = (blocksize * 2) + (blocksize // 4)
    if blocksize % 4:
        width += 1
    print("Block     Bytes{0:{1}} {2}".format("", (width - 5),
                                              encoding_text))
    print("--------  {0}  {1}".format("-" * (width - 1),
          "-" * max(len(encoding_text), blocksize)))
    block_number_format = "{0:08} " if decimal else "{0:08X} "
    block_number = 0
    fh = None
    try:
        fh = open(filename, "rb")
        while True:
            data = fh.read(blocksize)
            if not data:
                break
            line = [block_number_format.format(block_number)]
            chars = []
            for i, b in enumerate(data):
                if i % 4 == 0:
                    line.append(" ")
                line.append("{0:02X}".format(b))
                chars.append(b if 32 <= b < 127 else ord("."))
            for i in range(len(data), blocksize):
                if i % 4 == 0:
                    line.append(" ")
                line.append("  ")
            line.append("  ")
            line.append(bytes(chars).decode(encoding, "replace")
                        .replace("\uFFFD", "."))
            print("".join(line))
            block_number += 1
    except EnvironmentError as err:
        print(err)
    finally:
        if fh is not None:
            fh.close()


main()
