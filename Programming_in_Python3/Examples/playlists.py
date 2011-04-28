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

import optparse
import os
import re
import ReadKeyValue
import ReadM3U


def songs_from_dictionary(dictionary):
    NAME_NUMBER_RE = re.compile(r"^(?P<name>\D+)(?P<number>\d+)$")
    songs = []
    for file in (name for name in sorted(dictionary.keys())
                 if name.startswith("file")):
        name_number = NAME_NUMBER_RE.match(file)
        if name_number:
            name = name_number.group("name")
            number = int(name_number.group("number"))
            filename = dictionary[file]
            title = dictionary.get("title{0}".format(number),
                                   filename)
            seconds = dictionary.get("length{0}".format(number), -1)
            songs.append(ReadM3U.Song(title, seconds, filename))
    return songs


def write_pls(fh, songs):
    fh.write("[playlist]\n")
    for i, song in enumerate(songs, start=1):
        fh.write("File{i}={filename}\nTitle{i}={title}\n"
                "Length{i}={seconds}\n".format(i=i, **song._asdict()))
    fh.write("NumberOfEntries={0}\n".format(len(songs)))
    fh.write("Version=2\n")


def write_m3u(fh, songs):
    fh.write("#EXTM3U\n")
    for song in songs:
        fh.write("#EXTINF:{seconds},{title}\n{filename}\n".format(
                 **song._asdict()))


def parse_options():
    parsers = "regex ply pyparsing".split()
    formats = "m3u pls".split()
    parser = optparse.OptionParser(usage="""\
usage: %prog [options] infile

Reads a playlist in extended .m3u (WinAmp) or extended .pls format
and writes the same data in the specified output format, using the
same name as the infile but with the extension changed appropriately.
""")
    parser.set_defaults(force=False, parser="regex")
    parser.add_option("--force", dest="force",
            action="store_true", help=("write the outfile even if "
                                       "it exists [%default]"))
    parser.add_option("-f", "--format", dest="format",
            choices=formats,
            help="{0} [mandatory]".format(", ".join(formats)))
    parser.add_option("-p", "--parser", dest="parser",
            choices=parsers, help="{0} [%default]".format(
                ", ".join(parsers)))
    opts, args = parser.parse_args()

    if len(args) != 1:
        parser.error("exactly one input file must be specified")
    if not opts.format:
        parser.error("an output format must be specified")
    source = args[0]
    if not source.endswith(tuple(formats)):
        parser.error("input file must have a valid suffix "
                     "(m3u or pls)")
    target = source[:-3] + opts.format
    if source == target:
        parser.error("the output format must differ from the input "
                     "format")
    if os.path.exists(target) and not opts.force:
        parser.error("cannot overwrite existing file {0} without "
                     "the --force option".format(target))
    return opts, source, target


def main():
    parsers = {
        (".pls", "regex"): (lambda fh:
            ReadKeyValue.dict_from_key_values_regex(fh, True)),
        (".pls", "pyparsing"): (lambda fh:
            ReadKeyValue.dict_from_key_values_pyparsing(fh, True)),
        (".pls", "ply"): (lambda fh:
            ReadKeyValue.dict_from_key_values_ply(fh, True)),
        (".m3u", "regex"): ReadM3U.songs_regex,
        (".m3u", "pyparsing"): ReadM3U.songs_pyparsing,
        (".m3u", "ply"): ReadM3U.songs_ply}

    opts, source, target = parse_options()
    parse = parsers[os.path.splitext(source)[1], opts.parser]

    with open(source, "rt") as fh:
        songs = parse(fh)
    if isinstance(songs, dict):
        songs = songs_from_dictionary(songs)

    with open(target, "wt") as fh:
        if target.endswith(".pls"):
            write_pls(fh, songs)
        elif target.endswith(".m3u"):
            write_m3u(fh, songs)


if __name__ == "__main__":
    main()
