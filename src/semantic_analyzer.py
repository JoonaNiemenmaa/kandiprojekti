from .tokens import Token

class SemanticsException(Exception):
	pass

class SemanticAnalyzer:
	def __init__(self):
		self.symbols = []

	def add_symbol(self, token: Token):
		if not self.check_symbol(token):
			self.symbols.append(token.literal)

	def check_symbol(self, token: Token):
		literal = token.literal
		if literal not in self.symbols:
			raise SemanticsException(f"Identifier {literal} has not been declared!")
