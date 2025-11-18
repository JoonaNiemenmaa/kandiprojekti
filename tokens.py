from enum import Enum

class TokenType(Enum):
	VAR = "VAR"
	SPRITE = "SPRITE"
	DRAW = "DRAW"
	CLEAR = "CLEAR"
	IF = "IF"
	#MAIN = "MAIN"

	INT = "INT"
	IDENT = "IDENT"

	EOF = "EOF"
	ILLEGAL = "ILLEGAL"

	SEMICOLON = ";"
	COMMA = ","

	LBRACE = "{"
	RBRACE = "}"
	LBRACKET = "["
	RBRACKET = "]"

	ASSIGN = "="
	PLUS = "+"
	MINUS = "-"
	ASTERISK = "*"
	SLASH = "/"
	LPAREN = "("
	RPAREN = ")"

	NOT = "!"
	EQUALS = "=="
	NOT_EQUALS = "!="


class Token:
	def __init__(self, type: TokenType, literal: str, line: int, column: int):
		self.type = type
		self.literal = literal

		self.line = line
		self.column = column
	def __str__(self):
		return f"{self.type} with literal '{self.literal}' at {self.line}:{self.column}"

keywords = {
	"var": TokenType.VAR,
	"sprite": TokenType.SPRITE,
	"draw": TokenType.DRAW,
	"clear": TokenType.CLEAR,
	"if": TokenType.IF,
	#"main": TokenType.MAIN,
}

def identify_keyword(word):
	if word in keywords.keys():
		return keywords[word]
	else:
		return TokenType.IDENT
