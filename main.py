from pymonkey.lexer import Lexer
from pymonkey.parser import Parser


def main():
    input = "add(x, y);"
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()

    print(program)


if __name__ == '__main__':
    main()

