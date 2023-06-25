from pymonkey.lexer.mlexer import MLexer
from pymonkey.lexer.mtoken import (
    ASSIGN,
    ASTERISK,
    BANG,
    COMMA,
    EQUAL,
    GREATER,
    KEYWORD,
    LBRACE,
    LBRACKET,
    LESSER,
    LPAREN,
    MINUS,
    NOTEQUAL,
    NUMBER,
    PLUS,
    RBRACE,
    RBRACKET,
    RPAREN,
    SEMICOLON,
    SLASH,
    STRING,
    TRUE,
    MToken,
)


def test_token():
    input = "=+(){},;-!/*<>"
    tokens = [
        MToken(ASSIGN, ASSIGN),
        MToken(PLUS, PLUS),
        MToken(LPAREN, LPAREN),
        MToken(RPAREN, RPAREN),
        MToken(LBRACE, LBRACE),
        MToken(RBRACE, RBRACE),
        MToken(COMMA, COMMA),
        MToken(SEMICOLON, SEMICOLON),
        MToken(MINUS, MINUS),
        MToken(BANG, BANG),
        MToken(SLASH, SLASH),
        MToken(ASTERISK, ASTERISK),
        MToken(LESSER, LESSER),
        MToken(GREATER, GREATER),
    ]

    run_lexer(input, tokens)


def test_composed_token():
    input = "0 == 0; 0 != 1;"
    tokens = [
        MToken(NUMBER, "0"),
        MToken(EQUAL, "=="),
        MToken(NUMBER, "0"),
        MToken(SEMICOLON, SEMICOLON),
        MToken(NUMBER, "0"),
        MToken(NOTEQUAL, "!="),
        MToken(NUMBER, "1"),
        MToken(SEMICOLON, SEMICOLON),
    ]

    run_lexer(input, tokens)


def test_string():
    inp = '"foobar"; "foo bar"'
    tokens = [
        MToken(STRING, "foobar"),
        MToken(SEMICOLON, SEMICOLON),
        MToken(STRING, "foo bar"),
    ]

    run_lexer(inp, tokens)


def test_array():
    inp = '[1, "a", true];'
    tokens = [
        MToken(LBRACKET, LBRACKET),
        MToken(NUMBER, "1"),
        MToken(COMMA, COMMA),
        MToken(STRING, "a"),
        MToken(COMMA, COMMA),
        MToken(KEYWORD, TRUE),
        MToken(RBRACKET, RBRACKET),
        MToken(SEMICOLON, SEMICOLON),
    ]

    run_lexer(inp, tokens)


def run_lexer(input, tokens):
    lexer = MLexer(input)

    for lex_token, token in zip(lexer, tokens):
        print(f"{lex_token=} {token=}")
        assert lex_token == token
