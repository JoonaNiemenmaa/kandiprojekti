from parser import Parser

def test_statement_parser():

	test_cases = (
		("5 + 5;", "(5 + 5)"),
		("20 + 5 - 5;", "((20 + 5) - 5)"),
		("20 - (5 + 5);", "(20 - (5 + 5))"),
		("1 - 2 * 1;", "(1 - (2 * 1))"),
		("1 - 2 / 1;", "(1 - (2 / 1))"),
		("(255 + 10) / 3 * 10 + (10 + 5 - 5);", "((((255 + 10) / 3) * 10) + ((10 + 5) - 5))"),
		("var numero = 10;", "var numero = 10"),
		("var lasku = 20 + 5 - 10;", "var lasku = ((20 + 5) - 10)"),
	)

	for case, expected in test_cases:
		print(case, expected)
		parser = Parser(case)
		statement = parser.parse_statement()
		assert statement.__str__() == expected
