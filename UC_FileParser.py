from UC_Unit import *
from UC_Common import *

def isValidSymbol(sym):
	"""
	Determine whether a character is a valid unit symbol
	@param sym: the string to check
	@return True if the character is a valid unit symbol, False otherwise
	"""
	for char in sym:
		if (not char.isalpha()) and (char != '_'): return False
	return True

def isWhitespace(char):
	"""
	Determine whether a character is whitespace
	@param char: the character to check
	@return True if the character is whitespace, False otherwise
	"""
	return char == ' ' or char == '\t' or char == '\r' or char == '\n'

def isDelimiter(char):
	"""
	Determine whether a character is a delimiter
	@param char: the character to check
	@return True if the character is a delimiter, False otherwise
	"""
	return char == END_DELIMITER or char == SEP_DELIMITER or char == MAP_DELIMITER

def peekNextToken(tokens: list = []):
	"""
	Get the next token without removing it from the queue
	@param tokens: a list of tokens
	@return the next token
	"""

	if not tokens: raise FileFormatError(f"Expected token; none received")
	return tokens[0]

def getNextToken(tokens: list = [], expectedToken = None):
	"""
	Get the next token and remove it from the queue
	@param tokens: a list of tokens
	@param expectedToken: the expected token - an error is thrown if the next token
	does not equal the expected token
	@return the next token
	"""

	if not tokens: raise FileFormatError(f"Expected token; none received")
	token = tokens.pop(0)
	if expectedToken and token != expectedToken: raise FileFormatError(f"Expected '{expectedToken}'; received '{token}'")
	return token

def parseFloat(tokens):
	"""
	Get the next token as a float and remove it from the queue
	@param tokens: a list of tokens
	@return the next token as a float
	"""
	scaleFactorStr = getNextToken(tokens)
	try: scaleFactor = float(scaleFactorStr)
	except: raise FileFormatError(f"Expected float; received '{scaleFactorStr}'")
	return scaleFactor

def parseInt(tokens):
	"""
	Get the next token as an int and remove it from the queue
	@param tokens: a list of tokens
	@return the next token as an int
	"""
	scaleFactorStr = getNextToken(tokens)
	try: scaleFactor = int(scaleFactorStr)
	except: raise FileFormatError(f"Expected integer; received '{scaleFactorStr}'")
	return scaleFactor

def parseSymbol(tokens):
	"""
	Get the next token as a unit symbol and remove it from the queue
	@param tokens: a list of tokens
	@return the next token as a unit symbol
	"""
	sym = getNextToken(tokens)
	if not isValidSymbol(sym):
		raise FileFormatError(f"Expected alphabetical symbol; received '{sym}'")
	return sym

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