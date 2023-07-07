from pymonkey.compiler.compiler import Compiler
from pymonkey.evaluator.mobject import MBooleanObject, MIntegerObject, MObject
from pymonkey.lexer.mlexer import MLexer
from pymonkey.parser.mparser import MParser
from pymonkey.vm.vm import VM


def run_test(test_input: dict[str, MObject]) -> None:
    for i, (key, value) in enumerate(test_input.items()):
        lexer = MLexer(key)
        program = MParser(lexer).parse_program()

        compiler = Compiler()
        compiler.compile(program)

        vm = VM(compiler.bytecode())
        vm.run()

        assert vm.last_pop == value, f"Test {i} failed"


def test_integer() -> None:
    test_input: dict[str, MObject] = {
        "1;": MIntegerObject(1),
        "2;": MIntegerObject(2),
        "1 + 2;": MIntegerObject(3),
        "2 - 1;": MIntegerObject(1),
        "4 * 2;": MIntegerObject(8),
        "4 / 2;": MIntegerObject(2),
    }

    run_test(test_input)


def test_boolean() -> None:
    test_input: dict[str, MObject] = {
        "true;": MBooleanObject(True),
        "false;": MBooleanObject(False),
        "1 < 2;": MBooleanObject(True),
        "1 > 2;": MBooleanObject(False),
        "1 == 2;": MBooleanObject(False),
        "1 != 2;": MBooleanObject(True),
    }

    run_test(test_input)


def test_prefix() -> None:
    test_input: dict[str, MObject] = {
        "-2;": MIntegerObject(-2),
        "!true;": MBooleanObject(False),
    }

    run_test(test_input)


def test_jumps() -> None:
    test_input: dict[str, MObject] = {
        "if (true) { 10; };": MIntegerObject(10),
        "if (true) { 10; } else { 20; };": MIntegerObject(10),
        "if (false) { 10; } else { 20; };": MIntegerObject(20),
    }

    run_test(test_input)
