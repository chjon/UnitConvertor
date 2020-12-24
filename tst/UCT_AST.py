from src.UC_AST import *
from src.UC_Unit import *
from src.UC_Convertor import *

def test_fail(msg, verbose):
	if verbose: print(f"Test failed: {msg}")
	return 1

def conversion_expect(left, right, expected, convertor, verbose):
	if expected == None:
		try:
			result = convertor.convert(left, right)
			return test_fail(f"Received '{result}'; expected error", verbose)
		except: return 0
	else:
		result = convertor.convert(left, right)
		if result != expected: return test_fail(f"Received '{result}'; expected '{expected}'", verbose)
		return 0

def test_conversion(verbose = False):
	test_result = 0

	units = {
		"m": Unit("m"),
		"two_m": Unit("two_m", {"m": 1}),
		"square_m": Unit("m", {"m": 2}),
		"L": Unit("L", {"dm": 3}),
	}
	conversions = {
		"two_m": 2,
		"square_m": 1,
		"L": 1
	}
	prefixes = {
		"d": (10, 2),
		"c": (10, -2)
	}
	convertor = Convertor(units, conversions, prefixes)

	# Test conversion between identical units
	test_result += conversion_expect(Unit("m"), Unit("m"), 1, convertor, verbose)
	test_result += conversion_expect(Unit("cm"), Unit("cm"), 1, convertor, verbose)
	test_result += conversion_expect(Unit("two_m"), Unit("two_m"), 1, convertor, verbose)
	test_result += conversion_expect(Unit("square_m"), Unit("square_m"), 1, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": 1}), Unit(baseUnits = {"m": 1}), 1, convertor, verbose)

	# Test conversion between directly compatible units
	test_result += conversion_expect(Unit("m"), Unit(baseUnits = {"m": 1}), 1, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": 1}), Unit("m"), 1, convertor, verbose)
	test_result += conversion_expect(Unit("m"), Unit("two_m"), 0.5, convertor, verbose)
	test_result += conversion_expect(Unit("two_m"), Unit("m"), 2, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": 2}), Unit("square_m"), 1, convertor, verbose)
	test_result += conversion_expect(Unit("square_m"), Unit(baseUnits = {"m": 2}), 1, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"two_m": 2}), Unit("square_m"), 4, convertor, verbose)
	test_result += conversion_expect(Unit("square_m"), Unit(baseUnits = {"two_m": 2}), 0.25, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"two_m": 2}), Unit(baseUnits = {"square_m": 1}), 4, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"square_m": 1}), Unit(baseUnits = {"two_m": 2}), 0.25, convertor, verbose)

	# Test conversion with a prefix
	test_result += conversion_expect(Unit("m"), Unit("cm"), 100, convertor, verbose)
	test_result += conversion_expect(Unit("m"), Unit(baseUnits = {"cm": 1}), 100, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": 1}), Unit(baseUnits = {"cm": 1}), 100, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": 1}), Unit("cm"), 100, convertor, verbose)
	test_result += conversion_expect(Unit("cm"), Unit("m"), 0.01, convertor, verbose)
	test_result += conversion_expect(Unit("cm"), Unit(baseUnits = {"m": 1}), 0.01, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"cm": 1}), Unit(baseUnits = {"m": 1}), 0.01, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"cm": 1}), Unit("m"), 0.01, convertor, verbose)

	# Test conversion with dependent units
	test_result += conversion_expect(Unit(baseUnits = {"m": 1, "square_m": -1}), Unit(baseUnits = {"m": -1}), 1, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": -1, "square_m": 1}), Unit(baseUnits = {"m": 1}), 1, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": -1, "square_m": 1}), Unit("m"), 1, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": 1, "square_m": -1}), Unit(baseUnits = {"cm": -1}), 0.01, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": -1, "square_m": 1}), Unit(baseUnits = {"cm": 1}), 100, convertor, verbose)
	test_result += conversion_expect(Unit(baseUnits = {"m": -1, "square_m": 1}), Unit("cm"), 100, convertor, verbose)

	# Test conversion where derived units have a base unit with a prefix
	test_result += conversion_expect(Unit(baseUnits = {"dm": 1, "L": -1}), Unit(baseUnits = {"dm": -2}), 1, convertor, verbose)

	return test_result

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
		"square_m": Unit("m", {"m": 2}),
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
	test_result += ast_expect(
		AST_Add(
			Quantity(1, Unit(baseUnits = {"m", 2})),
			Quantity(1, Unit(baseUnits = {"m", 2}))
		),
		Quantity(2, Unit(baseUnits = {"m", 2})),
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
			Quantity(1, Unit(baseUnits = {"m": 2})),
			Quantity(1, Unit("square_m"))
		),
		Quantity(2, Unit("square_m")),
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
	print(f"test_conversion: {test_conversion(verbose)} tests failed")
	print(f"test_ast: {test_ast(verbose)} tests failed")

if (__name__ == "__main__"):
	main()