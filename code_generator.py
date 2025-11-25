from abstract_syntax_tree import Integer, Identifier, Infix, Expression, If, While, Clear, Draw, ExpressionStatement, IntegerDeclaration, SpriteDeclaration, Block, Statement, DrawNum, DrawChar, Pressed, UntilPressed, NotPressed
from tokens import TokenType

from semantic_analyzer import SemanticAnalyzer
import semantic_analyzer

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

# class LoadInstruction(Instruction):
# 	def __init__(self, name: str, nnn: int = 0):
# 		super().__init__(op=0xA, nnn=nnn)
# 		self.name = name

class CodeGenerator:

	def __init__(self, semantic: SemanticAnalyzer):
		self.registers = [True] * REGISTERS

		# Register V0 is used to load variables from memory and VF is used by certain instructions for various stuff
		# This is why they are set as reserved here
		self.registers[V0] = False
		self.registers[VF] = False

		self.semantic = semantic

		self.sprites: dict[str, bytes] = {}
		self.main: list[Instruction] = []

		# This op makes sure that a window is spawned when initializing the emulator
		self.main.append(Instruction(op=0x0, nnn=0x0E0))


	def allocate_register(self) -> int:
		for i in range(REGISTERS):
			if self.registers[i]:
				self.registers[i] = False
				return i
		raise CodeGeneratorException("No available registers")

	def free_register(self, register: int):
		if register not in (V0, VF):
			self.registers[register] = True

	def generate_integer(self, integer: Integer, block: list[Instruction]) -> int:
		register = self.allocate_register()
		block.append(Instruction(op=0x6, x=register, kk=integer.value))
		return register

	def generate_identifier(self, identifier: Identifier, block: list[Instruction]) -> int:
		register = self.allocate_register()
		mem_location = self.semantic.get_symbol_location(identifier.name)
		block.append(Instruction(op=0xA, nnn=mem_location))
		block.append(Instruction(op=0xF, x=0, kk=0x65))
		block.append(Instruction(op=0x8, x=register, y=0, n=0))
		return register

	def generate_draw(self, call: Draw, block: list[Instruction]) -> int:
		name = call.ident.name
		x = self.generate_expression(call.x, block)
		y = self.generate_expression(call.y, block)
		n = self.semantic.get_symbol_size(name)
		mem_location = self.semantic.get_symbol_location(name)
		block.append(Instruction(op=0xA, nnn=mem_location))
		block.append(Instruction(op=0xD, x=x, y=y, n=n))
		self.free_register(x)
		self.free_register(y)
		return VF

	def generate_draw_num(self, call: DrawNum, block: list[Instruction]) -> int:
		sprite_width = 4
		sprite_height = 5
		number = self.generate_expression(call.number, block)
		block.append(Instruction(op=0xA, nnn=0))
		block.append(Instruction(op=0xF, x=number, kk=0x33))
		self.free_register(number)
		x = self.generate_expression(call.x, block)
		y = self.generate_expression(call.y, block)
		block.append(Instruction(op=0xF, x=0, kk=0x65))
		block.append(Instruction(op=0xF, x=0, kk=0x29))
		block.append(Instruction(op=0xD, x=x, y=y, n=sprite_height))
		block.append(Instruction(op=0x7, x=x, kk=sprite_width + 1))
		block.append(Instruction(op=0xA, nnn=1))
		block.append(Instruction(op=0xF, x=0, kk=0x65))
		block.append(Instruction(op=0xF, x=0, kk=0x29))
		block.append(Instruction(op=0xD, x=x, y=y, n=sprite_height))
		block.append(Instruction(op=0x7, x=x, kk=sprite_width + 1))
		block.append(Instruction(op=0xA, nnn=2))
		block.append(Instruction(op=0xF, x=0, kk=0x65))
		block.append(Instruction(op=0xF, x=0, kk=0x29))
		block.append(Instruction(op=0xD, x=x, y=y, n=sprite_height))
		self.free_register(x)
		self.free_register(y)
		return VF

	def generate_draw_char(self, call: DrawChar, block: list[Instruction]) -> int:
		number = self.generate_expression(call.char, block)
		block.append(Instruction(op=0xF, x=number, kk=0x29))
		self.free_register(number)
		x = self.generate_expression(call.x, block)
		y = self.generate_expression(call.y, block)
		block.append(Instruction(op=0xD, x=x, y=y, n=5))
		self.free_register(x)
		self.free_register(y)
		return VF

	def generate_infix(self, infix: Infix, block: list[Instruction]) -> int:

		left_register = self.generate_expression(infix.left, block)
		right_register = self.generate_expression(infix.right, block)

		match infix.operator.type:
			case TokenType.PLUS:
				block.append(Instruction(op=0x8, x=left_register, y=right_register, n=4))
			case TokenType.MINUS:
				block.append(Instruction(op=0x8, x=left_register, y=right_register, n=5))
			case TokenType.ASTERISK:
				index_register = self.allocate_register()
				result_register = self.allocate_register()

				block.append(Instruction(op=0x6, x=index_register, kk=0))
				block.append(Instruction(op=0x6, x=result_register, kk=0))

				block.append(Instruction(op=0x9, x=left_register, y=index_register, n=0))
				block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 4))
				block.append(Instruction(op=0x8, x=result_register, y=right_register, n=4))
				block.append(Instruction(op=0x7, x=index_register, kk=1))
				block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * -4))

				self.free_register(index_register)
				self.free_register(left_register)
				left_register = result_register
			case TokenType.EQUALS:
				block.append(Instruction(op=0x5, x=left_register, y=right_register, n=0))
				block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 3))
				block.append(Instruction(op=0x6, x=left_register, kk=1))
				block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 2))
				block.append(Instruction(op=0x6, x=left_register, kk=0))
			case TokenType.NOT_EQUALS:
				block.append(Instruction(op=0x5, x=left_register, y=right_register, n=0))
				block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 3))
				block.append(Instruction(op=0x6, x=left_register, kk=0))
				block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 2))
				block.append(Instruction(op=0x6, x=left_register, kk=1))
			case _:
				raise CodeGeneratorException(f"Invalid operator '{infix.operator}'!")

		self.free_register(right_register)

		return left_register

	def generate_pressed_call(self, pressed: Pressed, block: list[Instruction]) -> int:
		register = self.generate_expression(pressed.expression, block)
		block.append(Instruction(op=0xE, x=register, kk=0x9E))
		block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 3))
		block.append(Instruction(op=0x6, x=register, kk=1))
		block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 2))
		block.append(Instruction(op=0x6, x=register, kk=0))
		return register

	def generate_not_pressed_call(self, not_pressed: NotPressed, block: list[Instruction]) -> int:
		register = self.generate_expression(not_pressed.expression, block)
		block.append(Instruction(op=0xE, x=register, kk=0xA1))
		block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 3))
		block.append(Instruction(op=0x6, x=register, kk=1))
		block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * 2))
		block.append(Instruction(op=0x6, x=register, kk=0))
		return register

	def generate_until_pressed_call(self, until_pressed: UntilPressed, block: list[Instruction]) -> int:
		register = self.allocate_register()
		block.append(Instruction(op=0xF, x=register, kk=0x0A))
		return register

	def generate_expression(self, expression: Expression, block: list[Instruction]) -> int:
		match expression:
			case Integer():
				register = self.generate_integer(expression, block)
			case Identifier():
				register = self.generate_identifier(expression, block)
			case Infix():
				register = self.generate_infix(expression, block)
			case Draw():
				register = self.generate_draw(expression, block)
			case DrawNum():
				register = self.generate_draw_num(expression, block)
			case DrawChar():
				register = self.generate_draw_char(expression, block)
			case Pressed():
				register = self.generate_pressed_call(expression, block)
			case NotPressed():
				register = self.generate_not_pressed_call(expression, block)
			case UntilPressed():
				register = self.generate_until_pressed_call(expression, block)
			case _:
				raise CodeGeneratorException("Invalid expression type")
		return register

	def generate_integer_declaration(self, statement: IntegerDeclaration, block: list[Instruction]):
		register_value = self.generate_expression(statement.expression, block)
		mem_location = self.semantic.get_symbol_location(statement.ident.name)
		block.append(Instruction(op=0xA, nnn=mem_location))
		if register_value != 0:
			block.append(Instruction(op=0x8, x=0, y=register_value, n=0))
		block.append(Instruction(op=0xF, x=0, kk=0x55))
		#self.sprites.append(b'\0')
		self.free_register(register_value)

	def generate_sprite_declaration(self, declaration: SpriteDeclaration):
		self.sprites[declaration.ident.name] = b''
		for row in declaration.rows:
			self.sprites[declaration.ident.name] += row.value.to_bytes(WORD_SIZE)

	def generate_draw_statement(self, statement: Draw, block: list[Instruction]):
		name = statement.ident.name
		x = self.generate_expression(statement.x, block)
		y = self.generate_expression(statement.y, block)
		n = self.semantic.get_symbol_size(name)
		mem_location = self.semantic.get_symbol_location(name)
		block.append(Instruction(op=0xA, nnn=mem_location))
		block.append(Instruction(op=0xD, x=x, y=y, n=n))
		self.free_register(x)
		self.free_register(y)

	def generate_clear_statement(self, statement: Clear, block: list[Instruction]):
		block.append(Instruction(op=0x0, kk=0xE0))

	def generate_if_statement(self, if_statement: If, block: list[Instruction]):
		condition = self.generate_expression(if_statement.condition, block)
		block.append(Instruction(op=4, x=condition, kk=0))
		consequence = []
		for statement in if_statement.consequence.statements:
			self.generate_statement(statement, consequence)
		alternative = []
		if if_statement.alternative:
			for statement in if_statement.alternative.statements:
				self.generate_statement(statement, alternative)
			consequence.append(Instruction(op=1, nnn=INSTRUCTION_LENGTH * (len(alternative) + 1)))
		block.append(Instruction(op=1, nnn=INSTRUCTION_LENGTH * (len(consequence) + 1)))
		block += consequence
		block += alternative
		self.free_register(condition)

	def generate_while_statement(self, while_statement: While, block: list[Instruction]):
		condition = []
		register = self.generate_expression(while_statement.condition, condition)
		block += condition
		block.append(Instruction(op=4, x=register, kk=0))
		consequence = []
		for statement in while_statement.block.statements:
			self.generate_statement(statement, consequence)
		block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * (len(consequence) + 2)))
		block += consequence
		block.append(Instruction(op=0x1, nnn=INSTRUCTION_LENGTH * -(len(consequence) + 2 + len(condition))))
		
	def generate_statement(self, statement: Statement, block: list[Instruction]):
		match statement:
			case ExpressionStatement():
				register = self.generate_expression(statement.expression, block)
				self.free_register(register)
			case Clear():
				self.generate_clear_statement(statement, block)
			case If():
				self.generate_if_statement(statement, block)
			case While():
				self.generate_while_statement(statement, block)
			case IntegerDeclaration():
				self.generate_integer_declaration(statement, block)
			case SpriteDeclaration():
				self.generate_sprite_declaration(statement)
			case _:
				raise CodeGeneratorException(f"Unrecognized statement {statement}!")

	def write_file(self, filename: str):
		with open(filename, "wb") as output:
			pc = 0
			size = 0
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
				output.write(instruction.as_byte_instruction())
				#print(f"{pc}: op={instruction.op} nnn={instruction.nnn - START if instruction.nnn else None}")
				pc += INSTRUCTION_LENGTH
				size += INSTRUCTION_LENGTH

			# These are needed for draw_num
			output.write(b'\0\0\0')

			for name, type in self.semantic.symbols.items():
				#print(name)
				match type:
					case semantic_analyzer.Integer():
						output.write(b'\0')
						#print("0")
					case semantic_analyzer.Sprite():
						output.write(self.sprites[name])
						#print(self.sprites[name].hex())
			

			print(f"The program is {size} bytes large!")
