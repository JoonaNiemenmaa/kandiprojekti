from enum import Enum

class TokenType(Enum):
	LET = "LET"
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
	SHIFTLEFT = "<<"
	SHIFTRIGHT = ">>"
	LPAREN = "("
	RPAREN = ")"

	LESSER = "<"
	GREATER = ">"
	EQUALS = "=="
	NOT_EQUALS = "!="

class Token:
	def __init__(self, type: TokenType, literal: str):
		self.type = type
		self.literal = literal
	def __str__(self):
		return f"{self.type}"

keywords = {
	"let": TokenType.LET
}

def identify_keyword(word):
	if word in keywords.keys():
		return keywords[word]
	else:
		return TokenType.IDENT
