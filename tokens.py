from enum import Enum

class TokenType(Enum):
	VAR = "VAR"
	INT = "INT"
	IDENT = "IDENT"
	SEMICOLON = ";"
	EOF = "EOF"
	ILLEGAL = "ILLEGAL"

	ASSIGN = "="
	PLUS = "+"
	MINUS = "-"
	ASTERISK = "*"
	SLASH = "/"
	LPAREN = "("
	RPAREN = ")"

	LESSER = "<"
	GREATER = ">"
	EQUALS = "=="
	NOT_EQUALS = "!="

class Token:
	def __init__(self, type: TokenType, literal: str, line: int, column: int):
		self.type = type
		self.literal = literal

		self.line = line
		self.column = column
	def __str__(self):
		return f"{self.type}"

keywords = {
	"var": TokenType.VAR
}

def identify_keyword(word):
	if word in keywords.keys():
		return keywords[word]
	else:
		return TokenType.IDENT
