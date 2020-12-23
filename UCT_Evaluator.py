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
	test_result += tokenization_expect("a2", ["a", "2"], verbose)
	test_result += tokenization_expect("  a  ", ["a"], verbose)
	test_result += tokenization_expect("a^2", ["a", "^", "2"], verbose)
	test_result += tokenization_expect("a*(b+c)^2 cm = m", ["a", "*", "(", "b", "+", "c", ")", "^", "2", "cm", "=", "m"], verbose)

	return test_result

def aggregation_expect(tokens, expected, verbose):
	if expected == None:
		try:
			tokens = UC_StrParser.aggregateUnits(tokens)
			tokens = UC_StrParser.aggregateQuantities(tokens)
			return test_fail(f"Received {tokens}; expected error", verbose)
		except: return 0
	else:
		tokens = UC_StrParser.aggregateUnits(tokens)
		tokens = UC_StrParser.aggregateQuantities(tokens)
		if tokens != expected: return test_fail(f"Received {tokens}; expected {expected}", verbose)
		return 0

def test_aggregation(verbose = False):
	test_result = 0

	# Test aggregating adjacent units
	test_result += aggregation_expect([], [], verbose)
	test_result += aggregation_expect(["1"], [("1", [])], verbose)
	test_result += aggregation_expect(["1", "cm"], [("1", ["cm"])], verbose)
	test_result += aggregation_expect(["1", "cm", "m"], [("1", ["cm", "*", "m"])], verbose)
	test_result += aggregation_expect(["1", "cm", "*", "m"], [("1", ["cm", "*", "m"])], verbose)
	test_result += aggregation_expect(["(", "1", "cm", ")"], ["(", ("1", ["cm"]), ")"], verbose)

	# Test aggregating exponents
	test_result += aggregation_expect(
		["1", "cm", "^", "2"],
		[("1", ["cm", "^", "2"])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "-", "2"],
		None,
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "(", "2", ")"],
		[("1", ["cm", "^", "(", "2", ")"])],
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "(", "-", "2", ")"],
		None,
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "(", "2", "+", "1", ")"],
		None,
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "(", "cm", ")"],
		None,
	verbose)
	test_result += aggregation_expect(
		["1", "cm", "^", "2", "m"],
		[("1", ["cm", "^", "2", "*", "m"])],
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
		None,
	verbose)
	test_result += aggregation_expect(
		["1", "(", "cm", ")"],
		[("1", []), "(", ("1", ["cm"]), ")"],
	verbose)
	test_result += aggregation_expect(
		["1", "*", "cm"],
		[("1", []), "*", ("1", ["cm"])],
	verbose)

	# Test expressions with invalid operators
	test_result += aggregation_expect(["*", "1", "cm"], None, verbose)
	test_result += aggregation_expect(["1", "cm", "*"], None, verbose)

	return test_result

def rpn_conversion_expect(tokens, expected, verbose):
	if expected == None:
		try:
			tokens = UC_StrParser.convertToRPN(tokens)
			return test_fail(f"Received {tokens}; expected error", verbose)
		except: return 0
	else:
		tokens = UC_StrParser.convertToRPN(tokens)
		if tokens != expected: return test_fail(f"Received {tokens}; expected {expected}", verbose)
		return 0

def test_rpn_conversion(verbose = False):
	test_result = 0

	# Test associativity
	test_result += rpn_conversion_expect([], [], verbose)
	test_result += rpn_conversion_expect(["1", "+", "2", "+", "3"], ["1", "2", "+", "3", "+"], verbose)
	test_result += rpn_conversion_expect(["1", "-", "2", "-", "3"], ["1", "2", "-", "3", "-"], verbose)
	test_result += rpn_conversion_expect(["1", "*", "2", "*", "3"], ["1", "2", "*", "3", "*"], verbose)
	test_result += rpn_conversion_expect(["1", "/", "2", "/", "3"], ["1", "2", "/", "3", "/"], verbose)
	test_result += rpn_conversion_expect(["1", "^", "2", "^", "3"], ["1", "2", "3", "^", "^"], verbose)

	# Test precedence
	test_result += rpn_conversion_expect(["1", "-", "2", "+", "3"], ["1", "2", "-", "3", "+"], verbose)
	test_result += rpn_conversion_expect(["1", "+", "2", "-", "3"], ["1", "2", "+", "3", "-"], verbose)
	test_result += rpn_conversion_expect(["1", "/", "2", "*", "3"], ["1", "2", "/", "3", "*"], verbose)
	test_result += rpn_conversion_expect(["1", "*", "2", "/", "3"], ["1", "2", "*", "3", "/"], verbose)
	test_result += rpn_conversion_expect(["1", "+", "2", "*", "3"], ["1", "2", "3", "*", "+"], verbose)
	test_result += rpn_conversion_expect(["1", "*", "2", "+", "3"], ["1", "2", "*", "3", "+"], verbose)
	test_result += rpn_conversion_expect(["1", "-", "2", "/", "3"], ["1", "2", "3", "/", "-"], verbose)
	test_result += rpn_conversion_expect(["1", "/", "2", "-", "3"], ["1", "2", "/", "3", "-"], verbose)
	test_result += rpn_conversion_expect(["1", "^", "2", "*", "3"], ["1", "2", "^", "3", "*"], verbose)
	test_result += rpn_conversion_expect(["1", "*", "2", "^", "3"], ["1", "2", "3", "^", "*"], verbose)

	# Test brackets
	test_result += rpn_conversion_expect(["(",")"], [], verbose)
	test_result += rpn_conversion_expect(["1", "^", "(", "2", "*", "3", ")"], ["1", "2", "3", "*", "^"], verbose)
	test_result += rpn_conversion_expect(["1", "*", "(", "2", "+", "3", ")"], ["1", "2", "3", "+", "*"], verbose)
	test_result += rpn_conversion_expect(["(", "1", "*", "2", "+", "3", ")"], ["1", "2", "*", "3", "+"], verbose)
	test_result += rpn_conversion_expect(["(", "1", ")", "*", "2", "+", "3"], ["1", "2", "*", "3", "+"], verbose)
	test_result += rpn_conversion_expect(["1", "*", "2", "+", "(", "3", ")"], ["1", "2", "*", "3", "+"], verbose)
	test_result += rpn_conversion_expect(["(", "(", "1", ")", "*", "(", "2", ")", ")"], ["1", "2", "*"], verbose)

	# Test unbalanced brackets
	test_result += rpn_conversion_expect(["("], None, verbose)
	test_result += rpn_conversion_expect(["(", "1", "+", "2"], None, verbose)
	test_result += rpn_conversion_expect(["1", "(", "+", "2"], None, verbose)
	test_result += rpn_conversion_expect(["1", "+", "(", "2"], None, verbose)
	test_result += rpn_conversion_expect(["1", "+", "2", "("], None, verbose)
	test_result += rpn_conversion_expect([")"], None, verbose)
	test_result += rpn_conversion_expect([")", "1", "+", "2"], None, verbose)
	test_result += rpn_conversion_expect(["1", ")", "+", "2"], None, verbose)
	test_result += rpn_conversion_expect(["1", "+", ")", "2"], None, verbose)
	test_result += rpn_conversion_expect(["1", "+", "2", ")"], None, verbose)

	return test_result

def parseUnit_expect(tokens, expected, verbose):
	if expected == None:
		try:
			result = UC_StrParser.parseUnit(tokens)
			return test_fail(f"Received '{result}'; expected error", verbose)
		except: return 0
	else:
		result = UC_StrParser.parseUnit(tokens)
		if result != expected: return test_fail(f"Received '{result}'; expected '{expected}'", verbose)
		return 0

def parseExpr_expect(string, expected, verbose):
	if expected == None:
		try:
			result = str(UC_StrParser.parseExpr(string))
			return test_fail(f"Received '{result}'; expected error", verbose)
		except: return 0
	else:
		result = str(UC_StrParser.parseExpr(string))
		if result != expected: return test_fail(f"Received '{result}'; expected '{expected}'", verbose)
		return 0

def test_parser(verbose = False):
	test_result = 0

	# Test exponents
	test_result += parseUnit_expect([], {}, verbose)
	test_result += parseUnit_expect(["cm"], {"cm": 1}, verbose)
	test_result += parseUnit_expect(["cm", "^", "1"], {"cm": 1}, verbose)
	test_result += parseUnit_expect(["cm", "^", "(", "1", "+", "1", ")"], {"cm": 2}, verbose)
	test_result += parseUnit_expect(["cm", "^", "(", "+1", ")"], {"cm": 1}, verbose)
	test_result += parseUnit_expect(["cm", "^", "(", "1", "+", "cm", ")"], None, verbose)
	test_result += parseUnit_expect(["cm", "^", "cm"], None, verbose)

	# Test multi-unit expressions
	# FIXME: Test using AST equality instead
	test_result += parseExpr_expect(["+1"], "1.0", verbose)
	test_result += parseExpr_expect(["1", "cm"], "1.0 cm", verbose)
	# test_result += parseExpr_expect(["1", "cm", "=", "1", "m"], "1.0 cm = 1.0 m", verbose)
	test_result += parseExpr_expect(["1", "cm", "+", "1", "m"], "(1.0 cm + 1.0 m)", verbose)
	test_result += parseExpr_expect(["1", "cm", "-", "1", "m"], "(1.0 cm - 1.0 m)", verbose)
	test_result += parseExpr_expect(["1", "cm", "*", "1", "m"], "(1.0 cm * 1.0 m)", verbose)
	test_result += parseExpr_expect(["1", "cm", "/", "1", "m"], "(1.0 cm / 1.0 m)", verbose)
	test_result += parseExpr_expect(["1", "cm", "^", "1", "cm"], "1.0 cm^(2)", verbose)
	test_result += parseExpr_expect(["1", "cm", "^", "1", "m"], "1.0 m cm", verbose)
	test_result += parseExpr_expect(["1", "cm", "^", "(", "1", "cm", ")"], None, verbose)

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