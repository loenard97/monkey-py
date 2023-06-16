from ..src.parser import Lexer, Parser


def test_parser():
    input = "let x = 3;"
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()

    print(program)


if __name__ == "__main__":
    test_parser()

