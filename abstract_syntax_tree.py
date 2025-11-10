from tokens import Token

class Statement:
	pass

class Expression:
	pass

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

class Identifier(Expression):
	def __init__(self, token: Token, name: str):
		self.token = token
		self.name = name
	def __str__(self) -> str:
		return self.name

class VarStatement(Statement):
	def __init__(self, token: Token, ident: Identifier, expression: Expression):
		self.token = token
		self.ident = ident
		self.expression = expression

	def __str__(self) -> str:
		return f"{self.token.literal} {self.ident.name} = {self.expression}"

class ExpressionStatement(Statement):
	def __init__(self, token: Token, expression: Expression):
		self.token = token
		self.expression = expression

	def __str__(self) -> str:
		return self.expression.__str__()
