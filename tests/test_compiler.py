from pymonkey.code.code import Instructions, MOpcode
from pymonkey.compiler.compiler import Compiler
from pymonkey.evaluator.mobject import MIntegerObject
from pymonkey.lexer.mlexer import MLexer
from pymonkey.parser.mparser import MParser


def assert_instructions(i, compiled: Instructions, expected):
    offset = 0
    for ins, exp in zip(compiled.instructions, expected):
        operation = MOpcode(ins[0])
        operands = []
        for b in ins[1:]:
            operands.append(int(b))

        assert offset == exp[0], f"Test {i} failed: wrong offset"
        assert operation == exp[1], f"Test {i} failed: wrong operation"
        assert operands == exp[2:], f"Test {i} failed: wrong operands"

        offset += len(operands) + 1


def run_test(test_input):
    for i, (key, value) in enumerate(test_input.items()):
        instructions, constants = value
        print(instructions)
        print(constants)
        lexer = MLexer(key)
        program = MParser(lexer).parse_program()
        compiler = Compiler()
        compiler.compile(program)

        assert_instructions(i, compiler.instructions, instructions)
        assert compiler.constants == constants, f"Test {i} failed: wrong constants"


def test_integer():
    test_input = {
        "1 + 2;": [
            [[0, MOpcode.OpConstant, 0x00, 0x00], [3, MOpcode.OpConstant, 0x00, 0x01]],
            [MIntegerObject(1), MIntegerObject(2)],
        ],
    }

    run_test(test_input)
