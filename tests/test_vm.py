from pymonkey.compiler.compiler import Compiler
from pymonkey.evaluator.mobject import (
    MArrayObject,
    MBooleanObject,
    MHashMapObject,
    MIntegerObject,
    MNullObject,
    MObject,
    MStringObject,
    MValuedObject,
)
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

        print(vm.last_pop)
        print(value)
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
        "if (false) { 10; };": MNullObject(),
    }

    run_test(test_input)


def test_global_let() -> None:
    test_input: dict[str, MObject] = {
        "let x = 1; x;": MIntegerObject(1),
    }

    run_test(test_input)


def test_string() -> None:
    test_input: dict[str, MObject] = {
        '"Hello " + "World"': MStringObject("Hello World"),
    }

    run_test(test_input)


def test_array() -> None:
    test_input: dict[str, MObject] = {
        "[]": MArrayObject([]),
        "[1, 2]": MArrayObject([MIntegerObject(1), MIntegerObject(2)]),
        "[true, false]": MArrayObject([MBooleanObject(True), MBooleanObject(False)]),
        "[true, false][1]": MBooleanObject(False),
    }

    run_test(test_input)


def test_hashmap() -> None:
    hashmap2: dict[MValuedObject, MObject] = {
        MStringObject("one"): MIntegerObject(1),
        MStringObject("two"): MIntegerObject(2),
    }
    test_input: dict[str, MObject] = {
        "{}": MHashMapObject({}),
        '{"one": 1, "two": 2}': MHashMapObject(hashmap2),
        '{"one": 1, "two": 2}["one"]': MIntegerObject(1),
    }

    run_test(test_input)
