import UC_StrParser

def test_fail(msg, verbose):
	if verbose: print(f"Test failed: {msg}")
	return 1

def tokenization_expect(string, expected, verbose):
	tokens = UC_StrParser.tokenize(string)
	if tokens != expected: return test_fail(f"Received {tokens}; expected {expected}", verbose)
	return 0

def test_tokenization(verbose = False):
	test_result = 0

	# Check that float-like symbols are handled properly
	test_result += tokenization_expect("1", ["1"], verbose)
	test_result += tokenization_expect(".1", [".1"], verbose)
	test_result += tokenization_expect("1.", ["1."], verbose)
	test_result += tokenization_expect(".", ["."], verbose)
	test_result += tokenization_expect("1.0", ["1.0"], verbose)
	test_result += tokenization_expect("1e", ["1", "e"], verbose)
	test_result += tokenization_expect("1.e", ["1.", "e"], verbose)
	test_result += tokenization_expect("1.0e", ["1.0", "e"], verbose)
	test_result += tokenization_expect("1.0e-", ["1.0", "e", "-"], verbose)
	test_result += tokenization_expect("1.0e-a", ["1.0", "e", "-", "a"], verbose)
	test_result += tokenization_expect("1.0ea", ["1.0", "ea"], verbose)
	test_result += tokenization_expect("1.0e3", ["1.0e3"], verbose)
	test_result += tokenization_expect("1.0e3a", ["1.0e3", "a"], verbose)
	test_result += tokenization_expect("1.0e-3a", ["1.0e-3", "a"], verbose)
	test_result += tokenization_expect("1.0 e-3a", ["1.0", "e", "-", "3", "a"], verbose)
	test_result += tokenization_expect("1. 0e-3a", ["1.", "0e-3", "a"], verbose)

	# Check that non-floats are handled properly 
	test_result += tokenization_expect("", [], verbose)
	test_result += tokenization_expect("    ", [], verbose)
	test_result += tokenization_expect("a", ["a"], verbose)
	test_result += tokenization_expect("  a  ", ["a"], verbose)
	test_result += tokenization_expect("a^2", ["a", "^", "2"], verbose)
	test_result += tokenization_expect("a*(b+c)^2 cm = m", ["a", "*", "(", "b", "+", "c", ")", "^", "2", "cm", "=", "m"], verbose)

	return test_result

def aggregation_expect(tokens, expected, verbose):
	if expected == None:
		try:
			tokens = UC_StrParser.aggregate(tokens)
			return test_fail(f"Received {tokens}; expected error", verbose)
		except: return 0
	else:
		tokens = UC_StrParser.aggregate(tokens)
		if tokens != expected: return test_fail(f"Received {tokens}; expected {expected}", verbose)
		return 0

def test_aggregation(verbose = False):
	test_result = 0

	# Test aggregating adjacent units
	test_result += aggregation_expect([], [], verbose)
	test_result += aggregation_expect(["1"], [("1", [])], verbose)
	test_result += aggregation_expect(["1", "cm"], [("1", ["cm"])], verbose)
	test_result += aggregation_expect(["1", "cm", "m"], [("1", ["cm", "m"])], verbose)
	test_result += aggregation_expect(["1", "cm", "*", "m"], [("1", ["cm", "*", "m"])], verbose)
	test_result += aggregation_expect(["(", "1", "cm", ")"], ["(", ("1", ["cm"]), ")"], verbose)

	# Test aggregating exponents
	test_result += aggregation_expect(
		["1", "cm", "^", "2"],
		[("1", ["cm", "^", "2"])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "-", "2"],
		[("1", ["cm", "^", "-", "2"])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "(", "2", ")"],
		[("1", ["cm", "^", "(", "2", ")"])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "(", "-", "2", ")"],
		[("1", ["cm", "^", "(", "-", "2", ")"])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "(", "2", "+", "1", ")"],
		[("1", ["cm", "^", "(", "2", "+", "1", ")"])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "(", "cm", ")"],
		None,
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "2", "m"],
		[("1", ["cm", "^", "2", "m"])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "2", "*", "m"],
		[("1", ["cm", "^", "2", "*", "m"])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "2", "*", "1"],
		[("1", ["cm", "^", "2"]), "*", ("1", [])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "2", "*", "1", "m"],
		[("1", ["cm", "^", "2"]), "*", ("1", ["m"])],
	verbose)

	# Test values/units with no immediately adjacent units/values
	test_result += aggregation_expect(
		["(", ")"],
		["(", ")"],
	verbose)
	test_result += aggregation_expect(
		["1", "(", "cm", ")"],
		[("1", []), "(", ("1", ["cm"]), ")"],
	verbose)
	test_result += aggregation_expect(
		["1", "*", "cm"],
		[("1", []), "*", ("1", ["cm"])],
	verbose)

	return test_result

def test_rpn_conversion(verbose = False):
	test_result = 0
	return test_result

def test_parser(verbose = False):
	test_result = 0

	tokens = UC_StrParser.parseExpr("15 cm^2 / m^2 + 18")
	print(tokens)

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_tokenization: {test_tokenization(verbose)} tests failed")
	print(f"test_aggregation: {test_aggregation(verbose)} tests failed")
	print(f"test_rpn_conversion: {test_rpn_conversion(verbose)} tests failed")
	print(f"test_parser: {test_parser(verbose)} tests failed")

if (__name__ == "__main__"):
	main()