import sys

from pymonkey.mevaluator import MEvaluator
from pymonkey.mlexer import MLexer
from pymonkey.mparser import MParser
from pymonkey.mrepl import repl


def main():
    if len(sys.argv) == 1:
        repl()

    else:
        with open(sys.argv[1], "r") as file:
            inp = file.read()

        lexer = MLexer(inp)
        program = MParser(lexer).parse_program()
        evaluation = MEvaluator(program).evaluate()

        print(evaluation)


if __name__ == "__main__":
    main()
