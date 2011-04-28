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

    FORMULA     ::= ('forall' | 'exists') SYMBOL ':' FORMULA
                 |  FORMULA '->' FORMULA      # right associative
                 |  FORMULA '|' FORMULA       # left associative
                 |  FORMULA '&' FORMULA       # left associative
                 |  '~' FORMULA
                 |  '(' FORMULA ')'
                 |  TERM '=' TERM
                 |  'true'
                 |  'false'
    TERM        ::= SYMBOL | SYMBOL '(' TERM_LIST ')'
    TERM_LIST   ::= TERM | TERM ',' TERM_LIST
    SYMBOL      ::= [a-zA-Z]\w*
"""

import ply.lex
import ply.yacc
try:
    from pyparsing import (alphanums, alphas, delimitedList, Forward,
            Group, Keyword, Literal, opAssoc, operatorPrecedence,
            ParserElement, ParseException, ParseSyntaxException, Suppress,
            Word)
except ImportError:
    from pyparsing_py3 import (alphanums, alphas, delimitedList, Forward,
            Group, Keyword, Literal, opAssoc, operatorPrecedence,
            ParserElement, ParseException, ParseSyntaxException, Suppress,
            Word)
ParserElement.enablePackrat()


def pyparsing_parse(text):
    """
    >>> formula = "a = b"
    >>> print(pyparsing_parse(formula))
    ['a', '=', 'b']
    >>> formula = "forall x: a = b"
    >>> print(pyparsing_parse(formula))
    ['forall', 'x', ['a', '=', 'b']]
    >>> formula = "a & b"
    >>> print(pyparsing_parse(formula))
    ['a', '&', 'b']
    >>> formula = "~true -> ~b = c"
    >>> print(pyparsing_parse(formula))
    [['~', 'true'], '->', ['~', ['b', '=', 'c']]]
    >>> formula = "~true -> ~(b = c)"
    >>> print(pyparsing_parse(formula))
    [['~', 'true'], '->', ['~', ['b', '=', 'c']]]
    >>> formula = "exists y: a -> b"
    >>> print(pyparsing_parse(formula))
    ['exists', 'y', ['a', '->', 'b']]
    >>> formula = "forall x: exists y: a = b"
    >>> print(pyparsing_parse(formula))
    ['forall', 'x', ['exists', 'y', ['a', '=', 'b']]]
    >>> formula = "forall x: exists y: a = b -> a = b & ~ a = b -> a = b"
    >>> print(pyparsing_parse(formula))
    ['forall', 'x', ['exists', 'y', [['a', '=', 'b'], '->', [[['a', '=', 'b'], '&', ['~', ['a', '=', 'b']]], '->', ['a', '=', 'b']]]]]
    >>> formula = "(forall x: exists y: a = b) -> a = b & ~ a = b -> a = b"
    >>> print(pyparsing_parse(formula))
    [['forall', 'x', ['exists', 'y', ['a', '=', 'b']]], '->', [[['a', '=', 'b'], '&', ['~', ['a', '=', 'b']]], '->', ['a', '=', 'b']]]
    >>> formula = "(forall x: exists y: true) -> true & ~ true -> true"
    >>> print(pyparsing_parse(formula))
    [['forall', 'x', ['exists', 'y', 'true']], '->', [['true', '&', ['~', 'true']], '->', 'true']]
    >>> formula = "a = b -> c = d & e = f"
    >>> result1 = pyparsing_parse(formula)
    >>> formula = "(a = b) -> (c = d & e = f)"
    >>> result2 = pyparsing_parse(formula)
    >>> result1 == result2
    True
    >>> result1
    [['a', '=', 'b'], '->', [['c', '=', 'd'], '&', ['e', '=', 'f']]]
    >>> formula = "forall x: exists y: true -> true & true | ~ true"
    >>> print(pyparsing_parse(formula))
    ['forall', 'x', ['exists', 'y', ['true', '->', [['true', '&', 'true'], '|', ['~', 'true']]]]]
    >>> formula = "~ true | true & true -> forall x: exists y: true"
    >>> print(pyparsing_parse(formula))
    [[['~', 'true'], '|', ['true', '&', 'true']], '->', ['forall', 'x', ['exists', 'y', 'true']]]
    >>> formula = "true & forall x: x = x"
    >>> print(pyparsing_parse(formula))
    ['true', '&', ['forall', 'x', ['x', '=', 'x']]]
    >>> formula = "true & (forall x: x = x)" # same as previous
    >>> print(pyparsing_parse(formula))
    ['true', '&', ['forall', 'x', ['x', '=', 'x']]]
    >>> formula = "forall x: x = x & true"
    >>> print(pyparsing_parse(formula))
    ['forall', 'x', [['x', '=', 'x'], '&', 'true']]
    >>> formula = "(forall x: x = x) & true" # different to previous
    >>> print(pyparsing_parse(formula))
    [['forall', 'x', ['x', '=', 'x']], '&', 'true']
    >>> formula = "forall x: = x & true"
    >>> print(pyparsing_parse(formula))
    Syntax error:
    forall x: = x & true
           ^
    []
    """
    left_parenthesis, right_parenthesis, colon = map(Suppress, "():")
    forall = Keyword("forall")
    exists = Keyword("exists")
    implies = Literal("->")
    or_ = Literal("|")
    and_ = Literal("&")
    not_ = Literal("~")
    equals = Literal("=")
    boolean = Keyword("false") | Keyword("true")
    symbol = Word(alphas, alphanums)
    term = Forward()
    term << (Group(symbol + Group(left_parenthesis +
                   delimitedList(term) + right_parenthesis)) | symbol)
    formula = Forward()
    forall_expression = Group(forall + symbol + colon + formula)
    exists_expression = Group(exists + symbol + colon + formula)
    operand = forall_expression | exists_expression | boolean | term
    formula << operatorPrecedence(operand, [
                                  (equals, 2, opAssoc.LEFT),
                                  (not_, 1, opAssoc.RIGHT),
                                  (and_, 2, opAssoc.LEFT),
                                  (or_, 2, opAssoc.LEFT),
                                  (implies, 2, opAssoc.RIGHT)])
    try:
        result = formula.parseString(text, parseAll=True)
        assert len(result) == 1
        return result[0].asList()
    except (ParseException, ParseSyntaxException) as err:
        print("Syntax error:\n{0.line}\n{1}^".format(err,
              " " * (err.column - 1)))
        return []


def ply_parse(text):
    """
    >>> formula = "a = b"
    >>> print(ply_parse(formula))
    ['a', '=', 'b']
    >>> formula = "forall x: a = b"
    >>> print(ply_parse(formula))
    ['forall', 'x', ['a', '=', 'b']]
    >>> formula = "a & b"
    >>> print(ply_parse(formula))
    ['a', '&', 'b']
    >>> formula = "~true -> ~b = c"
    >>> print(ply_parse(formula))
    [['~', 'true'], '->', ['~', ['b', '=', 'c']]]
    >>> formula = "~true -> ~(b = c)"
    >>> print(ply_parse(formula))
    [['~', 'true'], '->', ['~', ['b', '=', 'c']]]
    >>> formula = "exists y: a -> b"
    >>> print(ply_parse(formula))
    ['exists', 'y', ['a', '->', 'b']]
    >>> formula = "forall x: exists y: a = b"
    >>> print(ply_parse(formula))
    ['forall', 'x', ['exists', 'y', ['a', '=', 'b']]]
    >>> formula = "forall x: exists y: a = b -> a = b & ~ a = b -> a = b"
    >>> print(ply_parse(formula))
    ['forall', 'x', ['exists', 'y', [['a', '=', 'b'], '->', [[['a', '=', 'b'], '&', ['~', ['a', '=', 'b']]], '->', ['a', '=', 'b']]]]]
    >>> formula = "(forall x: exists y: a = b) -> a = b & ~ a = b -> a = b"
    >>> print(ply_parse(formula))
    [['forall', 'x', ['exists', 'y', ['a', '=', 'b']]], '->', [[['a', '=', 'b'], '&', ['~', ['a', '=', 'b']]], '->', ['a', '=', 'b']]]
    >>> formula = "(forall x: exists y: true) -> true & ~ true -> true"
    >>> print(ply_parse(formula))
    [['forall', 'x', ['exists', 'y', 'true']], '->', [['true', '&', ['~', 'true']], '->', 'true']]
    >>> formula = "a = b -> c = d & e = f"
    >>> result1 = ply_parse(formula)
    >>> formula = "(a = b) -> (c = d & e = f)"
    >>> result2 = ply_parse(formula)
    >>> result1 == result2
    True
    >>> result1
    [['a', '=', 'b'], '->', [['c', '=', 'd'], '&', ['e', '=', 'f']]]
    >>> formula = "forall x: exists y: true -> true & true | ~ true"
    >>> print(ply_parse(formula))
    ['forall', 'x', ['exists', 'y', ['true', '->', [['true', '&', 'true'], '|', ['~', 'true']]]]]
    >>> formula = "~ true | true & true -> forall x: exists y: true"
    >>> print(ply_parse(formula))
    [[['~', 'true'], '|', ['true', '&', 'true']], '->', ['forall', 'x', ['exists', 'y', 'true']]]
    >>> formula = "true & forall x: x = x"
    >>> print(ply_parse(formula))
    ['true', '&', ['forall', 'x', ['x', '=', 'x']]]
    >>> formula = "true & (forall x: x = x)" # same as previous
    >>> print(ply_parse(formula))
    ['true', '&', ['forall', 'x', ['x', '=', 'x']]]
    >>> formula = "forall x: x = x & true"
    >>> print(ply_parse(formula))
    ['forall', 'x', [['x', '=', 'x'], '&', 'true']]
    >>> formula = "(forall x: x = x) & true" # different to previous
    >>> print(ply_parse(formula))
    [['forall', 'x', ['x', '=', 'x']], '&', 'true']
    >>> formula = "forall x: = x & true"
    >>> print(ply_parse(formula))
    Syntax error, line 2: EQUALS
    []
    """
    keywords = {"exists": "EXISTS", "forall": "FORALL",
                "true": "TRUE", "false": "FALSE"}
    tokens = (["SYMBOL", "COLON", "COMMA", "LPAREN", "RPAREN",
               "EQUALS", "NOT", "AND", "OR", "IMPLIES"] +
              list(keywords.values()))

    def t_SYMBOL(t):
        r"[a-zA-Z]\w*"
        t.type = keywords.get(t.value, "SYMBOL")
        return t


    t_EQUALS = r"="
    t_NOT = r"~"
    t_AND = r"&"
    t_OR = r"\|"
    t_IMPLIES = r"->"
    t_COLON = r":"
    t_COMMA = r","
    t_LPAREN = r"\("
    t_RPAREN = r"\)"

    t_ignore = " \t\n"

    def t_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        i = line.find("\n")
        line = line if i == -1 else line[:i]
        raise ValueError("Syntax error, line {0}: {1}"
                         .format(t.lineno + 1, line))
    
    def p_formula_quantifier(p):
        """FORMULA : FORALL SYMBOL COLON FORMULA
                   | EXISTS SYMBOL COLON FORMULA"""
        p[0] = [p[1], p[2], p[4]]

    def p_formula_binary(p):
        """FORMULA : FORMULA IMPLIES FORMULA
                   | FORMULA OR FORMULA
                   | FORMULA AND FORMULA"""
        p[0] = [p[1], p[2], p[3]]

    def p_formula_not(p):
        "FORMULA : NOT FORMULA"
        p[0] = [p[1], p[2]]

    def p_formula_boolean(p):
        """FORMULA : FALSE
                   | TRUE"""
        p[0] = p[1]

    def p_formula_group(p):
        "FORMULA : LPAREN FORMULA RPAREN"
        p[0] = p[2]

    def p_formula_symbol(p):
        "FORMULA : SYMBOL"
        p[0] = p[1]

    def p_formula_equals(p):
        "FORMULA : TERM EQUALS TERM"
        p[0] = [p[1], p[2], p[3]]

    def p_term(p):
        """TERM : SYMBOL LPAREN TERMLIST RPAREN
                | SYMBOL"""
        p[0] = p[1] if len(p) == 2 else [p[1], p[3]]

    def p_termlist(p):
        """TERMLIST : TERM COMMA TERMLIST
                    | TERM"""
        p[0] = p[1] if len(p) == 2 else [p[1], p[3]]
       
    def p_error(p):
        if p is None:
            raise ValueError("Unknown error")
        raise ValueError("Syntax error, line {0}: {1}".format(
                         p.lineno + 1, p.type))

# from lowest to highest precedence!
    precedence = (("nonassoc", "FORALL", "EXISTS"),
                  ("right", "IMPLIES"),
                  ("left", "OR"),
                  ("left", "AND"),
                  ("right", "NOT"),
                  ("nonassoc", "EQUALS"))

    lexer = ply.lex.lex()
    parser = ply.yacc.yacc()
    try:
        return parser.parse(text, lexer=lexer)
    except ValueError as err:
        print(err)
        return []
    

if __name__ == "__main__":
    import doctest
    doctest.testmod()
