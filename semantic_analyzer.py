from tokens import Token

INT_MIN = 0
INT_MAX = 255

SPRITE_MAX_SIZE = 15

class Type:
	def __init__(self, location: int, size: int):
		self.location = location
		self.size = size

class Integer(Type):
	def __init__(self, location: int):
		super().__init__(location, size=1)

class Sprite(Type):
	def __init__(self, location: int, size: int):
		if size > SPRITE_MAX_SIZE:
			raise SemanticsException(f"Sprites may not be larger than {SPRITE_MAX_SIZE}!")
		super().__init__(location, size)

class SemanticsException(Exception):
	pass

class SemanticAnalyzer:
	def __init__(self):
		self.stack_pointer = 0
		self.symbols: dict[str, Type] = {}

	def add_integer_symbol(self, name: str):
		if name in self.symbols.keys():
			raise SemanticsException(f"{name} already exists!")
		type = Integer(self.stack_pointer)
		self.symbols[name] = type
		self.stack_pointer += type.size

	def add_sprite_symbol(self, name: str, size: int):
		if name in self.symbols.keys():
			raise SemanticsException(f"{name} already exists!")
		type = Sprite(self.stack_pointer, size)
		self.symbols[name] = type
		self.stack_pointer += type.size

	def get_symbol_location(self, symbol: str):
		return self.symbols[symbol].location

	def get_symbol_size(self, symbol: str):
		return self.symbols[symbol].size

	def check_symbol(self, token: Token):
		literal = token.literal
		if literal not in self.symbols:
			raise SemanticsException(f"Identifier '{literal}' has not been declared at {token.line}:{token.column}!")

	def check_integer_value(self, token: Token):
		literal = token.literal
		value = 0
		if literal.startswith("0b"):
			value = int(token.literal, 2)
		else:
			value = int(token.literal)
		if not (value <= INT_MAX and value >= INT_MIN):
			raise SemanticsException(f"Value '{value}' out of bounds {INT_MIN} <= value <= {INT_MAX} at {token.line}:{token.column}")
