from lexer import Lexer
from tokens import TokenType

def test_expression_lexing():

	test_cases = [
		("var result = number - (5 + 505) * 4 / 8;",
			[
				TokenType.VAR,
				TokenType.IDENT,
				TokenType.ASSIGN,
				TokenType.IDENT,
				TokenType.MINUS,
				TokenType.LPAREN,
			 	TokenType.INT,
				TokenType.PLUS,
				TokenType.INT,
				TokenType.RPAREN,
				TokenType.ASTERISK,
				TokenType.INT,
				TokenType.SLASH,
				TokenType.INT,
				TokenType.SEMICOLON,
				TokenType.EOF,
			]
		), (
			"\t\tjoona        0891, 	\n\n	 5+5",
			[
				TokenType.IDENT,
				TokenType.INT,
				TokenType.ILLEGAL,
				TokenType.INT,
				TokenType.PLUS,
				TokenType.INT,
				TokenType.EOF,
			]
		)
	]

	for case, expected in test_cases:
		lexer = Lexer(case)
		for expected_type in expected:
			token = lexer.next_token()
			assert token.type is expected_type
