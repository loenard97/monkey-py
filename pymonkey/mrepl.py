import sys

from pymonkey.mlexer import MLexer
from pymonkey.mobject import MEnvironment
from pymonkey.mparser import Parser
from pymonkey.mevaluator import eval


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



if __name__ == '__main__':
    repl()

