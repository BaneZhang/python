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

import datetime
import functools
import optparse
import os
import sys
import time


def coroutine(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        generator = function(*args, **kwargs)
        next(generator)
        return generator
    return wrapper


@coroutine
def suffix_matcher(receiver, suffixes):
    while True:
        filename, stat = (yield)
        if filename.endswith(suffixes):
            receiver.send((filename, stat))


@coroutine
def size_matcher(receiver, minimum=None, maximum=None):
    while True:
        filename, stat = (yield)
        if ((minimum is None or stat.st_size >= minimum) and
            (maximum is None or stat.st_size <= maximum)):
            receiver.send((filename, stat))


@coroutine
def date_matcher(receiver, when):
    while True:
        filename, stat = (yield)
        if stat.st_mtime >= when:
            receiver.send((filename, stat))


@coroutine
def get_files(receiver):
    while True:
        path = (yield)
        if os.path.isfile(path):
            filename = os.path.abspath(path)
            receiver.send((filename, os.stat(filename)))
        else:
            for root, dirs, files in os.walk(path):
                for filename in files:
                    filename = os.path.abspath(
                            os.path.join(root, filename))
                    receiver.send((filename, os.stat(filename)))

@coroutine
def reporter(output):
    size_format = "{0:12,}" if sys.version_info[1] > 0 else "{0:11}"
    while True:
        filename, stat = (yield)
        result = []
        if output is not None:
            if "date" in output:
                result.append(datetime.datetime.fromtimestamp(
                                    stat.st_mtime).isoformat(" "))
            if "size" in output:
                result.append(size_format.format(stat.st_size))
        result.append(filename)
        print(" ".join(result))
        

def get_bytes(s):
    if s[-1] in "kKmM":
        factor = 1024 if s[-1] in "kK" else (1024 ** 2)
        return int(s[:-1]) * factor
    else:
        return int(s)


def parse_options():
    parser = optparse.OptionParser(usage="""\
usage: %prog [options] files_or_paths

Recursively lists all the files that match the given options;
or all the files if no options are specified.

For --bigger and --smaller the size can be given as the number of
bytes (no suffix required), or kilobytes (with a suffix of 'k'),
or megabytes (with a suffix of 'm').

Examples:
    find.py -d1 -o date,size *.*
Find all files modified today and output their name, size, and date.
    find.py -b1m -s10m -d30 -o size *.*
Find all files bigger than 1MB and smaller than 10MB modified in the
past 30 days and output their name and size.""")
    parser.add_option("-d", "--days", dest="days", type="int",
            help=("only find files updated within the past given "
                  "number of days [default: any time]"))
    parser.add_option("-b", "--bigger", dest="bigger",
            help=("only find files bigger than the given amount "
                  "[default: any size]"))
    parser.add_option("-s", "--smaller", dest="smaller",
            help=("only find files smaller than the given amount "
                  "[default: any size]"))
    parser.add_option("-u", "--suffix", dest="suffix",
            help=("only find files that have the given suffix "
                  "(or suffixes if a comma-separated list is given) "
                  "[default: any suffix]"))
    parser.add_option("-o", "--output", dest="output",
            help=("in addition to the filename also output 'date' "
                  "or 'size' or both if both specified comma-separated "
                  "[default: nothing else]"))
    opts, args = parser.parse_args()

    if len(args) == 0:
        parser.error("no files or paths have been specified")
    if opts.smaller is not None:
        opts.smaller = get_bytes(opts.smaller)
    if opts.bigger is not None:
        opts.bigger = get_bytes(opts.bigger)
    if (opts.smaller is not None and opts.bigger is not None and
        opts.bigger > opts.smaller):
        parser.error("cannot find files bigger than {0} that are "
                     "also smaller than {1}".format(
                     opts.bigger, opts.smaller))
    if opts.suffix is not None:
        if "," in opts.suffix:
            opts.suffix = tuple(opts.suffix.split(","))
    if opts.days is not None:
        delta = datetime.timedelta(days=opts.days)
        days = datetime.datetime.today() - delta
        opts.days = time.mktime(days.timetuple())
    return opts, args


def main():
    opts, paths = parse_options()
    pipes = []
    pipes.append(reporter(opts.output))
    if opts.bigger is not None or opts.smaller is not None:
        pipes.append(size_matcher(pipes[-1], minimum=opts.bigger,
                     maximum=opts.smaller))
    if opts.suffix is not None:
        pipes.append(suffix_matcher(pipes[-1], opts.suffix))
    if opts.days is not None:
        pipes.append(date_matcher(pipes[-1], opts.days))
    pipes.append(get_files(pipes[-1]))
    pipeline = pipes[-1]
    try:
        for path in paths:
            pipeline.send(path)
    finally:
        for pipe in pipes:
            pipe.close()

main()
