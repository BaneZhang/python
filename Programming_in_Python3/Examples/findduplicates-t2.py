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
import itertools
import optparse
import os
import queue
import sys
import threading
import Util


class Worker(threading.Thread):

    Md5_lock = threading.Lock()

    def __init__(self, work_queue, md5_from_filename, results_queue,
                 number):
        super().__init__()
        self.work_queue = work_queue
        self.md5_from_filename = md5_from_filename
        self.results_queue = results_queue
        self.number = number


    def run(self):
        while True:
            try:
                size, names = self.work_queue.get()
                self.process(size, names)
            finally:
                self.work_queue.task_done()


    def process(self, size, filenames):
        md5s = collections.defaultdict(set)
        for filename in filenames:
            with self.Md5_lock:
                md5 = self.md5_from_filename.get(filename, None)
            if md5 is None:
                try:
                    md5 = hashlib.md5()
                    with open(filename, "rb") as fh:
                        md5.update(fh.read())
                    md5 = md5.digest()
                    with self.Md5_lock:
                        self.md5_from_filename[filename] = md5
                except EnvironmentError:
                    continue
            md5s[md5].add(filename)
        for filenames in md5s.values():
            if len(filenames) == 1:
                continue
            self.results_queue.put("{0}Duplicate files ({1:n} bytes):"
                                   "\n\t{2}".format(self.number, size,
                                   "\n\t".join(sorted(filenames))))


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

    if opts.verbose:
        print("Creating {0} thread{1}...".format(
              opts.count, Util.s(opts.count)))
    work_queue = queue.PriorityQueue()
    results_queue = queue.Queue()
    md5_from_filename = {}
    for i in range(opts.count):
        number = "{0}: ".format(i + 1) if opts.debug else ""
        worker = Worker(work_queue, md5_from_filename, results_queue,
                        number)
        worker.daemon = True
        worker.start()

    results_thread = threading.Thread(
                        target=lambda: print_results(results_queue))
    results_thread.daemon = True
    results_thread.start()

    for size, filename in sorted(data):
        names = data[size, filename]
        if len(names) > 1:
            work_queue.put((size, names))
    work_queue.join()
    results_queue.join()


def print_results(results_queue):
    while True:
        try:
            results = results_queue.get()
            if results:
                print(results)
        finally:
            results_queue.task_done()


def parse_options():
    parser = optparse.OptionParser(
            usage=("usage: %prog [options] [path]\n"
                   "outputs a list of duplicate files in path "
                   "using the MD5 algorithm\n"
                   "ignores zero-length files\n"
                   "path defaults to ."))
    parser.add_option("-t", "--threads", dest="count", default=7,
            type="int",
            help=("the number of threads to use (1..20) "
                  "[default %default]"))
    parser.add_option("-v", "--verbose", dest="verbose",
                      default=False, action="store_true")
    parser.add_option("-d", "--debug", dest="debug", default=False,
                      action="store_true")
    opts, args = parser.parse_args()
    if not (1 <= opts.count <= 20):
        parser.error("thread count must be 1..20")
    return opts, args[0] if args else "."


main()
