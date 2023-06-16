from src.lexer import Lexer
from src.parser import Parser


def main():
    input = "let x = 3;"
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()

    print(program)


if __name__ == '__main__':
    main()

