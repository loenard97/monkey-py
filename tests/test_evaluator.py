from pymonkey.object import BooleanObject, Environment, IntegerObject, NullObject
from pymonkey.parser import Lexer, Parser
from pymonkey.evaluator import eval


def evaluate_test(test_dict: dict):
    for i, (in_test, out_test) in enumerate(test_dict.items()):
        try:
            lexer = Lexer(in_test)
            parser = Parser(lexer)
            program = parser.parse_program()
            env = Environment()
        
            eval(program, env)
        except Exception as err:
            assert False, f"Test {i} failed: Error: {err}"
        else:
            assert eval(program, env) == out_test, f"Test {i} failed: {in_test} {out_test}"


def test_int():
    tests = {
        "5;": IntegerObject(5),
        "10;": IntegerObject(10),
        "-5;": IntegerObject(-5),
        "-10;": IntegerObject(-10),
        "5 + 5 + 5 + 5 - 10;": IntegerObject(10),
        "2 * 2 * 2 * 2 * 2;": IntegerObject(32),
        "-50 + 100 + -50;": IntegerObject(0),
        "5 * 2 + 10;": IntegerObject(20),
        "5 + 2 * 10;": IntegerObject(25),
        "20 + 2 * -10;": IntegerObject(0),
        "50 / 2 * 2 + 10;": IntegerObject(60),
        "2 * (5 + 10);": IntegerObject(30),
        "3 * 3 * 3 + 10;": IntegerObject(37),
        "3 * (3 * 3) + 10;": IntegerObject(37),
        "(5 + 10 * 2 + 15 / 3) * 2 + -10;": IntegerObject(50),
    }

    evaluate_test(tests)


def test_bool():
    tests = {
        "true;": BooleanObject(True),
        "false;": BooleanObject(False),
        "1 < 2;": BooleanObject(True),
        "1 > 2;": BooleanObject(False),
        "1 < 1;": BooleanObject(False),
        "1 > 1;": BooleanObject(False),
        "1 == 1;": BooleanObject(True),
        "1 != 1;": BooleanObject(False),
        "1 == 2;": BooleanObject(False),
        "1 != 2;": BooleanObject(True),
        "true == true;": BooleanObject(True),
        "false == false;": BooleanObject(True),
        "true == false;": BooleanObject(False),
        "true != false;": BooleanObject(True),
        "false != true;": BooleanObject(True),
        "(1 < 2) == true;": BooleanObject(True),
        "(1 < 2) == false;": BooleanObject(False),
        "(1 > 2) == true;": BooleanObject(False),
        "(1 > 2) == false;": BooleanObject(True),
    }

    evaluate_test(tests)


def test_bang():
    tests = {
        "!true;": BooleanObject(False),
        "!false;": BooleanObject(True),
        "!5;": BooleanObject(False),
        "!!true;": BooleanObject(True),
        "!!false;": BooleanObject(False),
        "!!5;": BooleanObject(True),
    }

    evaluate_test(tests)


def test_if():
    tests = {
        "if (true) { 10 };": IntegerObject(10),
        "if (false) { 10 };": NullObject(),
        "if (1) { 10 };": IntegerObject(10),
        "if (1 < 2) { 10 };": IntegerObject(10),
        "if (1 > 2) { 10 };": NullObject(),
        "if (1 > 2) { 10 } else { 20 };": IntegerObject(20),
        "if (1 < 2) { 10 } else { 20 };": IntegerObject(10),
    }

    evaluate_test(tests)


def test_return():
    tests = {
        "return 10;": 10,
        "return 10; 9;": 10,
        "return 2 * 5; 9;": 10,
        "9; return 2 * 5; 9;": 10,
        "if (10 > 1) { return 10; };": 10,
    }

    evaluate_test(tests)

