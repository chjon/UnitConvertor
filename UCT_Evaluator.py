import UC_StrParser

def test_fail(msg, verbose):
	if verbose: print(f"Test failed: {msg}")
	return 1

def test_parser(verbose = False):
	test_result = 0

	tokens = UC_StrParser.tokenize("1 (mm^2)")
	tokens = UC_StrParser.aggregateUnits(tokens)
	tokens = UC_StrParser.convertToRPN(tokens)
	print(tokens)

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_parser: {test_parser(verbose)} tests failed")

if (__name__ == "__main__"):
	main()