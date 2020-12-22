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

def test_parser(verbose = False):
	test_result = 0

	tokens = UC_StrParser.tokenize("15 cm^2-1.7e-17 mm *8mm +1e+1.e + 1.3e +1.4e-e 3.4 m^(0+1)")
	print(tokens)
	tokens = UC_StrParser.aggregateUnits(tokens)
	print(tokens)
	tokens = UC_StrParser.convertToRPN(tokens)

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_tokenization: {test_tokenization(verbose)} tests failed")
	print(f"test_parser: {test_parser(verbose)} tests failed")

if (__name__ == "__main__"):
	main()