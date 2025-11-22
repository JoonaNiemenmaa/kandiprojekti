from tokens import Token

class Statement:
	def __init__(self, token: Token):
		self.token = token

class Block(Statement):
	def __init__(self, token: Token, statements: list[Statement]):
		super().__init__(token)
		self.statements: list[Statement] = statements

	def __str__(self) -> str:
		block_string = "{\n"
		for statement in self.statements:
			block_string += f"\t{statement.__str__()}\n"
		block_string += "}"
		return block_string

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

class Draw(Expression):
	def __init__(self, token: Token, ident: Identifier, x: Expression, y: Expression):
		self.token = token
		self.ident = ident
		self.x = x
		self.y = y

	def __str__(self) -> str:
		return f"draw({self.ident}, {self.x}, {self.y})"

class DrawNum(Expression):
	def __init__(self, token: Token, number: Expression, x: Expression, y: Expression):
		self.token = token
		self.number = number
		self.x = x
		self.y = y
		
	def __str__(self) -> str:
		return f"draw_num({self.number}, {self.x}, {self.y})"

class DrawChar(Expression):
	def __init__(self, token: Token, char: Expression, x: Expression, y: Expression):
		self.token = token
		self.char = char
		self.x = x
		self.y = y
		
	def __str__(self) -> str:
		return f"draw_char({self.char}, {self.x}, {self.y})"

class If(Statement):
	def __init__(self, token: Token, condition: Expression, consequence: Block, alternative: Block | None = None):
		self.token = token
		self.condition = condition
		self.consequence = consequence
		self.alternative = alternative
	def __str__(self) -> str:
		return f"if ({self.condition}) {self.consequence}{" else " + self.alternative.__str__() if self.alternative else ""}"

class While(Statement):
	def __init__(self, token: Token, condition: Expression, block: Block):
		self.token = token
		self.condition = condition
		self.block = block
	def __str__(self) -> str:
		return f"while ({self.condition}) {self.block}"

class ExpressionStatement(Statement):
	def __init__(self, token: Token, expression: Expression):
		super().__init__(token)
		self.expression = expression

	def __str__(self) -> str:
		return f"{self.expression.__str__()};"


class Clear(Statement):
	def __init__(self, token: Token):
		super().__init__(token)

	def __str__(self) -> str:
		return "clear;"

class SpriteDeclaration(Statement):
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

class IntegerDeclaration(Statement):
	def __init__(self, token: Token, ident: Identifier, expression: Expression):
		super().__init__(token)
		self.ident = ident
		self.expression = expression

	def __str__(self) -> str:
		return f"{self.token.literal} {self.ident.name} = {self.expression};"
