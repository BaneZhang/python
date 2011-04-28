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

    FILE        :: = LINE+
    LINE        ::= INI_HEADER | KEY_VALUE | COMMENT | BLANK
    INI_HEADER  ::= '[' [^]]+ ']'
    KEY_VALUE   ::= KEY '=' VALUE?
    KEY         ::= \w+
    VALUE       ::= .+
    COMMENT     ::= #.*
    BLANK       ::= ^$
"""

import os
import re
import sys
import ply.lex
try:
    from pyparsing import (alphanums, CharsNotIn, OneOrMore,
            ParseException, restOfLine, Suppress, Word)
except ImportError:
    from pyparsing_py3 import (alphanums, CharsNotIn, OneOrMore,
            ParseException, restOfLine, Suppress, Word)


def dict_from_key_values_regex(file, lowercase_keys=False):
    """
    >>> filename = os.path.dirname(__file__)
    >>> filename = os.path.join(filename, "data/iradio-initial.pls")
    >>> with open(filename, "rt", encoding="utf8") as fh:
    ...     d = dict_from_key_values_regex(fh)
    >>> for key in sorted(d.keys())[-4:]:
    ...     print("{0}: {1}".format(key, d[key]))
    title6: Virgin Xtreme (Broadband)
    title7: Virgin Classic Rock (Modem)
    title8: Virgin Classic Rock (Broadband)
    title9: CBC Radio One (Canada)
    >>> d["file13"]
    'http://media.hiof.no/streams/m3u/nrk-petre-172.ogg.m3u'
    >>> d["genre15"]
    ''
    >>> len(d.keys())
    54
    """
    INI_HEADER = re.compile(r"^\[[^]]+\]$")
    KEY_VALUE_RE = re.compile(r"^(?P<key>\w+)\s*=\s*(?P<value>.*)$")

    key_values = {}
    for lino, line in enumerate(file, start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key_value = KEY_VALUE_RE.match(line)
        if key_value:
            key = key_value.group("key")
            if lowercase_keys:
                key = key.lower()
            key_values[key] = key_value.group("value")
        else:
            ini_header = INI_HEADER.match(line)
            if not ini_header:
                print("Failed to parse line {0}: {1}".format(lino,
                                                             line))
    return key_values


def dict_from_key_values_pyparsing(file, lowercase_keys=False):
    """
    >>> filename = os.path.dirname(__file__)
    >>> filename = os.path.join(filename, "data/iradio-initial.pls")
    >>> with open(filename, "rt", encoding="utf8") as fh:
    ...     d = dict_from_key_values_pyparsing(fh)
    >>> for key in sorted(d.keys())[-4:]:
    ...     print("{0}: {1}".format(key, d[key]))
    title6: Virgin Xtreme (Broadband)
    title7: Virgin Classic Rock (Modem)
    title8: Virgin Classic Rock (Broadband)
    title9: CBC Radio One (Canada)
    >>> d["file13"]
    'http://media.hiof.no/streams/m3u/nrk-petre-172.ogg.m3u'
    >>> d["genre15"]
    ''
    >>> len(d.keys())
    54
    """
    def accumulate(tokens):
        key, value = tokens
        key = key.lower() if lowercase_keys else key
        key_values[key] = value

    key_values = {}
    left_bracket, right_bracket, equals = map(Suppress, "[]=")
    ini_header = left_bracket + CharsNotIn("]") + right_bracket
    key_value = Word(alphanums) + equals + restOfLine
    key_value.setParseAction(accumulate)
    comment = "#" + restOfLine
    parser = OneOrMore(ini_header | key_value)
    parser.ignore(comment)
    try:
        parser.parseFile(file)
    except ParseException as err:
        print("parse error: {0}".format(err))
        return {}
    return key_values


def dict_from_key_values_ply(file, lowercase_keys=False):
    """
    >>> filename = os.path.dirname(__file__)
    >>> filename = os.path.join(filename, "data/iradio-initial.pls")
    >>> with open(filename, "rt", encoding="utf8") as fh:
    ...     d = dict_from_key_values_ply(fh)
    >>> for key in sorted(d.keys())[-4:]:
    ...     print("{0}: {1}".format(key, d[key]))
    title6: Virgin Xtreme (Broadband)
    title7: Virgin Classic Rock (Modem)
    title8: Virgin Classic Rock (Broadband)
    title9: CBC Radio One (Canada)
    >>> d["file13"]
    'http://media.hiof.no/streams/m3u/nrk-petre-172.ogg.m3u'
    >>> d["genre15"]
    ''
    >>> len(d.keys())
    54
    """
    tokens = ("INI_HEADER", "COMMENT", "KEY", "VALUE")

    t_ignore_INI_HEADER = r"\[[^]]+\]"
    t_ignore_COMMENT = r"\#.*"

    def t_KEY(t):
        r"\w+"
        if lowercase_keys:
            t.value = t.value.lower()
        return t

    def t_VALUE(t):
        r"=.*"
        t.value = t.value[1:].strip()
        return t

    def t_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        i = line.find("\n")
        line = line if i == -1 else line[:i]
        print("Failed to parse line {0}: {1}".format(t.lineno + 1,
                                                     line))

    key_values = {}
    lexer = ply.lex.lex()
    lexer.input(file.read())
    key = None
    for token in lexer:
        if token.type == "KEY":
            key = token.value
        elif token.type == "VALUE":
            if key is None:
                print("Failed to parse: value '{0}' without key"
                      .format(token.value))
            else:
                key_values[key] = token.value
                key = None
    return key_values


if __name__ == "__main__":
    import doctest
    doctest.testmod()
