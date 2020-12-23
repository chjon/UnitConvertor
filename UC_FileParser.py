from UC_Unit import *
from UC_Utils import *
from UC_Common import *

def parseBaseUnitMap(tokens):
	"""
	Convert the next series of tokens into a map of units to exponents
	@param tokens: a list of tokens
	@return pairs of units and their corresponding exponents
	"""
	baseUnitMap = {}

	baseSym = parseSymbol(tokens)
	if baseSym not in baseUnitMap: baseUnitMap[baseSym] = 0
	baseUnitMap[baseSym] += parseInt(tokens)

	while peekNextToken(tokens) == SEP_DELIMITER:
		getNextToken(tokens)
		baseSym = parseSymbol(tokens)
		if baseSym not in baseUnitMap: baseUnitMap[baseSym] = 0
		baseUnitMap[baseSym] += parseInt(tokens)

	getNextToken(tokens, END_DELIMITER)
	return baseUnitMap

def parseUnit(units, conversions, tokens):
	"""
	Convert the next series of tokens into a unit
	@param units: a map of unit symbols to unit objects to be modified
	@param conversions: a map of unit symbols to scale factors to be modified
	@param tokens: a list of tokens
	"""
	baseUnitMap = {}

	# Handle base unit
	sym = parseSymbol(tokens)
	if sym in units: raise FileFormatError(f"Duplicate definition of unit '{sym}'")

	# Handle derived unit
	nextToken = getNextToken(tokens)
	if nextToken == MAP_DELIMITER:
		scaleFactor = parseFloat(tokens)
		getNextToken(tokens, SEP_DELIMITER)
		baseUnitMap = parseBaseUnitMap(tokens)
		conversions[sym] = scaleFactor
	
	# Handle other tokens
	elif nextToken != END_DELIMITER: raise FileFormatError(f"Expected delimiter; received '{nextToken}'")

	# Create unit
	units[sym] = Unit(sym, baseUnitMap)

def parsePrefixMapping(prefixes, tokens, base):
	"""
	Convert the next series of tokens into a prefix-exponent pair
	@param prefixes: the prefix-exponent map to modify
	@param tokens: a list of tokens
	@param base: the base for the exponent
	"""
	prefix = getNextToken(tokens)
	if prefix in prefixes: raise FileFormatError(f"Duplicate definition of prefix '{prefix}'")
	prefixes[prefix] = (base, parseInt(tokens))

def parsePrefix(prefixes, tokens):
	"""
	Convert the next series of tokens into prefix-exponent pairs
	@param prefixes: the prefix-exponent map to modify
	@param tokens: a list of tokens
	"""
	base = parseFloat(tokens)
	getNextToken(tokens, MAP_DELIMITER)

	parsePrefixMapping(prefixes, tokens, base)
	while peekNextToken(tokens) == SEP_DELIMITER:
		getNextToken(tokens)
		parsePrefixMapping(prefixes, tokens, base)	
	getNextToken(tokens, END_DELIMITER)

# Recursive descent parsing
def parseFile(tokens):
	"""
	Convert a list of tokens into maps of units, conversions, and prefixes
	@param tokens: a list of tokens
	@return units: a map of unit symbols to unit objects
	@return conversions: a map of derived unit symbols to scale factors
	@return prefixes: a map of prefixes to exponents
	"""
	units = {}
	conversions = {}
	prefixes = {}
	while len(tokens):
		if isValidSymbol(tokens[0]):
			parseUnit(units, conversions, tokens)
		else:
			parsePrefix(prefixes, tokens)

	# Return result of parsing
	return units, conversions, prefixes