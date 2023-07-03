import sys

from pymonkey.evaluator.mevaluator import MEvaluator
from pymonkey.lexer.mlexer import MLexer
from pymonkey.mrepl import repl
from pymonkey.parser.mparser import MParser, UnknownTokenException


def print_parser_errors(inp: str, parser: MParser) -> None:
    inp_lines = inp.split("\n")

    for err in parser.errors:
        print(f"Error: {err.msg}")
        if err.token.position is not None:
            print(
                f"-> File: {err.token.position.file}:{err.token.position.line+1}:{err.token.position.pos}"
            )
            print("   |")
            print(
                f" {err.token.position.line+1} | {inp_lines[err.token.position.line]}"
            )
            print(f"   | {'-' * (err.token.position.pos - 1)}^\n")


def print_lexer_errors(inp: str, lexer: MLexer) -> None:
    inp_lines = inp.split("\n")

    for err in lexer.errors:
        print(f"Error: {err.msg}")
        if err.token.position is not None:
            print(
                f"-> File: {err.token.position.file}:{err.token.position.line+1}:{err.token.position.pos}"
            )
            print("   |")
            print(
                f" {err.token.position.line+1} | {inp_lines[err.token.position.line]}"
            )
            print(f"   | {'-' * (err.token.position.pos - 1)}^\n")


def main() -> None:
    if len(sys.argv) == 1:
        repl()

    else:
        with open(sys.argv[1], "r") as file:
            inp = file.read()

        lexer = MLexer(inp)
        parser = MParser(lexer)
        try:
            program = parser.parse_program()
        except UnknownTokenException:
            print_parser_errors(inp, parser)
            return
        if lexer.errors:
            print_lexer_errors(inp, lexer)
            return
        evaluation = MEvaluator(program).evaluate()

        print(evaluation)


if __name__ == "__main__":
    main()
