from .semantic_analyzer import SemanticAnalyzer
from .lexer import Lexer
from .tokens import TokenType
from .abstract_syntax_tree import *

class ParserException(Exception):
	pass

class TokenException(ParserException):
	def __init__(self, expected_type: TokenType, found_token: Token):
		self.expected_type = expected_type
		self.found_token = found_token
		self.message = f"Found token {found_token} when expected token {expected_type} at {found_token.line}:{found_token.column}"
		super().__init__(self.message)

class Parser:

	LOWEST = 1
	SUM = 2
	PRODUCT = 3

	def __init__(self, code: str):
		self.lexer = Lexer(code)
		self.semantic = SemanticAnalyzer()
		self.current_token = self.lexer.next_token()
		self.peek_token = self.lexer.next_token()

	def next_token(self):
		self.current_token = self.peek_token
		self.peek_token = self.lexer.next_token()

	def check_peek_token(self, expected: TokenType):
		if self.peek_token.type is not expected:
			raise TokenException(expected, self.peek_token)
		self.next_token()

	def parse_int(self):
		value = int(self.current_token.literal)
		self.semantic.check_integer(self.current_token)
		return Integer(self.current_token, value)

	def parse_ident(self):
		name = self.current_token.literal
		self.semantic.check_symbol(self.current_token)
		return Identifier(self.current_token, name)

	def parse_grouped_expression(self):
		self.next_token()
		expression = self.parse_expression(self.LOWEST)
		self.check_peek_token(TokenType.RPAREN)
		return expression

	def parse_infix(self, left_expression):
		self.next_token()
		operator = self.current_token
		self.next_token()
		right_expression = self.parse_expression(self.get_precedence(operator.type))
		return Infix(operator, left_expression, right_expression)

	prefix_functions = {
		TokenType.INT: parse_int,
		TokenType.IDENT: parse_ident,
		TokenType.LPAREN: parse_grouped_expression,
	}

	precedences = {
		TokenType.PLUS: SUM,
		TokenType.MINUS: SUM,
		TokenType.ASTERISK: PRODUCT,
		TokenType.SLASH: PRODUCT,
	}

	def get_precedence(self, type: TokenType):
		return self.precedences.get(type, self.LOWEST)

	infix_functions = {
		TokenType.PLUS: parse_infix,
		TokenType.MINUS: parse_infix,
		TokenType.ASTERISK: parse_infix,
		TokenType.SLASH: parse_infix,
	}

	# tokens allowed after a prefix
	after_prefix_tokens = (
		TokenType.PLUS,
		TokenType.MINUS,
		TokenType.ASTERISK,
		TokenType.SLASH,
		TokenType.SEMICOLON,
		TokenType.RPAREN,
	)

	def parse_expression(self, precedence):
		prefix = self.prefix_functions.get(self.current_token.type)
		if not prefix:
			raise ParserException(f"No prefix parsing function for {self.current_token} {self.current_token.line}:{self.current_token.column}")

		left_expression = prefix(self)

		infix_expression = left_expression

		if self.peek_token.type not in self.after_prefix_tokens:
			raise ParserException(f"No infix parsing function for {self.peek_token} {self.peek_token.line}:{self.peek_token.column}")

		while self.peek_token.type is not TokenType.SEMICOLON and precedence < self.get_precedence(self.peek_token.type):
			infix = self.infix_functions.get(self.peek_token.type)
			if not infix:
				raise ParserException(f"No infix parsing function for {self.peek_token}")
			infix_expression = infix(self, infix_expression)

		return infix_expression

	def parse_expression_statement(self):
		token = self.current_token
		expression = self.parse_expression(self.LOWEST)
		if not expression:
			raise ParserException
		statement = ExpressionStatement(token, expression)
		return statement

	def parse_let_statement(self):
		token = self.current_token
		self.check_peek_token(TokenType.IDENT)
		ident = self.current_token
		self.check_peek_token(TokenType.ASSIGN)
		self.next_token()
		expression = self.parse_expression(self.LOWEST)
		self.semantic.add_symbol(ident)
		return LetStatement(token, ident, expression)

	def parse_program(self):
		program = []
		while self.current_token.type != TokenType.EOF:
			match self.current_token.type:
				case TokenType.VAR:
					statement = self.parse_let_statement()
				case _:
					statement = self.parse_expression_statement()
			self.check_peek_token(TokenType.SEMICOLON)
			if statement:
				program.append(statement)
			self.next_token()
		return program

def main():
	code = "var ankka = 255;\nvar joona = (55+10)*ankka;"
	parser = Parser(code)
	program = parser.parse_program()
	for statement in program:
		print(statement)

if __name__ == "__main__":
	main()
