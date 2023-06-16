from src.lexer import Lexer


def main():
    input = "let x = 3;"
    lex = Lexer(input)

    for tok in lex:
        print(tok)


if __name__ == '__main__':
    main()

