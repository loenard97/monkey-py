import sys

from pymonkey.mlexer import MLexer
from pymonkey.mobject import MEnvironment
from pymonkey.mparser import Parser
from pymonkey.mevaluator import eval


def main():
    with open(sys.argv[1], 'r') as file:
        inp = file.read()

    lexer = MLexer(inp)
    parser = Parser(lexer)

    program = parser.parse_program()
    env = MEnvironment()

    evaluated = eval(program, env)

    print(evaluated)


if __name__ == '__main__':
    main()

