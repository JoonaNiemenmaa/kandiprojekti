from tokens import Token

class Statement:
	def __init__(self, token: Token):
		self.token = token

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

class ExpressionStatement(Statement):
	def __init__(self, token: Token, expression: Expression):
		super().__init__(token)
		self.expression = expression

	def __str__(self) -> str:
		return f"{self.expression.__str__()};"

class DrawStatement(Statement):
	def __init__(self, token: Token, ident: Identifier, x: Expression, y: Expression):
		super().__init__(token)
		self.ident = ident
		self.x = x
		self.y = y

	def __str__(self) -> str:
		return f"draw({self.ident}, {self.x}, {self.y});"

class Declaration(Statement):
	pass

class SpriteDeclaration(Declaration):
	def __init__(self, token: Token, ident: Identifier, rows: list[Integer]):
		super().__init__(token)
		self.ident = ident
		self.rows = rows

	def __str__(self) -> str:
		rows = "{ "
		for row in self.rows:
			rows += f"{row.__str__()}, "
		rows = f"{rows[:-2]} }}"
		return f"{self.token.literal} {self.ident.name} = {rows};"

class IntegerDeclaration(Declaration):
	def __init__(self, token: Token, ident: Identifier, expression: Expression):
		super().__init__(token)
		self.ident = ident
		self.expression = expression

	def __str__(self) -> str:
		return f"{self.token.literal} {self.ident.name} = {self.expression};"

class Block:
	def __init__(self, statements: list[Statement]):
		self.statements = statements

	def __str__(self) -> str:
		block_string = ""
		for statement in self.statements:
			block_string += f"\t{statement.__str__()}\n"
		return block_string

class MainDeclaration(Declaration):
	def __init__(self, token: Token, block: Block):
		super().__init__(token)
		self.block = block

	def __str__(self):
		return f"main {{\n{self.block}}}"
