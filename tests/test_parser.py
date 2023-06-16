import pytest

from pymonkey.parser import Lexer, Parser


def test_parser():
    input = "let x = 3;"
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()

    assert str(program) == "let x = 3"

