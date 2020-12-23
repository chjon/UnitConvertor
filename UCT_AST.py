from UC_AST import *
from UC_Unit import *
from UC_Convertor import Convertor

def ast_expect(ast, expected, convertor, verbose):
	if expected == None:
		try:
			result = ast.evaluate(convertor)
			return test_fail(f"Received '{result}'; expected error", verbose)
		except: return 0
	else:
		result = ast.evaluate(convertor)
		if result != expected: return test_fail(f"Received '{result}'; expected '{expected}'", verbose)
		return 0

def test_ast(verbose = False):
	test_result = 0

	units = {
		"m": Unit("m"),
		"two_m": Unit("two_m", {"m": 1}),
	}
	conversions = {"two_m": 2}
	prefixes = {"c": (10, -2)}
	convertor = Convertor(units, conversions, prefixes)

	# Test addition of identical units
	test_result += ast_expect(
		AST_Add(
			Quantity(1, Unit("m")),
			Quantity(1, Unit("m"))
		),
		Quantity(2, Unit("m")),
	convertor, verbose)

	# Test addition of compatible units
	test_result += ast_expect(
		AST_Add(
			Quantity(1, Unit("two_m")),
			Quantity(1, Unit("m"))
		),
		Quantity(3, Unit("m")),
	convertor, verbose)
	test_result += ast_expect(
		AST_Add(
			Quantity(1, Unit("m")),
			Quantity(1, Unit("two_m"))
		),
		Quantity(1.5, Unit("two_m")),
	convertor, verbose)
	test_result += ast_expect(
		AST_Add(
			Quantity(1, Unit("cm")),
			Quantity(1, Unit("m"))
		),
		Quantity(1.01, Unit("m")),
	convertor, verbose)

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_ast: {test_ast(verbose)} tests failed")

if (__name__ == "__main__"):
	main()