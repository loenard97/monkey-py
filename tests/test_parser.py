from pymonkey.parser import Lexer, Parser


def test_let():
    input = [
        "let x = 3;",
        "let y = true;",
        "let foobar = y;",
    ]

    for e in input:
        run_parser(e)


def test_return():
    input = [
        "return 1;",
        "return true;",
        "return foobar;",
    ]

    for e in input:
        run_parser(e)


def test_prefix():
    input = [
        "!5;",
        "-15;",
        "!foobar;",
        "-foobar;",
        "!true;",
        "!false;",
    ]

    for e in input:
        run_parser(e)


def test_infix():
    input = [
        "5 + 5;",
        "5 - 5;",
        "5 * 5;",
        "5 / 5;",
        "5 > 5;",
        "5 < 5;",
        "5 == 5;",
        "5 != 5;",
    ]

    for e in input:
        run_parser(e)


def test_if():
    input = [
        "if (true) { return 1; };",
        "if (false) { return 1; } else { return 0; };",
    ]
    
    for e in input:
        run_parser(e)


def test_function():
    input = [
        "fn(x, y) { x + y; };",
        "add(x, y);",
    ]

    for e in input:
        run_parser(e)


def run_parser(input: str):
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert str(program) == input

