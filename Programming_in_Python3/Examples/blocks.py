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

    BLOCKS  ::= NODES+
    NODES   ::= NEW_ROW* NODE+
    NODE    ::= '[' (COLOR ':')? NAME? NODES* ']'
    COLOR   ::= '#'[\dA-Fa-f]{6} | [a-zA-Z]\w*
    NAME    ::= [^][/]+
    NEW_ROW ::= '/'
"""

import optparse
import sys
import Block
import BlockOutput
import ply.lex
try:
    from pyparsing import (alphanums, alphas, CharsNotIn, Forward,
            Group, hexnums, OneOrMore, Optional, ParseException,
            ParseSyntaxException, Suppress, Word, ZeroOrMore)
except ImportError:
    from pyparsing_py3 import (alphanums, alphas, CharsNotIn, Forward,
            Group, hexnums, OneOrMore, Optional, ParseException,
            ParseSyntaxException, Suppress, Word, ZeroOrMore)


EmptyBlock = 0
class LexError(Exception): pass


def recursive_descent_parse(text):
    """
    >>> import os
    >>> dirname = os.path.join(os.path.dirname(__file__), "data")
    >>> filename = os.path.join(dirname, "error1.blk")
    >>> recursive_descent_parse(open(filename, encoding="utf8").read())
    Traceback (most recent call last):
    ...
    ValueError: Error {0}:line 8, column 2: ran out of text when expecting ']'
    >>> filename = os.path.join(dirname, "error2.blk")
    >>> recursive_descent_parse(open(filename, encoding="utf8").read())
    Traceback (most recent call last):
    ...
    ValueError: Error {0}:line 1, column 1: expected '[]/' but got '#'
    >>> filename = os.path.join(dirname, "error3.blk")
    >>> recursive_descent_parse(open(filename, encoding="utf8").read())
    Traceback (most recent call last):
    ...
    ValueError: Error {0}:line 8, column 2: ran out of text when expecting '['
    >>> expected = "[white: ]\\n[lightblue: Director]\\n/\\n/\\n[white: ]\\n[lightgreen: Secretary]\\n/\\n/\\n[Minion #1]\\n[white: ]\\n[Minion #2]"
    >>> filename = os.path.join(dirname, "hierarchy.blk")
    >>> blocks = recursive_descent_parse(open(filename, encoding="utf8").read())
    >>> str(blocks).strip() == expected
    True
    >>> expected = "[#00CCDE: MessageBox Window\\n[lightgray: Frame\\n[white: ]\\n[white: Message text]\\n/\\n/\\n[goldenrod: OK Button]\\n[white: ]\\n[#ff0505: Cancel Button]\\n/\\n[white: ]\\n]\\n]"
    >>> filename = os.path.join(dirname, "messagebox.blk")
    >>> blocks = recursive_descent_parse(open(filename, encoding="utf8").read())
    >>> str(blocks).strip() == expected
    True
    """

    class Data:

        def __init__(self, text):
            self.text = text
            self.pos = 0
            self.line = 1
            self.column = 1
            self.brackets = 0
            self.stack = [Block.get_root_block()]

        def location(self):
            return "line {0}, column {1}".format(self.line,
                                                 self.column)

        def _advance_by_one(self):
            self.pos += 1
            if (self.pos < len(self.text) and
                self.text[self.pos] == "\n"):
                self.line += 1
                self.column = 1
            else:
                self.column += 1


        def advance_by(self, amount):
            for x in range(amount):
                self._advance_by_one()


        def advance_to_position(self, position):
            while self.pos < position:
                self._advance_by_one()


        def advance_up_to(self, characters):
            while (self.pos < len(self.text) and
                   self.text[self.pos] not in characters and
                   self.text[self.pos].isspace()):
                self._advance_by_one()
            if not self.pos < len(self.text):
                return False
            if self.text[self.pos] in characters:
                return True
            raise LexError("expected '{0}' but got '{1}'"
                           .format(characters, self.text[self.pos]))


    def parse_new_row(data):
        data.stack[-1].children.append(Block.get_new_row())
        data.advance_by(1)


    def parse_block_data(data, end):
        color = None
        colon = data.text.find(":", data.pos)
        if -1 < colon < end:
            color = data.text[data.pos:colon]
            data.advance_to_position(colon + 1)
        name = data.text[data.pos:end].strip()
        data.advance_to_position(end)
        if not name and color is None:
            block = Block.get_empty_block()
        else:
            block = Block.Block(name, color)
        data.stack[-1].children.append(block)
        return block


    def parse_block(data):
        data.advance_by(1)
        nextBlock = data.text.find("[", data.pos)
        endOfBlock = data.text.find("]", data.pos)
        if nextBlock == -1 or endOfBlock < nextBlock:
            parse_block_data(data, endOfBlock)
        else:
            block = parse_block_data(data, nextBlock)
            data.stack.append(block)
            parse(data)
            data.stack.pop()


    def parse(data):
        while data.pos < len(data.text):
            if not data.advance_up_to("[]/"):
                break
            if data.text[data.pos] == "[":
                data.brackets += 1
                parse_block(data)
            elif data.text[data.pos] == "/":
                parse_new_row(data)
            elif data.text[data.pos] == "]":
                data.brackets -= 1
                data.advance_by(1)
            else:
                raise LexError("expecting '[', ']', or '/'; "
                        "but got '{0}'".format(data.text[data.pos]))
        if data.brackets:
            raise LexError("ran out of text when expecting '{0}'"
                           .format(']' if data.brackets > 0 else '['))

    data = Data(text)
    try:
        parse(data)
    except LexError as err:
        raise ValueError("Error {{0}}:{0}: {1}".format(
                         data.location(), err))
    return data.stack[0]


def populate_children(items, stack):
    for item in items:
        if isinstance(item, Block.Block):
            stack[-1].children.append(item)
        elif isinstance(item, list) and item:
            stack.append(stack[-1].children[-1])
            populate_children(item, stack)
            stack.pop()
        elif isinstance(item, int):
            if item == EmptyBlock:
                stack[-1].children.append(Block.get_empty_block())
            else:
                for x in range(item):
                    stack[-1].children.append(Block.get_new_row())


def pyparsing_parse(text):
    """
    >>> import os
    >>> dirname = os.path.join(os.path.dirname(__file__), "data")
    >>> filename = os.path.join(dirname, "error1.blk")
    >>> pyparsing_parse(open(filename, encoding="utf8").read())
    Traceback (most recent call last):
    ...
    ValueError: Error {0}: syntax error, line 8
    >>> filename = os.path.join(dirname, "error2.blk")
    >>> pyparsing_parse(open(filename, encoding="utf8").read())
    Traceback (most recent call last):
    ...
    ValueError: Error {0}: syntax error, line 1
    >>> filename = os.path.join(dirname, "error3.blk")
    >>> pyparsing_parse(open(filename, encoding="utf8").read())
    Traceback (most recent call last):
    ...
    ValueError: Error {0}: syntax error, line 4
    >>> expected = "[white: ]\\n[lightblue: Director]\\n/\\n/\\n[white: ]\\n[lightgreen: Secretary]\\n/\\n/\\n[white: Minion #1]\\n[white: ]\\n[white: Minion #2]"
    >>> filename = os.path.join(dirname, "hierarchy.blk")
    >>> blocks = pyparsing_parse(open(filename, encoding="utf8").read())
    >>> str(blocks).strip() == expected
    True

    >>> expected = "[#00CCDE: MessageBox Window\\n[lightgray: Frame\\n[white: ]\\n[white: Message text]\\n/\\n/\\n[goldenrod: OK Button]\\n[white: ]\\n[#ff0505: Cancel Button]\\n/\\n[white: ]\\n]\\n]"
    >>> filename = os.path.join(dirname, "messagebox.blk")
    >>> blocks = pyparsing_parse(open(filename, encoding="utf8").read())
    >>> str(blocks).strip() == expected
    True
    """

    def add_block(tokens):
        return Block.Block(tokens.name, tokens.color if tokens.color
                                                     else "white")

    left_bracket, right_bracket = map(Suppress, "[]")
    new_rows = Word("/")("new_rows").setParseAction(
            lambda tokens: len(tokens.new_rows))
    name = CharsNotIn("[]/\n")("name").setParseAction(
            lambda tokens: tokens.name.strip())
    color = (Word("#", hexnums, exact=7) |
             Word(alphas, alphanums))("color")
    empty_node = (left_bracket + right_bracket).setParseAction(
            lambda: EmptyBlock)
    nodes = Forward()
    node_data = Optional(color + Suppress(":")) + Optional(name)
    node_data.setParseAction(add_block)
    node = left_bracket - node_data + nodes + right_bracket
    nodes << Group(ZeroOrMore(Optional(new_rows) +
                              OneOrMore(node | empty_node)))
    stack = [Block.get_root_block()]
    try:
        results = nodes.parseString(text, parseAll=True)
        assert len(results) == 1
        items = results.asList()[0]
        populate_children(items, stack)
    except (ParseException, ParseSyntaxException) as err:
        raise ValueError("Error {{0}}: syntax error, line "
                         "{0}".format(err.lineno))
    return stack[0]


def ply_parse(text):
    """
    >>> import os
    >>> dirname = os.path.join(os.path.dirname(__file__), "data")
    >>> filename = os.path.join(dirname, "error1.blk")
    >>> ply_parse(open(filename, encoding="utf8").read())
    Traceback (most recent call last):
    ...
    ValueError: Error {0}:line 8: unbalanced brackets []
    >>> filename = os.path.join(dirname, "error2.blk")
    >>> ply_parse(open(filename, encoding="utf8").read())
    Traceback (most recent call last):
    ...
    ValueError: Error {0}:line 2: syntax error
    >>> filename = os.path.join(dirname, "error3.blk")
    >>> ply_parse(open(filename, encoding="utf8").read())
    Traceback (most recent call last):
    ...
    ValueError: Error {0}:line 8: too many ']'s
    >>> expected = "[white: ]\\n[lightblue: Director]\\n/\\n/\\n[white: ]\\n[lightgreen: Secretary]\\n/\\n/\\n[white: Minion #1]\\n[white: ]\\n[white: Minion #2]"
    >>> filename = os.path.join(dirname, "hierarchy.blk")
    >>> blocks = ply_parse(open(filename, encoding="utf8").read())
    >>> str(blocks).strip() == expected
    True

    >>> expected = "[#00CCDE: MessageBox Window\\n[lightgray: Frame\\n[white: ]\\n[white: Message text]\\n/\\n/\\n[goldenrod: OK Button]\\n[white: ]\\n[#ff0505: Cancel Button]\\n/\\n[white: ]\\n]\\n]"
    >>> filename = os.path.join(dirname, "messagebox.blk")
    >>> blocks = ply_parse(open(filename, encoding="utf8").read())
    >>> str(blocks).strip() == expected
    True
    """
    tokens = ("NODE_START", "NODE_END", "COLOR", "NAME", "NEW_ROWS",
              "EMPTY_NODE")

    t_NODE_START = r"\["
    t_NODE_END = r"\]"
    t_COLOR = r"(?:\#[\dA-Fa-f]{6}|[a-zA-Z]\w*):"
    t_NAME = r"[^][/\n]+"
    t_NEW_ROWS = r"/+"
    t_EMPTY_NODE = r"\[\]"

    t_ignore = " \t"

    def t_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        i = line.find("\n")
        line = line if i == -1 else line[:i]
        raise LexError("syntax error: {1}".format(line))


    stack = [Block.get_root_block()]
    block = None
    brackets = 0
    lexer = ply.lex.lex()
    try:
        lexer.input(text)
        for token in lexer:
            if token.type == "NODE_START":
                brackets += 1
                block = Block.get_empty_block()
                stack[-1].children.append(block)
                stack.append(block)
            elif token.type == "NODE_END":
                brackets -= 1
                if brackets < 0:
                    raise LexError("too many ']'s")
                block = None
                stack.pop()
            elif token.type == "COLOR":
                if block is None or Block.is_new_row(block):
                    raise LexError("syntax error")
                block.color = token.value[:-1]
            elif token.type == "NAME":
                if block is None or Block.is_new_row(block):
                    raise LexError("syntax error")
                block.name = token.value
            elif token.type == "EMPTY_NODE":
                stack[-1].children.append(Block.get_empty_block())
            elif token.type == "NEW_ROWS":
                for x in range(len(token.value)):
                    stack[-1].children.append(Block.get_new_row())
        if brackets:
            raise LexError("unbalanced brackets []")
    except LexError as err:
        raise ValueError("Error {{0}}:line {0}: {1}".format(
                         token.lineno + 1, err))
    return stack[0]


def parse_options():
    parsers = "recursive ply pyparsing".split()
    parser = optparse.OptionParser(usage="""\
usage: %prog [options] infile1 [infile2 [...]]

Reads one or more 'blocks' (.blk) description file and for each one
writes an equivalent .svg file to visualize the blocks, using the same
name as the infile but with the extension changed appropriately.
""")
    parser.set_defaults(parser="recursive")
    parser.add_option("-p", "--parser", dest="parser",
            choices=parsers, help="{0} [%default]".format(
                ", ".join(parsers)))
    opts, args = parser.parse_args()

    args = [arg for arg in args if arg.endswith(".blk")]
    if not len(args):
        parser.error("at least one .blk file must be specified")
    if opts.parser == "recursive":
        parse = recursive_descent_parse
    elif opts.parser == "pyparsing":
        parse = pyparsing_parse
    elif opts.parser == "ply":
        parse = ply_parse
    return parse, args


def main():
    parse, files = parse_options()
    for file in files:
        blocks = open(file, encoding="utf8").read()
        try:
            blocks = parse(blocks)
            svg = file.replace(".blk", ".svg")
            if BlockOutput.save_blocks_as_svg(blocks, svg):
                print("Saved {0}".format(svg))
            else:
                print("Error: failed to save {0}".format(svg))
        except ValueError as err:
            print(str(err).format(file))


if __name__ == "__main__":
    main()
