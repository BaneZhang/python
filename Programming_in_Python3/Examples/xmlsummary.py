#!/usr/bin/env python3
# Copyright (c) 2008-10 Qtrac Ltd. All rights reserved.
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
import queue
import threading
import xml.etree.ElementTree
import xml.parsers.expat
import Util


if hasattr(xml.etree.ElementTree, "ParseError"): # Python 3.2
    class Worker(threading.Thread):

        def __init__(self, work_queue, results_queue, number):
            super().__init__()
            self.work_queue = work_queue
            self.results_queue = results_queue
            self.number = number


        def run(self):
            while True:
                try:
                    filename = self.work_queue.get()
                    self.process(filename)
                finally:
                    self.work_queue.task_done()


        def process(self, filename):
            tags = set()
            try:
                with open(filename, "r", encoding="utf8",
                        errors="ignore") as fh:
                    line = fh.readline()
                    if not line.startswith("<?xml"):
                        return
                    fh.close()
                tree = xml.etree.ElementTree.parse(filename)
                for element in tree.getiterator():
                    tags.add(element.tag)
            except xml.etree.ElementTree.ParseError as err: # Python 3.2
                message = "has the following error:\n    " + str(err)
            except xml.parsers.expat.ExpatError as err:
                message = "has the following error:\n    " + str(err)
            except EnvironmentError as err:
                message = "could not be read:\n    " + str(err)
            else:
                message = ("uses the following tags:\n    " +
                        "\n    ".join(sorted(tags, key=str.lower)))
            message = (self.number + filename + " is an XML file that " +
                    message)
            self.results_queue.put(message)
else:
    class Worker(threading.Thread):

        def __init__(self, work_queue, results_queue, number):
            super().__init__()
            self.work_queue = work_queue
            self.results_queue = results_queue
            self.number = number


        def run(self):
            while True:
                try:
                    filename = self.work_queue.get()
                    self.process(filename)
                finally:
                    self.work_queue.task_done()


        def process(self, filename):
            tags = set()
            try:
                with open(filename, "r", encoding="utf8",
                        errors="ignore") as fh:
                    line = fh.readline()
                    if not line.startswith("<?xml"):
                        return
                    fh.close()
                tree = xml.etree.ElementTree.parse(filename)
                for element in tree.getiterator():
                    tags.add(element.tag)
            except xml.parsers.expat.ExpatError as err:
                message = "has the following error:\n    " + str(err)
            except EnvironmentError as err:
                message = "could not be read:\n    " + str(err)
            else:
                message = ("uses the following tags:\n    " +
                        "\n    ".join(sorted(tags, key=str.lower)))
            message = (self.number + filename + " is an XML file that " +
                    message)
            self.results_queue.put(message)


def main():
    opts, path = parse_options()
    if opts.verbose:
        print("Creating {0} thread{1}...".format(
              opts.count, Util.s(opts.count)))
    work_queue = queue.Queue()
    results_queue = queue.Queue()
    for i in range(opts.count):
        number = "{0}: ".format(i + 1) if opts.debug else ""
        worker = Worker(work_queue, results_queue, number)
        worker.daemon = True
        worker.start()

    results_thread = threading.Thread(
                        target=lambda: print_results(results_queue))
    results_thread.daemon = True
    results_thread.start()

    for root, dirs, files in os.walk(path):
        for filename in files:
            fullname = os.path.join(root, filename)
            work_queue.put(fullname)
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
                   "outputs a summary of the XML files in path\n"
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
