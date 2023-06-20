from pymonkey.lexer import Lexer
from pymonkey.object import Environment
from pymonkey.parser import Parser
from pymonkey.evaluator import eval


def main():
    input = "1 + ( 2 + 3 ) + 4;"
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()

    print(program)


if __name__ == '__main__':
    main()

