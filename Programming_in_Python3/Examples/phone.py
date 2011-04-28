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

import re
import sys


US_PHONE_RE = re.compile(r"""^[ \t]*
                         (?P<parenthesis>\()?
                         [- ]?
                         (?P<area>\d{3})
                         (?(parenthesis)\))
                         [- ]?
                         (?P<local_a>\d{3})
                         [- ]?
                         (?P<local_b>\d{4})
                         [ \t]*$
                         """, re.VERBOSE)

if __name__ == "__main__":
    for line in sys.stdin.readlines():
        line = line.strip()
        if not line:
            continue
        match = US_PHONE_RE.match(line)
        if match:
            print("({0}) {1} {2}".format(match.group("area"),
                match.group("local_a"), match.group("local_b")))
        else:
            print("Invalid U.S. phone number: {0}".format(line))
