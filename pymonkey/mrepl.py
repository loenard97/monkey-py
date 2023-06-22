import sys

from pymonkey.mevaluator import eval
from pymonkey.mlexer import MLexer
from pymonkey.mobject import MEnvironment
from pymonkey.mparser import Parser


def repl():
    print("Monkey REPL: (type exit() to close REPL)")

    for line in sys.stdin:
        if line == "exit()\n":
            break

        lexer = MLexer(line)
        parser = Parser(lexer)
        program = parser.parse_program()
        env = MEnvironment()
        evaluation = eval(program, env)

        print(f"-> {evaluation}")


if __name__ == "__main__":
    repl()
