from pymonkey.compiler.compiler import Compiler
from pymonkey.evaluator.mobject import MIntegerObject
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

        assert vm.stack_top() == value, f"Test {i} failed"


def test_integer():
    test_input = {
        "1;": MIntegerObject(1),
        "2;": MIntegerObject(2),
        "1 + 2;": MIntegerObject(3),
    }

    run_test(test_input)
