from .tokens import Token

class Statement:
	pass

class Expression:
	pass

class LetStatement(Statement):
	def __init__(self, token: Token, ident: Token, expression: Expression):
		self.token = token
		self.ident = ident
		self.expression = expression

	def __str__(self) -> str:
		return f"{self.token.literal} {self.ident.literal} = {self.expression}"

class ExpressionStatement(Statement):
	def __init__(self, token: Token, expression: Expression):
		self.token = token
		self.expression = expression

	def __str__(self) -> str:
		return self.expression.__str__()

class Identifier(Expression):
	def __init__(self, token: Token, value: str):
		self.token = token
		self.name = value
	def __str__(self) -> str:
		return self.name

class Integer(Expression):
	def __init__(self, token: Token, value: int):
		self.token = token
		self.value = value
	def __str__(self) -> str:
		return str(self.value)

class Infix(Expression):
	def __init__(self, operator: Token, left: Expression, right: Expression):
		self.operator = operator
		self.left = left
		self.right = right
	def __str__(self) -> str:
		return f"({self.left} {self.operator.literal} {self.right})"
