from pymonkey.compiler.compiler import Compiler
from pymonkey.evaluator.mobject import MBooleanObject, MIntegerObject
from pymonkey.lexer.mlexer import MLexer
from pymonkey.parser.mparser import MParser
from pymonkey.vm.vm import VM


def run_test(test_input):
    for i, (key, value) in enumerate(test_input.items()):
        lexer = MLexer(key)
        program = MParser(lexer).parse_program()

        compiler = Compiler()
        compiler.compile(program)

        vm = VM(compiler.bytecode())
        vm.run()

        assert vm.last_pop == value, f"Test {i} failed"


def test_integer():
    test_input = {
        "1;": MIntegerObject(1),
        "2;": MIntegerObject(2),
        "1 + 2;": MIntegerObject(3),
        "2 - 1;": MIntegerObject(1),
        "4 * 2;": MIntegerObject(8),
        "4 / 2;": MIntegerObject(2),
    }

    run_test(test_input)


def test_boolean():
    test_input = {
        "true;": MBooleanObject(True),
        "false;": MBooleanObject(False),
    }

    run_test(test_input)
