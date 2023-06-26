import sys

from pymonkey.evaluator.mevaluator import MEvaluator
from pymonkey.lexer.mlexer import MLexer
from pymonkey.parser.mparser import MParser


def repl():
    print("Monkey REPL: (type exit() to close REPL)")

    for line in sys.stdin:
        if line == "exit()\n":
            break

        lexer = MLexer(line)
        program = MParser(lexer).parse_program()
        evaluation = MEvaluator(program).evaluate()

        print(f"-> {evaluation}")


if __name__ == "__main__":
    repl()
