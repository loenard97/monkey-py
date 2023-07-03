from pymonkey.lexer.mlexer import MLexer
from pymonkey.lexer.mtoken import MToken, MTokenType


def run_lexer(test_input: str, tokens: list[MToken]) -> None:
    lexer = MLexer(test_input, file_name="test")

    for lex_token, token in zip(lexer, tokens):
        print(f"{lex_token=} {token=}")
        assert lex_token.type == token.type and lex_token.literal == token.literal


def test_token() -> None:
    test_input = "=+(){},;-!/*<>"
    tokens = [
        MToken(MTokenType.Assign, "="),
        MToken(MTokenType.Plus, "+"),
        MToken(MTokenType.LParen, "("),
        MToken(MTokenType.RParen, ")"),
        MToken(MTokenType.LBrace, "{"),
        MToken(MTokenType.RBrace, "}"),
        MToken(MTokenType.Comma, ","),
        MToken(MTokenType.Semicolon, ";"),
        MToken(MTokenType.Minus, "-"),
        MToken(MTokenType.Bang, "!"),
        MToken(MTokenType.Slash, "/"),
        MToken(MTokenType.Asterisk, "*"),
        MToken(MTokenType.Lesser, "<"),
        MToken(MTokenType.Greater, ">"),
    ]

    run_lexer(test_input, tokens)


def test_composed_token() -> None:
    test_input = "0 == 0; 0 != 1;"
    tokens = [
        MToken(MTokenType.Number, "0"),
        MToken(MTokenType.Equal, "=="),
        MToken(MTokenType.Number, "0"),
        MToken(MTokenType.Semicolon, ";"),
        MToken(MTokenType.Number, "0"),
        MToken(MTokenType.NotEqual, "!="),
        MToken(MTokenType.Number, "1"),
        MToken(MTokenType.Semicolon, ";"),
    ]

    run_lexer(test_input, tokens)


def test_string() -> None:
    test_input = '"foobar"; "foo bar"'
    tokens = [
        MToken(MTokenType.String, "foobar"),
        MToken(MTokenType.Semicolon, ";"),
        MToken(MTokenType.String, "foo bar"),
    ]

    run_lexer(test_input, tokens)


def test_array() -> None:
    test_input = '[1, "a", true];'
    tokens = [
        MToken(MTokenType.LBracket, "["),
        MToken(MTokenType.Number, "1"),
        MToken(MTokenType.Comma, ","),
        MToken(MTokenType.String, "a"),
        MToken(MTokenType.Comma, ","),
        MToken(MTokenType.Keyword, "true"),
        MToken(MTokenType.RBracket, "]"),
        MToken(MTokenType.Semicolon, ";"),
    ]

    run_lexer(test_input, tokens)


def test_hashmap() -> None:
    test_input = '{"foo": "bar"};'
    tokens = [
        MToken(MTokenType.LBrace, "{"),
        MToken(MTokenType.String, "foo"),
        MToken(MTokenType.Colon, ":"),
        MToken(MTokenType.String, "bar"),
        MToken(MTokenType.RBrace, "}"),
        MToken(MTokenType.Semicolon, ";"),
    ]

    run_lexer(test_input, tokens)
