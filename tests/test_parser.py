from pymonkey.parser.mparser import MLexer, MParser


def run_parser(test: list[str]) -> None:
    for i, t in enumerate(test):
        lexer = MLexer(t)
        parser = MParser(lexer)
        program = parser.parse_program()

        assert str(program) == t, f"Test {i} failed: {t}"


def test_let() -> None:
    test_input = [
        "let x = 3;",
        "let y = true;",
        "let foobar = y;",
    ]

    run_parser(test_input)


def test_return() -> None:
    test_input = [
        "return 1;",
        "return true;",
        "return foobar;",
    ]

    run_parser(test_input)


def test_prefix() -> None:
    test_input = [
        "!5;",
        "-15;",
        "!foobar;",
        "-foobar;",
        "!true;",
        "!false;",
    ]

    run_parser(test_input)


def test_infix() -> None:
    test_input = [
        "5 + 5;",
        "5 - 5;",
        "5 * 5;",
        "5 / 5;",
        "5 > 5;",
        "5 < 5;",
        "5 == 5;",
        "5 != 5;",
    ]

    run_parser(test_input)


def test_math() -> None:
    test_input = [
        "-a * b;",
        "!-a;",
        "a + b + c;",
        "a + b - c;",
        "a * b * c;",
        "a * b / c;",
        "a + b / c;",
        "a + b * c + d / e - f;",
        # "3 + 4; -5 * 5;",
        "5 > 4 == 3 < 4;",
        "5 < 4 != 3 > 4;",
        "3 + 4 * 5 == 3 * 1 + 4 * 5;",
        "true;",
        "false;",
        "3 > 5 == false;",
        "3 < 5 == true;",
        # "1 + (2 + 3) + 4;",
        # "(5 + 5) * 2;",
        # "2 / (5 + 5);",
        # "(5 + 5) * 2 * (5 + 5);",
        # "-(5 + 5);",
        # "!(true == true);",
        # "a + add(b * c) + d;",
        # "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8));",
        # "add(a + b + c * d / f + g);",
    ]

    run_parser(test_input)


def test_if() -> None:
    test_input = [
        "if (true) { return 1; };",
        "if (false) { return 1; } else { return 0; };",
    ]

    run_parser(test_input)


def test_function() -> None:
    test_input = [
        "fn(x, y) { x + y; };",
        "add(x, y);",
    ]

    run_parser(test_input)


def test_string() -> None:
    inp = ['"hello world";']

    run_parser(inp)


def test_array() -> None:
    inp = [
        "[1, true];",
        "[];",
    ]

    run_parser(inp)


def test_index() -> None:
    inp = ["arr[1 + 1];"]

    run_parser(inp)


def test_hashmap() -> None:
    test_input = [
        '{"one": 1, "two": 2, "three": 3};',
        "{};",
    ]

    run_parser(test_input)
