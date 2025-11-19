from code_generator import CodeGenerator
from semantic_analyzer import SemanticAnalyzer
from lexer import Lexer
from tokens import TokenType, Token
from abstract_syntax_tree import Integer, Identifier, Infix, Expression, If, While, Clear, DrawCall, ExpressionStatement, IntegerDeclaration, SpriteDeclaration, Block

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
	EQUALS = 2
	SUM = 3
	PRODUCT = 4
	CALL = 5

	def __init__(self, code: str):
		self.lexer = Lexer(code)
		self.semantic = SemanticAnalyzer()
		self.generator = CodeGenerator(self.semantic)
		self.current_token = self.lexer.next_token()
		self.peek_token = self.lexer.next_token()

	def next_token(self):
		self.current_token = self.peek_token
		self.peek_token = self.lexer.next_token()

	def check_peek_token(self, expected: TokenType):
		if self.peek_token.type is not expected:
			raise TokenException(expected, self.peek_token)
		self.next_token()

	def check_current_token(self, expected: TokenType):
		if self.current_token.type is not expected:
			raise TokenException(expected, self.current_token)
		self.next_token()

	def parse_int(self) -> Integer:
		literal = self.current_token.literal
		if literal.startswith("0b"):
			value = int(literal, 2)
		else:
			value = int(self.current_token.literal)
		self.semantic.check_integer_value(self.current_token)
		return Integer(self.current_token, value)

	def parse_ident(self, declaration = False) -> Identifier:
		name = self.current_token.literal
		if not declaration:
			self.semantic.check_symbol(self.current_token)
		return Identifier(self.current_token, name)

	def parse_grouped_expression(self) -> Expression:
		self.next_token()
		expression = self.parse_expression(self.LOWEST)
		self.check_peek_token(TokenType.RPAREN)
		return expression

	def parse_draw_call(self) -> DrawCall:
		token = self.current_token
		self.check_peek_token(TokenType.LPAREN)

		self.check_peek_token(TokenType.IDENT)
		ident = self.parse_ident()

		self.check_peek_token(TokenType.COMMA)
		self.next_token()

		x = self.parse_expression(self.LOWEST)

		self.check_peek_token(TokenType.COMMA)
		self.next_token()

		y = self.parse_expression(self.LOWEST)

		self.check_peek_token(TokenType.RPAREN)

		return DrawCall(token, ident, x, y)

	def parse_infix(self, left_expression) -> Infix:
		self.next_token()
		operator = self.current_token
		self.next_token()
		right_expression = self.parse_expression(self.get_precedence(operator.type))
		return Infix(operator, left_expression, right_expression)

	prefix_functions = {
		TokenType.INT: parse_int,
		TokenType.IDENT: parse_ident,
		TokenType.LPAREN: parse_grouped_expression,
		TokenType.DRAW: parse_draw_call,
	}

	precedences = {
		TokenType.EQUALS: EQUALS,
		TokenType.NOT_EQUALS: EQUALS,
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
		TokenType.EQUALS: parse_infix,
		TokenType.NOT_EQUALS: parse_infix,
	}

	# tokens allowed after a prefix
	# this allows for better error reporting
	after_prefix_tokens = (
		TokenType.EQUALS,
		TokenType.NOT_EQUALS,
		TokenType.PLUS,
		TokenType.MINUS,
		TokenType.ASTERISK,
		TokenType.SLASH,
		TokenType.SEMICOLON,
		TokenType.RPAREN,
		TokenType.COMMA,
	)

	def parse_expression(self, precedence):
		prefix = self.prefix_functions.get(self.current_token.type)
		if not prefix:
			raise ParserException(f"No prefix parsing function for {self.current_token} at {self.current_token.line}:{self.current_token.column}")

		left_expression = prefix(self)

		infix_expression = left_expression

		#if self.peek_token.type not in self.after_prefix_tokens:
			#raise ParserException(f"No infix parsing function for {self.peek_token} at {self.peek_token.line}:{self.peek_token.column}")

		while self.peek_token.type is not TokenType.SEMICOLON and precedence < self.get_precedence(self.peek_token.type):
			infix = self.infix_functions.get(self.peek_token.type)
			if not infix:
				raise ParserException(f"No infix parsing function for {self.peek_token} at {self.peek_token.line}:{self.peek_token.column}")
			infix_expression = infix(self, infix_expression)

		return infix_expression

	def parse_expression_statement(self):
		token = self.current_token
		expression = self.parse_expression(self.LOWEST)
		if not expression:
			raise ParserException
		statement = ExpressionStatement(token, expression)
		return statement

	# def parse_draw_statement(self):
	# 	token = self.current_token
	# 	self.check_peek_token(TokenType.LPAREN)
	# 	self.check_peek_token(TokenType.IDENT)
	# 	ident = self.parse_ident()
	# 	self.check_peek_token(TokenType.COMMA)
	# 	self.next_token()
	# 	x = self.parse_expression(self.LOWEST)
	# 	self.check_peek_token(TokenType.COMMA)
	# 	self.next_token()
	# 	y = self.parse_expression(self.LOWEST)
	# 	self.check_peek_token(TokenType.RPAREN)
	# 	return Draw(token, ident, x, y)

	def parse_clear_statement(self):
		token = self.current_token
		return Clear(token)

	def parse_block(self):
		token = self.current_token
		statements = []
		self.next_token()
		while self.current_token.type is not TokenType.RBRACE:
			statement = self.parse_statement()
			statements.append(statement)
		return Block(token, statements)

	def parse_if_statement(self) -> If:
		token = self.current_token
		self.check_peek_token(TokenType.LPAREN)
		self.next_token()
		condition = self.parse_expression(self.LOWEST)
		self.check_peek_token(TokenType.RPAREN)
		self.next_token()
		consequence = self.parse_block()
		if self.peek_token.type is TokenType.ELSE:
			self.next_token()
			self.next_token()
			alternative = self.parse_block()
			return If(token, condition, consequence, alternative)
		else:
			return If(token, condition, consequence)

	def parse_while_statement(self) -> While:
		token = self.current_token
		self.check_peek_token(TokenType.LPAREN)
		self.next_token()
		condition = self.parse_expression(self.LOWEST)
		self.check_peek_token(TokenType.RPAREN)
		self.next_token()
		block = self.parse_block()
		return While(token, condition, block)

	def parse_integer_declaration(self):
		token = self.current_token
		self.check_peek_token(TokenType.IDENT)
		ident = self.parse_ident(declaration=True)
		self.check_peek_token(TokenType.ASSIGN)
		self.next_token()
		expression = self.parse_expression(self.LOWEST)
		self.semantic.add_integer_symbol(ident.name)
		return IntegerDeclaration(token, ident, expression)

	def parse_sprite_declaration(self):
		token = self.current_token
		self.check_peek_token(TokenType.IDENT)
		ident = self.parse_ident(declaration=True)
		self.check_peek_token(TokenType.ASSIGN)
		self.check_peek_token(TokenType.LBRACE)
		self.check_peek_token(TokenType.INT)

		rows = []
		rows.append(self.parse_int())

		while self.peek_token.type is TokenType.COMMA:
			self.next_token()
			self.next_token()
			rows.append(self.parse_int())

		self.check_peek_token(TokenType.RBRACE)

		self.semantic.add_sprite_symbol(ident.name, len(rows))
		return SpriteDeclaration(token, ident, rows)

	def parse_statement(self):
		match self.current_token.type:
			case TokenType.VAR:
				statement = self.parse_integer_declaration()
				self.check_peek_token(TokenType.SEMICOLON)
			case TokenType.SPRITE:
				statement = self.parse_sprite_declaration()
				self.check_peek_token(TokenType.SEMICOLON)
			case TokenType.IF:
				statement = self.parse_if_statement()
			case TokenType.WHILE:
				statement = self.parse_while_statement()
			# case TokenType.DRAW:
			# 	statement = self.parse_draw_statement()
			# 	self.check_peek_token(TokenType.SEMICOLON)
			case TokenType.CLEAR:
				statement = self.parse_clear_statement()
				self.check_peek_token(TokenType.SEMICOLON)
			case _:
				statement = self.parse_expression_statement()
				self.check_peek_token(TokenType.SEMICOLON)
		self.next_token()
		return statement

	def parse_program(self):
		program = []
		while self.current_token.type != TokenType.EOF:
			statement = self.parse_statement()
			#self.generator.generate_statement(statement)
			program.append(statement)
		self.generator.write_file("output.ch8")
		return program

def main():
	code = ""
	with open("conditionals.c8c", "r") as file:
		code = file.read()
	parser = Parser(code)
	program = parser.parse_program()
	for statement in program:
		print(statement)

if __name__ == "__main__":
	main()
