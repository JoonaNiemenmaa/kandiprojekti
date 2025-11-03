from tokens import Token

class Statement:
	pass

class Expression:
	pass

class Program:
	statements = []

class Identifier(Expression):
	pass

class Integer(Expression):
	pass

class LetStatement(Statement):
	def __init__(self):
		self.identifier: Identifier
		self.expression: Integer
