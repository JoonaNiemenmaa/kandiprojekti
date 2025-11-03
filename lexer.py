from string import whitespace
from tokens import Token, TokenType, identify_keyword

class Lexer:
	def read_char(self):
		if self.read_position >= len(self.code):
			self.ch = ""
		else:
			self.position = self.read_position
			self.ch = self.code[self.read_position]
			self.read_position += 1

	def __init__(self, code):
		self.code = code

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

	def read_number(self):
		number = ""
		while self.ch.isnumeric():
			number += self.ch
			self.read_char()
		return number

	def eat_whitespace(self):
		while self.ch in whitespace:
			self.read_char()


	def next_token(self):
		token = None
		self.eat_whitespace()
		match self.ch:
			case "=":
				token = Token(TokenType.ASSIGN, self.ch)
			case ";":
				token = Token(TokenType.SEMICOLON, self.ch)
			case "":
				token = Token(TokenType.EOF, self.ch)
			case _:
				if self.ch.isalpha():
					word = self.read_word()
					type = identify_keyword(word)
					token = Token(type, word)
					return token
				elif self.ch.isnumeric():
					number = self.read_number()
					token = Token(TokenType.INT, number)
					return token
				else:
					token = Token(TokenType.ILLEGAL, self.ch)
		self.read_char()
		return token

def main():
	code = open("variables.c8c", "r").read()
	lexer = Lexer(code)
	token = lexer.next_token()
	print(token)
	while token.type != TokenType.EOF:
		token = lexer.next_token()
		print(token)

if __name__ == "__main__":
	main()
