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

"""
BNF

    M3U         ::= '#EXTM3U' ENTRY+
    ENTRY       ::= INFO FILENAME
    INFO        ::= '#EXTINF:' SECONDS ',' TITLE
    SECONDS     ::= -?\d+
    TITLE       ::= .+
    FILENAME    ::= .+
"""

import collections
import re
import ply.lex
try:
    from pyparsing import (Combine, LineEnd, nums, OneOrMore,
            Optional, ParseException, restOfLine, Suppress, Word)
except ImportError:
    from pyparsing_py3 import (Combine, LineEnd, nums, OneOrMore,
            Optional, ParseException, restOfLine, Suppress, Word)


Song = collections.namedtuple("Song", "title seconds filename")


def songs_regex(fh):
    r"""
    >>> import os
    >>> filename = os.path.dirname(__file__)
    >>> filename = os.path.join(filename, "data/Various-Pop.m3u")
    >>> with open(filename, "rt", encoding="utf8") as fh:
    ...     songs = songs_regex(fh)
    >>> songs[0].title, songs[0].seconds, songs[0].filename
    ('Various - Two Tribes', 236, 'Various\\Frankie Goes To Hollywood\\02-Two Tribes.ogg')
    >>> songs[-1].title, songs[-1].seconds, songs[-1].filename
    ('The Police - Walking On The Moon', 303, 'Various\\Sting & The Police 1997\\06-Walking On The Moon.ogg')
    >>> lines = []
    >>> lines.append("#EXTM3U")
    >>> lines.append("#EXTINF:140,The Beatles - Love Me Do")
    >>> lines.append("Beatles\\Greatest Hits\\01-Love Me Do.ogg")
    >>> lines.append("#EXTINF:-1,The Beatles - From Me To You")
    >>> lines.append("Beatles\\Greatest Hits\\02-From Me To You.ogg")
    >>> import io
    >>> data = io.StringIO("\n".join(lines))
    >>> songs = songs_ply(data)
    >>> len(songs) == 2
    True
    >>> songs[0].title, songs[0].seconds
    ('The Beatles - Love Me Do', 140)
    >>> songs[1].title, songs[1].seconds
    ('The Beatles - From Me To You', -1)
    """
    if fh.readline() != "#EXTM3U\n":
        print("This is not a .m3u file")
        return []
    songs = []
    INFO_RE = re.compile(r"#EXTINF:(?P<seconds>-?\d+),(?P<title>.+)")
    title = seconds = None
    WANT_INFO, WANT_FILENAME = range(2)
    state = WANT_INFO
    for lino, line in enumerate(fh, start=2):
        line = line.strip()
        if not line:
            continue
        if state == WANT_INFO:
            info = INFO_RE.match(line)
            if info:
                title = info.group("title")
                seconds = int(info.group("seconds"))
                state = WANT_FILENAME
            else:
                print("Failed to parse line {0}: {1}".format(
                      lino, line))
        elif state == WANT_FILENAME:
            songs.append(Song(title, seconds, line))
            title = seconds = None
            state = WANT_INFO
    return songs


def songs_pyparsing(fh):
    r"""
    >>> import os
    >>> filename = os.path.dirname(__file__)
    >>> filename = os.path.join(filename, "data/Various-Pop.m3u")
    >>> with open(filename, "rt", encoding="utf8") as fh:
    ...     songs = songs_pyparsing(fh)
    >>> songs[0].title, songs[0].seconds, songs[0].filename
    ('Various - Two Tribes', 236, 'Various\\Frankie Goes To Hollywood\\02-Two Tribes.ogg')
    >>> songs[-1].title, songs[-1].seconds, songs[-1].filename
    ('The Police - Walking On The Moon', 303, 'Various\\Sting & The Police 1997\\06-Walking On The Moon.ogg')
    >>> lines = []
    >>> lines.append("#EXTM3U")
    >>> lines.append("#EXTINF:140,The Beatles - Love Me Do")
    >>> lines.append("Beatles\\Greatest Hits\\01-Love Me Do.ogg")
    >>> lines.append("#EXTINF:-1,The Beatles - From Me To You")
    >>> lines.append("Beatles\\Greatest Hits\\02-From Me To You.ogg")
    >>> import io
    >>> data = io.StringIO("\n".join(lines))
    >>> songs = songs_ply(data)
    >>> len(songs) == 2
    True
    >>> songs[0].title, songs[0].seconds
    ('The Beatles - Love Me Do', 140)
    >>> songs[1].title, songs[1].seconds
    ('The Beatles - From Me To You', -1)
    """

    def add_song(tokens):
        songs.append(Song(tokens.title, tokens.seconds,
                          tokens.filename))
        #songs.append(Song(**tokens.asDict()))

    songs = []
    title = restOfLine("title")
    filename = restOfLine("filename")
    seconds = Combine(Optional("-") + Word(nums)).setParseAction(
            lambda tokens: int(tokens[0]))("seconds")
    info = Suppress("#EXTINF:") + seconds + Suppress(",") + title
    entry = info + LineEnd() + filename + LineEnd()
    entry.setParseAction(add_song)
    parser = Suppress("#EXTM3U") + OneOrMore(entry)
    try:
        parser.parseFile(fh)
    except ParseException as err:
        print("parse error: {0}".format(err))
        return []
    return songs


def songs_ply(fh):
    r"""
    >>> import os
    >>> filename = os.path.dirname(__file__)
    >>> filename = os.path.join(filename, "data/Various-Pop.m3u")
    >>> with open(filename, "rt", encoding="utf8") as fh:
    ...     songs = songs_ply(fh)
    >>> songs[0].title, songs[0].seconds, songs[0].filename
    ('Various - Two Tribes', 236, 'Various\\Frankie Goes To Hollywood\\02-Two Tribes.ogg')
    >>> songs[-1].title, songs[-1].seconds, songs[-1].filename
    ('The Police - Walking On The Moon', 303, 'Various\\Sting & The Police 1997\\06-Walking On The Moon.ogg')
    >>> lines = []
    >>> lines.append("#EXTM3U")
    >>> lines.append("#EXTINF:140,The Beatles - Love Me Do")
    >>> lines.append("Beatles\\Greatest Hits\\01-Love Me Do.ogg")
    >>> lines.append("#EXTINF:-1,The Beatles - From Me To You")
    >>> lines.append("Beatles\\Greatest Hits\\02-From Me To You.ogg")
    >>> import io
    >>> data = io.StringIO("\n".join(lines))
    >>> songs = songs_ply(data)
    >>> len(songs) == 2
    True
    >>> songs[0].title, songs[0].seconds
    ('The Beatles - Love Me Do', 140)
    >>> songs[1].title, songs[1].seconds
    ('The Beatles - From Me To You', -1)
    """
    tokens = ("M3U", "INFO", "SECONDS", "TITLE", "FILENAME")
    states = (("entry", "exclusive"), ("filename", "exclusive"))

    t_M3U = r"\#EXTM3U"

    def t_INFO(t):
        r"\#EXTINF:"
        t.lexer.begin("entry")
        return None

    def t_entry_SECONDS(t):
        r"-?\d+,"
        t.value = int(t.value[:-1])
        return t

    def t_entry_TITLE(t):
        r"[^\n]+"
        t.lexer.begin("filename")
        return t

    def t_filename_FILENAME(t):
        r"[^\n]+"
        t.lexer.begin("INITIAL")
        return t

    t_ANY_ignore = " \t\n"

    def t_ANY_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_ANY_error(t):
        line = t.value.lstrip()
        i = line.find("\n")
        line = line if i == -1 else line[:i]
        print("Failed to parse line {0}: {1}".format(t.lineno + 1,
                                                     line))

    songs = []
    title = seconds = None
    lexer = ply.lex.lex()
    lexer.input(fh.read())
    for token in lexer:
        if token.type == "SECONDS":
            seconds = token.value
        elif token.type == "TITLE":
            title = token.value
        elif token.type == "FILENAME":
            if title is not None and seconds is not None:
                songs.append(Song(title, seconds, token.value))
                title = seconds = None
            else:
                print("Failed, filename '{0}' without title/duration"
                      .format(token.value))
    return songs


if __name__ == "__main__":
    import doctest
    doctest.testmod()
