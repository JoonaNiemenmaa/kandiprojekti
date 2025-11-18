from string import whitespace
from tokens import Token, TokenType, identify_keyword

class LexerException(Exception):
	pass

class Lexer:
	def read_char(self):
		if self.read_position >= len(self.code):
			self.ch = ""
		else:
			self.position = self.read_position
			self.ch = self.code[self.read_position]
			self.read_position += 1
			if self.ch == "\n":
				self.line += 1
				self.column = 1
			else:
				self.column += 1

	def __init__(self, code):
		self.code = code

		self.line = 1
		self.column = 1
		self.position = 0
		self.read_position = 0
		self.ch = ""
		self.read_char()

	def read_word(self):
		word = ""
		while self.ch.isalpha():
			word += self.ch
			self.read_char()
		return word

	def read_binary(self):
		number = "0b"
		self.read_char()
		while self.ch in ("1", "0"):
			number += self.ch
			self.read_char()
		if number == "0b":
			raise LexerException(f"Invalid binary literal '{number}' at {self.line}:{self.column}")
		return number
			

	def read_decimal(self):
		number = "0"
		while self.ch.isnumeric():
			number += self.ch
			self.read_char()
		return number

	def read_number(self):
		number = None
		if self.ch == "0":
			self.read_char()
			if self.ch == "b":
				number = self.read_binary()
			else:
				number = self.read_decimal()
		else:
			number = self.read_decimal()
		return number


	def eat_whitespace(self):
		while self.ch in whitespace and self.ch != "":
			self.read_char()

	def next_token(self):
		token = None
		self.eat_whitespace()
		match self.ch:
			case "=":
				token = Token(TokenType.ASSIGN, self.ch, self.line, self.column)
			case "+":
				token = Token(TokenType.PLUS, self.ch, self.line, self.column)
			case "-":
				token = Token(TokenType.MINUS, self.ch, self.line, self.column)
			case "*":
				token = Token(TokenType.ASTERISK, self.ch, self.line, self.column)
			case "/":
				token = Token(TokenType.SLASH, self.ch, self.line, self.column)
			case "(":
				token = Token(TokenType.LPAREN, self.ch, self.line, self.column)
			case ")":
				token = Token(TokenType.RPAREN, self.ch, self.line, self.column)
			case "{":
				token = Token(TokenType.LBRACE, self.ch, self.line, self.column)
			case "}":
				token = Token(TokenType.RBRACE, self.ch, self.line, self.column)
			case "[":
				token = Token(TokenType.LBRACKET, self.ch, self.line, self.column)
			case "]":
				token = Token(TokenType.RBRACKET, self.ch, self.line, self.column)
			case ";":
				token = Token(TokenType.SEMICOLON, self.ch, self.line, self.column)
			case ",":
				token = Token(TokenType.COMMA, self.ch, self.line, self.column)
			case "":
				token = Token(TokenType.EOF, self.ch, self.line, self.column)
			case _:
				if self.ch.isalpha():
					word = self.read_word()
					type = identify_keyword(word)
					token = Token(type, word, self.line, self.column)
					return token
				elif self.ch.isnumeric():
					number = self.read_number()
					token = Token(TokenType.INT, number, self.line, self.column)
					return token
				else:
					token = Token(TokenType.ILLEGAL, self.ch, self.line, self.column)
		self.read_char()
		return token

def main():
	code = "var nimi = 0 + 0b101 + 0b;"
	lexer = Lexer(code)
	token = lexer.next_token()
	print(token)
	while token.type != TokenType.EOF:
		token = lexer.next_token()
		print(token)

if __name__ == "__main__":
	main()
