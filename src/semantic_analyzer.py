from .tokens import Token

INT_MIN = 0
INT_MAX = 255

class SemanticsException(Exception):
	pass

class SemanticAnalyzer:
	def __init__(self):
		self.symbols = []

	def add_symbol(self, token: Token):
		if token.literal not in self.symbols:
			self.symbols.append(token.literal)

	def check_symbol(self, token: Token):
		literal = token.literal
		if literal not in self.symbols:
			raise SemanticsException(f"Identifier '{literal}' has not been declared at {token.line}:{token.column}!")

	def check_integer(self, token: Token):
		value = int(token.literal)
		if not (value <= INT_MAX and value >= INT_MIN):
			raise SemanticsException(f"Value '{value}' out of bounds {INT_MIN} <= value <= {INT_MAX} at {token.line}:{token.column}")
