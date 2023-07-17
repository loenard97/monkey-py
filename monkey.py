import sys

from pymonkey.compiler.compiler import Compiler
from pymonkey.evaluator.mevaluator import MEvaluator
from pymonkey.lexer.mlexer import MLexer
from pymonkey.mrepl import repl
from pymonkey.parser.mparser import MParser, UnknownTokenException
from pymonkey.vm.vm import VM


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


def build(in_file_path: str, out_file_path: str = "a.mb") -> None:
    with open(in_file_path, "r") as file:
        input_ = file.read()

    lexer = MLexer(input_)
    parser = MParser(lexer)
    try:
        program = parser.parse_program()
    except UnknownTokenException:
        parser = MParser(lexer)
    try:
        program = parser.parse_program()
    except UnknownTokenException:
        print_parser_errors(input_, parser)
        return

    compiler = Compiler()
    compiler.compile(program)
    bytecode = compiler.bytecode()
    bytecode.to_pickle(out_file_path)

    print("finished building", out_file_path)


def main() -> None:
    # start repl if no args
    if len(sys.argv) == 1:
        repl()
        return

    # build system
    if sys.argv[1] == "build":
        build(in_file_path=sys.argv[2], out_file_path=sys.argv[3])
        return

    # run file in vm
    if sys.argv[1].endswith(".mo") or sys.argv[1].endswith(".monkey"):
        with open(sys.argv[1], "r") as file:
            input_ = file.read()

        # run monkey file
        lexer = MLexer(input_)
        parser = MParser(lexer)
        try:
            program = parser.parse_program()
        except UnknownTokenException:
            print_parser_errors(input_, parser)
            return
        if lexer.errors:
            print_lexer_errors(input_, lexer)
            return
        evaluation = MEvaluator(program).evaluate()

        print(evaluation)

    else:
        # run byte file
        vm = VM.from_bytecode_pickle(sys.argv[1])
        vm.run()
        print(vm.last_pop)


if __name__ == "__main__":
    main()
