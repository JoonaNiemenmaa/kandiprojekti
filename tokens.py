from enum import Enum


class TokenType(Enum):
	VAR = "VAR"
	SPRITE = "SPRITE"
	DRAW = "DRAW"
	DRAW_NUM = "DRAW_NUM"
	DRAW_CHAR = "DRAW_CHAR"
	PRESSED = "PRESSED"
	NOT_PRESSED = "NOT_PRESSED"
	UNTIL_PRESSED = "UNTIL_PRESSED"
	CLEAR = "CLEAR"
	IF = "IF"
	ELSE = "ELSE"
	WHILE = "WHILE"
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
	"draw_num": TokenType.DRAW_NUM,
	"draw_char": TokenType.DRAW_CHAR,
	"clear": TokenType.CLEAR,

	"if": TokenType.IF,
	"else": TokenType.ELSE,
	"while": TokenType.WHILE,

	"pressed": TokenType.PRESSED,
	"not_pressed": TokenType.NOT_PRESSED,
	"until_pressed": TokenType.UNTIL_PRESSED,
}


def identify_keyword(word):
	if word in keywords.keys():
		return keywords[word]
	else:
		return TokenType.IDENT
