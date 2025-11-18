import pytest
from lexer import Lexer, LexerException
from tokens import TokenType

def test_lexing():

	test_cases = (
		("var result = !number - (5 + 505) * 4 / 8;",
			(
				(TokenType.VAR, "var"),
				(TokenType.IDENT, "result"),
				(TokenType.ASSIGN, "="),
				(TokenType.NOT, "!"),
				(TokenType.IDENT, "number"),
				(TokenType.MINUS, "-"),
				(TokenType.LPAREN, "("),
			 	(TokenType.INT, "5"),
				(TokenType.PLUS, "+"),
				(TokenType.INT, "505"),
				(TokenType.RPAREN, ")"),
				(TokenType.ASTERISK, "*"),
				(TokenType.INT, "4"),
				(TokenType.SLASH, "/"),
				(TokenType.INT, "8"),
				(TokenType.SEMICOLON, ";"),
				(TokenType.EOF, ""),
			)
		),
		("\t\tjoona        0891, 	\n\n	 5+5",
			(
				(TokenType.IDENT, "joona"),
				(TokenType.INT, "0891"),
				(TokenType.COMMA, ","),
				(TokenType.INT, "5"),
				(TokenType.PLUS, "+"),
				(TokenType.INT, "5"),
				(TokenType.EOF, ""),
			)
		),
		("6 == 5 != 0b101",
			(
				(TokenType.INT, "6"),
				(TokenType.EQUALS, "=="),
				(TokenType.INT, "5"),
				(TokenType.NOT_EQUALS, "!="),
				(TokenType.INT, "0b101"),
				(TokenType.EOF, ""),
			)
		),
		("sprite hilavitkutin = { 0b11, 0b11 };",
			(
				(TokenType.SPRITE, "sprite"),
				(TokenType.IDENT, "hilavitkutin"),
				(TokenType.ASSIGN, "="),
				(TokenType.LBRACE, "{"),
				(TokenType.INT, "0b11"),
				(TokenType.COMMA, ","),
				(TokenType.INT, "0b11"),
				(TokenType.RBRACE, "}"),
				(TokenType.SEMICOLON, ";"),
				(TokenType.EOF, ""),
			)
		),
		("clear;",
			(
				(TokenType.CLEAR, "clear"),
				(TokenType.SEMICOLON, ";"),
				(TokenType.EOF, ""),
			)
		)
	)

	for case, expected in test_cases:
		lexer = Lexer(case)
		for expected_type, expected_literal in expected:
			token = lexer.next_token()
			assert token.type is expected_type
			assert token.literal == expected_literal

def test_binary_lexing():
	test_cases = (
		"0b00011",
		"0b101",
		"0b1",
		"0b1010101",
		"0b0"
	)

	for case in test_cases:
		lexer = Lexer(case)
		token = lexer.next_token()
		assert token.type is TokenType.INT
		assert token.literal == case

def test_invalid_binary():
	code = "0b"
	lexer = Lexer(code)
	with pytest.raises(LexerException):
		lexer.next_token()
