from abstract_syntax_tree import *
from semantic_analyzer import SemanticAnalyzer
from tokens import TokenType

class CodeGeneratorException(Exception):
	pass

REGISTERS = 16
RAM = 4096
INSTRUCTION_LENGTH = 2
START = 0x200

V0 = 0x0
V1 = 0x1
V2 = 0x2
V3 = 0x3
V4 = 0x4
V5 = 0x5
V6 = 0x6
V7 = 0x7
V8 = 0x8
V9 = 0x9
VA = 0xA
VB = 0xB
VC = 0xC
VD = 0xD
VE = 0xE
VF = 0xF

class CodeGenerator:

	def __init__(self, filename, semantic: SemanticAnalyzer):
		self.registers = [True] * REGISTERS

		# Register V0 is used to load variables from memory and VF is used by certain instructions for various stuff
		# This is why they are set as reserved here
		self.registers[V0] = False
		self.registers[VF] = False

		self.output = open(filename, "wb")
		self.pc = START
		self.semantic = semantic

	def write_instruction(self, op: int, x = 0, y = 0, n = 0, kk: int | None = None, nnn: int | None = None):
		instruction = op<<4
		if nnn:
			instruction = instruction<<8 | nnn
		else:
			if kk:
				instruction = (instruction | x)<<4
				instruction = instruction<<4 | kk
			else:
				instruction = (instruction | x)<<4
				instruction = (instruction | y)<<4
				instruction = (instruction | n)
		self.output.write(instruction.to_bytes(length=INSTRUCTION_LENGTH))
		self.pc += 2

	def close(self):
		self.output.close()

	def allocate_register(self) -> int:
		for i in range(REGISTERS):
			if self.registers[i]:
				self.registers[i] = False
				return i
		raise CodeGeneratorException("No available registers")

	def free_register(self, register: int):
		self.registers[register] = True

	def get_mem_location(self, identifier: str):
		return RAM - self.semantic.get_symbol_location(identifier) - 1

	def generate_var_statement(self, statement: VarStatement):
		register_value = self.generate_expression(statement.expression)
		mem_location = self.get_mem_location(statement.ident.name)
		self.write_instruction(op=0xA, nnn=mem_location)
		if register_value != 0:
			self.write_instruction(op=0x8, x=0, y=register_value, n=0)
		self.write_instruction(op=0xF, x=0, kk=55)
		self.free_register(register_value)

	def generate_integer(self, integer: Integer) -> int:
		register = self.allocate_register()
		self.write_instruction(op=0x6, x=register, kk=integer.value)
		return register

	def generate_identifier(self, identifier: Identifier) -> int:
		register = self.allocate_register()
		mem_location = self.get_mem_location(identifier.name)
		self.write_instruction(op=0xA, nnn=mem_location);
		self.write_instruction(op=0xF, x=0, kk=65)
		self.write_instruction(op=0x8, x=register, y=0, n=0)
		return register

	def generate_infix(self, infix: Infix) -> int:

		left_register = self.generate_expression(infix.left)
		right_register = self.generate_expression(infix.right)

		match infix.operator.type:
			case TokenType.PLUS:
				self.write_instruction(op=0x8, x=left_register, y=right_register, n=4)
			case TokenType.MINUS:
				self.write_instruction(op=0x8, x=left_register, y=right_register, n=5)
			case TokenType.ASTERISK:
				index_register = self.allocate_register()
				result_register = self.allocate_register()

				self.write_instruction(op=0x6, x=index_register, kk=0)
				self.write_instruction(op=0x6, x=result_register, kk=0)

				loop_start = self.pc

				self.write_instruction(op=0x9, x=left_register, y=index_register, n=0)
				self.write_instruction(op=0x1, nnn=loop_start + INSTRUCTION_LENGTH * 5)
				self.write_instruction(op=0x8, x=result_register, y=right_register, n=4)
				self.write_instruction(op=0x7, x=index_register, kk=1)
				self.write_instruction(op=0x1, nnn=loop_start)

				self.free_register(index_register)
				self.free_register(left_register)
				left_register = result_register
			case _:
				raise CodeGeneratorException("Invalid operand!")

		self.free_register(right_register)

		return left_register

	def generate_expression(self, expression: Expression) -> int:
		match expression:
			case Integer():
				register = self.generate_integer(expression)
			case Identifier():
				register = self.generate_identifier(expression)
			case Infix():
				register = self.generate_infix(expression)
			case _:
				raise CodeGeneratorException("Invalid expression type")
		return register

	def generate_statement(self, statement: Statement):
		match statement:
			case ExpressionStatement():
				print(statement)
				register = self.generate_expression(statement.expression)
				self.free_register(register)
			case VarStatement():
				self.generate_var_statement(statement)
