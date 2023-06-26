from typing import Dict

from pymonkey.evaluator.mevaluator import MEvaluator
from pymonkey.evaluator.mobject import (
    MArrayObject,
    MBooleanObject,
    MIntegerObject,
    MNullObject,
    MObject,
    MStringObject,
)
from pymonkey.parser.mparser import MLexer, MParser


def evaluate_test(test_dict: Dict[str, MObject]):
    for i, (in_test, out_test) in enumerate(test_dict.items()):
        try:
            lexer = MLexer(in_test)
            program = MParser(lexer).parse_program()
            evaluation = MEvaluator(program).evaluate()
        except Exception as err:
            assert False, f"Test {i} failed: Error: {err}"
        else:
            assert evaluation == out_test, f"Test {i} failed: {in_test} != {out_test}"


def test_int():
    tests: Dict[str, MObject] = {
        "5;": MIntegerObject(5),
        "10;": MIntegerObject(10),
        "-5;": MIntegerObject(-5),
        "-10;": MIntegerObject(-10),
        "5 + 5 + 5 + 5 - 10;": MIntegerObject(10),
        "2 * 2 * 2 * 2 * 2;": MIntegerObject(32),
        "-50 + 100 + -50;": MIntegerObject(0),
        "5 * 2 + 10;": MIntegerObject(20),
        "5 + 2 * 10;": MIntegerObject(25),
        "20 + 2 * -10;": MIntegerObject(0),
        "50 / 2 * 2 + 10;": MIntegerObject(60),
        "2 * (5 + 10);": MIntegerObject(30),
        "3 * 3 * 3 + 10;": MIntegerObject(37),
        "3 * (3 * 3) + 10;": MIntegerObject(37),
        "(5 + 10 * 2 + 15 / 3) * 2 + -10;": MIntegerObject(50),
    }

    evaluate_test(tests)


def test_bool():
    tests: Dict[str, MObject] = {
        "true;": MBooleanObject(True),
        "false;": MBooleanObject(False),
        "1 < 2;": MBooleanObject(True),
        "1 > 2;": MBooleanObject(False),
        "1 < 1;": MBooleanObject(False),
        "1 > 1;": MBooleanObject(False),
        "1 == 1;": MBooleanObject(True),
        "1 != 1;": MBooleanObject(False),
        "1 == 2;": MBooleanObject(False),
        "1 != 2;": MBooleanObject(True),
        "true == true;": MBooleanObject(True),
        "false == false;": MBooleanObject(True),
        "true == false;": MBooleanObject(False),
        "true != false;": MBooleanObject(True),
        "false != true;": MBooleanObject(True),
        "(1 < 2) == true;": MBooleanObject(True),
        "(1 < 2) == false;": MBooleanObject(False),
        "(1 > 2) == true;": MBooleanObject(False),
        "(1 > 2) == false;": MBooleanObject(True),
    }

    evaluate_test(tests)


def test_bang():
    tests: Dict[str, MObject] = {
        "!true;": MBooleanObject(False),
        "!false;": MBooleanObject(True),
        "!5;": MBooleanObject(False),
        "!!true;": MBooleanObject(True),
        "!!false;": MBooleanObject(False),
        "!!5;": MBooleanObject(True),
    }

    evaluate_test(tests)


def test_if():
    tests: Dict[str, MObject] = {
        "if (true) { 10 };": MIntegerObject(10),
        "if (false) { 10 };": MNullObject(),
        "if (1) { 10 };": MIntegerObject(10),
        "if (1 < 2) { 10 };": MIntegerObject(10),
        "if (1 > 2) { 10 };": MNullObject(),
        "if (1 > 2) { 10 } else { 20 };": MIntegerObject(20),
        "if (1 < 2) { 10 } else { 20 };": MIntegerObject(10),
    }

    evaluate_test(tests)


def test_return():
    tests: Dict[str, MObject] = {
        "return 10;": MIntegerObject(10),
        "return 10; 9;": MIntegerObject(10),
        "return 2 * 5; 9;": MIntegerObject(10),
        "9; return 2 * 5; 9;": MIntegerObject(10),
        "if (10 > 1) { return 10; };": MIntegerObject(10),
    }

    evaluate_test(tests)


def test_let():
    tests: Dict[str, MObject] = {
        "let a = 5; a;": MIntegerObject(5),
        "let a = 5 * 5; a;": MIntegerObject(25),
        "let a = 5; let b = a; b;": MIntegerObject(5),
        "let a = 5; let b = a; let c = a + b + 5; c;": MIntegerObject(15),
    }

    evaluate_test(tests)


def test_fn():
    tests: Dict[str, MObject] = {
        "let identity = fn(x) { x; }; identity(5);": MIntegerObject(5),
        "let identity = fn(x) { return x; }; identity(5);": MIntegerObject(5),
        "let double = fn(x) { x * 2; }; double(5);": MIntegerObject(10),
        "let add = fn(x, y) { x + y; }; add(5, 5);": MIntegerObject(10),
        "let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));": (MIntegerObject(20)),
        "fn(x) { x; }(5)": MIntegerObject(5),
    }

    evaluate_test(tests)


def test_string():
    tests: Dict[str, MObject] = {
        '"Hello World!";': MStringObject("Hello World!"),
        '"Hello" + " " + "World" + "!"': MStringObject("Hello World!"),
    }

    evaluate_test(tests)


def test_builtin():
    tests: Dict[str, MObject] = {
        'len("Hello World!")': MIntegerObject(12),
    }

    evaluate_test(tests)


def test_env():
    tests: Dict[str, MObject] = {
        "let first = 10;"
        "let second = 10;"
        "let third = 10;"
        "let ourFunction = fn(first) { let second = 20; return first + second; }; "
        "ourFunction(20) + first + second + third;": MIntegerObject(70),
    }

    evaluate_test(tests)


def test_array():
    tests: Dict[str, MObject] = {
        "[1, 2 * 2, 3 + 3];": MArrayObject(
            [MIntegerObject(1), MIntegerObject(4), MIntegerObject(6)]
        ),
        "[1, 2, 3][0];": MIntegerObject(1),
        "[1, 2, 3][2];": MIntegerObject(3),
        "let i = 0; [1][i];": MIntegerObject(1),
        "[1, 2, 3][1 + 1];": MIntegerObject(3),
        "[1, 2, 3][-1];": MNullObject(),
        "[1, 2, 3][3];": MNullObject(),
    }

    evaluate_test(tests)


def test_hashmap():
    tests: Dict[str, MObject] = {
        '{"one": 1}["one"]': MIntegerObject(1),
        'let hm = {"one": 1}; hm["one"];': MIntegerObject(1),
        'let hm = {}; hm["one"];': MNullObject(),
    }

    evaluate_test(tests)
