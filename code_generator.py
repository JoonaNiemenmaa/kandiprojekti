from abstract_syntax_tree import *
from semantic_analyzer import SemanticAnalyzer
from tokens import TokenType

class CodeGeneratorException(Exception):
	pass

REGISTERS = 16
RAM = 4096
INSTRUCTION_LENGTH = 2
WORD_SIZE = 1
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

class Instruction:
	def __init__(self, op: int, x = 0, y = 0, n = 0, kk: int | None = None, nnn: int | None = None):
		self.op = op
		self.x = x
		self.y = y
		self.n = n
		self.kk = kk
		self.nnn = nnn

	def as_byte_instruction(self) -> bytes:
		instruction = self.op<<4
		if self.nnn:
			instruction = instruction<<8 | self.nnn
		else:
			if self.kk:
				instruction = (instruction | self.x)<<4
				instruction = instruction<<4 | self.kk
			else:
				instruction = (instruction | self.x)<<4
				instruction = (instruction | self.y)<<4
				instruction = (instruction | self.n)
		return instruction.to_bytes(length=INSTRUCTION_LENGTH)

	def __str__(self) -> str:
		return self.as_byte_instruction().hex()

class LoadInstruction(Instruction):
	def __init__(self, name: str, nnn: int = 0):
		super().__init__(op=0xA, nnn=nnn)
		self.name = name

class CodeGenerator:

	def __init__(self, semantic: SemanticAnalyzer):
		self.registers = [True] * REGISTERS

		# Register V0 is used to load variables from memory and VF is used by certain instructions for various stuff
		# This is why they are set as reserved here
		self.registers[V0] = False
		self.registers[VF] = False

		self.semantic = semantic

		self.stack: list[bytes] = []
		self.main: list[Instruction] = []

	def allocate_register(self) -> int:
		for i in range(REGISTERS):
			if self.registers[i]:
				self.registers[i] = False
				return i
		raise CodeGeneratorException("No available registers")

	def free_register(self, register: int):
		self.registers[register] = True

	def generate_integer(self, integer: Integer) -> int:
		register = self.allocate_register()
		self.main.append(Instruction(op=0x6, x=register, kk=integer.value))
		return register

	def generate_identifier(self, identifier: Identifier) -> int:
		register = self.allocate_register()
		mem_location = self.semantic.get_symbol_location(identifier.name)
		self.main.append(Instruction(op=0xA, nnn=mem_location))
		self.main.append(Instruction(op=0xF, x=0, kk=0x65))
		self.main.append(Instruction(op=0x8, x=register, y=0, n=0))
		return register

	def generate_infix(self, infix: Infix) -> int:

		left_register = self.generate_expression(infix.left)
		right_register = self.generate_expression(infix.right)

		match infix.operator.type:
			case TokenType.PLUS:
				self.main.append(Instruction(op=0x8, x=left_register, y=right_register, n=4))
			case TokenType.MINUS:
				self.main.append(Instruction(op=0x8, x=left_register, y=right_register, n=5))
			case TokenType.ASTERISK:
				index_register = self.allocate_register()
				result_register = self.allocate_register()

				self.main.append(Instruction(op=0x6, x=index_register, kk=0))
				self.main.append(Instruction(op=0x6, x=result_register, kk=0))

				self.main.append(Instruction(op=0x9, x=left_register, y=index_register, n=0))
				self.main.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 4))
				self.main.append(Instruction(op=0x8, x=result_register, y=right_register, n=4))
				self.main.append(Instruction(op=0x7, x=index_register, kk=1))
				self.main.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * -4))

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

	def generate_integer_declaration(self, statement: IntegerDeclaration):
		register_value = self.generate_expression(statement.expression)
		mem_location = self.semantic.get_symbol_location(statement.ident.name)
		self.main.append(Instruction(op=0xA, nnn=mem_location))
		if register_value != 0:
			self.main.append(Instruction(op=0x8, x=0, y=register_value, n=0))
		self.main.append(Instruction(op=0xF, x=0, kk=0x55))
		self.stack.append(b'\0')
		self.free_register(register_value)

	def generate_sprite_declaration(self, declaration: SpriteDeclaration):
		for row in declaration.rows:
			self.stack.append(row.value.to_bytes(WORD_SIZE))

	def generate_declaration(self, declaration: Declaration):
		match declaration:
			case IntegerDeclaration():
				self.generate_integer_declaration(declaration)
			case SpriteDeclaration():
				self.generate_sprite_declaration(declaration)
			case _:
				raise CodeGeneratorException(f"Unrecognized declaration {declaration}!")

	def generate_draw_statement(self, statement: DrawStatement):
		name = statement.ident.name
		x = self.generate_expression(statement.x)
		y = self.generate_expression(statement.y)
		n = self.semantic.get_symbol_size(name)
		mem_location = self.semantic.get_symbol_location(name)
		self.main.append(Instruction(op=0xA, nnn=mem_location))
		self.main.append(Instruction(op=0xD, x=x, y=y, n=n))
		self.free_register(x)
		self.free_register(y)

	def generate_statement(self, statement: Statement):
		match statement:
			case ExpressionStatement():
				register = self.generate_expression(statement.expression)
				self.free_register(register)
			case DrawStatement():
				self.generate_draw_statement(statement)
			case Declaration():
				self.generate_declaration(statement)
			case _:
				raise CodeGeneratorException(f"Unrecognized statement {statement}!")

	def write_file(self, filename: str):
		with open(filename, "wb") as output:
			pc = 0
			# This instruction here makes it so that the emulator doesn't
			# spill over the main block and start interpreting the stack
			# as instructions
			self.main.append(Instruction(op=0x1, nnn=0))
			main_length = len(self.main) * INSTRUCTION_LENGTH
			for instruction in self.main:
				match instruction.op:
					case 0xA:
						instruction.nnn = START + main_length + instruction.nnn
					case 0x1:
						instruction.nnn = START + pc + instruction.nnn
				print(instruction)
				output.write(instruction.as_byte_instruction())
				pc += INSTRUCTION_LENGTH

			for sprite in self.stack:
				output.write(sprite)
