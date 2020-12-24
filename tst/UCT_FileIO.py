from decimal import Decimal
import src.UC_Common as UC_Common
import src.UC_Utils as UC_Utils
import src.UC_FileIO as UC_FileIO
import src.UC_FileParser as UC_FileParser
import src.UC_FileSerializer as UC_FileSerializer

def test_fail(msg, verbose):
	if verbose: print(f"Test failed: {msg}")
	return 1

def tokenize_expect(toTokenize, expected, verbose):
	tokens = UC_FileIO.tokenize(toTokenize)
	if tokens != expected: return test_fail(f"Expected {expected}, received {tokens}", verbose)
	return 0

def test_tokenization(verbose = False):
	test_result = 0
	
	# Test empty input list
	test_result += tokenize_expect(
		[],
		[],
	verbose)

	# Test empty string
	test_result += tokenize_expect(
		[""],
		[],
	verbose)

	# Test whitespace string
	test_result += tokenize_expect(
		["     \t  \r\n   "],
		[],
	verbose)

	# Test string padded with whitespace
	test_result += tokenize_expect(
		["        ABC  "],
		["ABC"],
	verbose)

	# Test multiple whitespace-separated strings
	test_result += tokenize_expect(
		["A BC   DEF G"],
		["A", "BC", "DEF", "G"],
	verbose)

	# Test multiple delimiter-separated strings
	test_result += tokenize_expect(
		["A:1;B:2,H 1,He 2; "],
		["A", ":", "1", ";", "B", ":", "2", ",", "H", "1", ",", "He", "2", ";"],
	verbose)

	# Test multiple input lines
	test_result += tokenize_expect(
		["", "   ABC \t  \r\n  D", "A BC   DEF G"],
		["ABC", "D", "A", "BC", "DEF", "G"],
	verbose)

	return test_result

def test_parser(verbose = False):
	test_result = 0

	# Test token queue
	tokens = ["A1", "B2", "C3"]
	if UC_Utils.getNextToken(tokens) != "A1": test_result += test_fail("Failed to get expected symbol", verbose)
	if UC_Utils.getNextToken(tokens) != "B2": test_result += test_fail("Failed to get expected symbol", verbose)
	if UC_Utils.getNextToken(tokens) != "C3": test_result += test_fail("Failed to get expected symbol", verbose)
	try:
		token = UC_Utils.getNextToken(tokens)
		test_result += test_fail(f"Received unexpected token {token}", verbose)
	except: pass

	# Test the parsing of basic datatypes
	res = UC_Utils.parseInt(["2"])
	if res != Decimal("2"): test_result += test_fail("Incorrectly parsed int", verbose)
	res = UC_Utils.parseFloat(["2.7"])
	if res != Decimal("2.7"): test_result += test_fail("Incorrectly parsed float", verbose)
	res = UC_Utils.parseSymbol(["sym"])
	if res != "sym": test_result += test_fail("Incorrectly parsed symbol", verbose)

	# Test the parsing of unit dependencies
	baseUnitMap = UC_FileParser.parseBaseUnitMap(["A", "1", ",", "B", "2", ";"])
	if baseUnitMap["A"] != 1: test_result += test_fail("Incorrectly parsed base unit map", verbose)
	if baseUnitMap["B"] != 2: test_result += test_fail("Incorrectly parsed base unit map", verbose)
	if len(baseUnitMap) != 2: test_result += test_fail("Incorrectly parsed base unit map", verbose)
	try:
		baseUnitMap = UC_FileParser.parseBaseUnitMap(["A", "1", ",", "B", "2", "C"])
		test_result += test_fail("Should fail to parse an incorrectly formatted dependency string", verbose)
	except: pass

	# Test the parsing of a base unit
	units = {}
	conversions = {}
	UC_FileParser.parseUnit(units, conversions, ["A", ";"])
	if (("A" not in units) or
		("A" in conversions) or
		(len(units) != 1)
	): test_result += test_fail("Incorrectly parsed base unit", verbose)
	try:
		UC_FileParser.parseUnit(["A", "B"])
		test_result += test_fail("Should fail to parse an incorrectly formatted base unit string", verbose)
	except: pass
	
	# Test the parsing of a derived unit
	UC_FileParser.parseUnit(units, conversions, ["H", ":", "12.4", ",", "A", "1", ",", "B", "2", ";"])
	if (("H" not in units) or
		(units["H"].baseUnits["A"] != 1) or 
		(units["H"].baseUnits["B"] != 2) or 
		(len(units["H"].baseUnits) != 2) or
		(conversions["H"] != Decimal("12.4")) or
		(len(units) != 2)
	): test_result += test_fail("Incorrectly parsed derived unit", verbose)
	try:
		UC_FileParser.parseUnit(units, conversions, ["H", ":", "12.4", ",", "A", "1", ",", "B", "2", "C"])
		test_result += test_fail("Should fail to parse an incorrectly formatted derived unit string", verbose)
	except: pass
	try:
		UC_FileParser.parseUnit(units, conversions, ["H", ":", "12.4", ";"])
		test_result += test_fail("Should fail to parse an incorrectly formatted derived unit string", verbose)
	except: pass

	# Test the parsing of a prefix map
	prefixes = {}
	UC_FileParser.parsePrefix(prefixes, ["10", ":", "k", "3", ",", "M", "6", ";"])
	if ((len(prefixes) != 2) or
		(prefixes["k"] != (10, 3)) or
		(prefixes["M"] != (10, 6))
	): test_result += test_fail("Incorrectly parsed prefix map", verbose)
	try:
		UC_FileParser.parsePrefix(prefixes, ["10", ":", "k", "3", ",", "M", "6", "C"])
		test_result += test_fail("Should fail to parse an incorrectly formatted prefix map string", verbose)
	except: pass
	try:
		UC_FileParser.parsePrefix(prefixes, ["10", ":", ";"])
		test_result += test_fail("Should fail to parse an incorrectly formatted prefix map string", verbose)
	except: pass
	
	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_tokenization: {test_tokenization(verbose)} tests failed")
	print(f"test_parser: {test_parser(verbose)} tests failed")

if (__name__ == "__main__"):
	main()