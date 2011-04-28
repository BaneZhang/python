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

    BIBTEXES    ::= BIBTEX+
    BIBTEX      ::= '@Book{' IDENTIFIER ',' KEY_VALUES '}'
    IDENTIFIER  ::= [a-zA-Z][^,\s]*
    KEY_VALUES  ::= KEY_VALUE | KEY_VALUE ',' KEY_VALUES
    KEY_VALUE   ::= KEY '=' VALUE
    KEY         ::= [a-zA-Z]\w*
    VALUE       ::= "[^"]+" | \d+
"""

import pprint
import ply.lex
try:
    from pyparsing import (alphas, alphanums, delimitedList, nums,
            OneOrMore, ParseException, QuotedString, Regex, Suppress, Word)
except ImportError:
    from pyparsing_py3 import (alphas, alphanums, delimitedList, nums,
            OneOrMore, ParseException, QuotedString, Regex, Suppress, Word)
import re

# The examples are copied from Wikipedia
TEXT = """
@Book{blanchette+summerfield,
  author    =  "Jasmin Blanchette and Mark Summerfield",
  title     =  "C++ GUI Programming with Qt 4,
                Second Edition",
  publisher =   "Prentice Hall",
  year      =   2008,
  address   =  "New York"
}
@Book{abramowitz+stegun,
  author    =     "Milton {Abramowitz} and Irene A. {Stegun}",
  title     =      "Handbook of Mathematical Functions with
                  Formulas, Graphs, and Mathematical Tables",
  publisher =      "Dover",
  year      =      1964,
  address   =     "New York",
  edition   =     "ninth Dover printing, tenth GPO printing"
}
@Book{hicks2001,
  author    =     "von Hicks, III, Michael",
  title     =      "Design of a Carbon Fiber Composite Grid Structure for the GLAST 
                 Spacecraft Using a Novel Manufacturing Technique",
  publisher =      "Stanford Press",
  year      =      2001,
  address   =   "Palo Alto",
  edition   =     "1st,",
  isbn      =   "0-69-697269-4"
}
@Book{Torre2008,
  author = "Joe Torre and Tom Verducci",
  publisher = "Doubleday",
  title = "The Yankee Years",
  year = 2008,
  isbn = "0385527403"
}
"""

def pyparsing_parse(text):
    WHITESPACE = re.compile(r"\s+")
    books = {}
    key_values = {}

    def normalize(tokens):
        return WHITESPACE.sub(" ", tokens[0])

    def add_key_value(tokens):
        key_values[tokens.key] = tokens.value

    def add_book(tokens):
        books[tokens.identifier] = key_values.copy()
        key_values.clear()

    left_brace, right_brace, comma, equals = map(Suppress, "{},=")
    start = Suppress("@Book") + left_brace
    identifier = Regex(r"[a-zA-Z][^,\s]*")("identifier") + comma
    key = Word(alphas, alphanums)("key")
    value = (Word(nums).setParseAction(lambda t: int(t[0])) |
             QuotedString('"', multiline=True).setParseAction(normalize)
            )("value")
    key_value = (key + equals + value).setParseAction(add_key_value)
    end = right_brace
    bibtex = (start + identifier + delimitedList(key_value) + end
             ).setParseAction(add_book)
    parser = OneOrMore(bibtex)
    try:
        parser.parseString(text)
    except ParseException as err:
        print("parse error: {0}".format(err))
    return books


def ply_parse(text):
    WHITESPACE = re.compile(r"\s+")

    tokens = ("START", "IDENTIFIER", "KEY", "NUMBER", "QUOTEDSTRING",
              "COMMA", "END")

    t_ignore_START = r"@Book"

    def t_IDENTIFIER(t):
        r"\{[a-zA-Z][^,\s]*"
        t.value = t.value[1:]
        return t

    t_KEY = r"[a-zA-Z]\w*"

    def t_NUMBER(t):
        r"=\s*\d+"
        t.value = int(t.value[1:].lstrip())
        return t

    def t_QUOTEDSTRING(t):
        r'=\s*"[^="]+"'
        t.value = WHITESPACE.sub(" ", t.value[1:].lstrip()[1:-1].strip())
        return t

    t_ignore_COMMA = r","

    t_ignore_END = r"\}"

    t_ignore = " \t\n"

    def t_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        i = line.find("\n")
        line = line if i == -1 else line[:i]
        print("failed to parse line {0}: {1}".format(t.lineno + 1,
                                                     line))

    books = {}
    book = key = None
    lexer = ply.lex.lex()
    lexer.input(text.replace("\n", " "))
    for token in lexer:
        if token.type == "IDENTIFIER":
            books[token.value] = book = {}
            continue
        if book is None:
            print("missing start of book line {0}".format(token.lineno))
        if token.type == "KEY":
            key = token.value
            continue
        if key is None:
            print("missing key line {0}".format(token.lineno))
        if token.type in ("QUOTEDSTRING", "NUMBER"):
            book[key] = token.value
    return books


def main():
    books_ply = ply_parse(TEXT)
    books_pyparsing = pyparsing_parse(TEXT)
    pprint.pprint(books_pyparsing)
    assert books_ply == books_pyparsing


main()
