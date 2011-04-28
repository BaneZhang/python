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

import locale
locale.setlocale(locale.LC_ALL, "")

import collections
import hashlib
import optparse
import os
import multiprocessing


def main():
    opts, path = parse_options()
    data = collections.defaultdict(list)
    if opts.verbose:
        print("Creating file list...")
    for root, dirs, files in os.walk(path):
        for filename in files:
            fullname = os.path.join(root, filename)
            try:
                key = (os.path.getsize(fullname), filename)
            except EnvironmentError:
                continue
            if key[0] == 0:
                continue
            data[key].append(fullname)

    items = []
    for key in sorted(data):
        if len(data[key]) > 1:
            items.append((key[0], tuple(data[key])))
    if items:
        pool = multiprocessing.Pool()
        pool.map_async(check_one_item, items, 1, print_result)
        pool.close()
        pool.join()


def check_one_item(item):
    filenames = item[1]
    md5s = collections.defaultdict(set)
    for filename in filenames:
        try:
            md5 = hashlib.md5()
            with open(filename, "rb") as fh:
                md5.update(fh.read())
            md5 = md5.digest()
            md5s[md5].add(filename)
        except EnvironmentError:
            continue
    results = []
    for filenames in md5s.values():
        if len(filenames) == 1:
            continue
        results.append("Duplicate files ({0:n} bytes):\n\t{1}".format(
                       item[0], "\n\t".join(sorted(filenames))))
    return "\n".join(results)


def print_result(results):
    for result in results:
        if result:
            print(result)


def parse_options():
    parser = optparse.OptionParser(
            usage=("usage: %prog [options] [path]\n"
                   "outputs a list of duplicate files in path "
                   "using the MD5 algorithm\n"
                   "ignores zero-length files\n"
                   "path defaults to ."))
    parser.add_option("-v", "--verbose", dest="verbose",
                      default=False, action="store_true")
    parser.add_option("-d", "--debug", dest="debug", default=False,
                      action="store_true")
    opts, args = parser.parse_args()
    return opts, args[0] if args else "."


if __name__ == "__main__": # This is *vital* on Windows!
    main()
