from decimal import Decimal
import src.UC_Unit as UC_Unit
import src.UC_Utils as UC_Utils
import src.UC_Common as UC_Common

def parseBaseUnitMap(tokens):
	"""
	Convert the next series of tokens into a map of units to exponents
	@param tokens: a list of tokens
	@return pairs of units and their corresponding exponents
	"""
	baseUnitMap = {}

	baseSym = UC_Utils.parseSymbol(tokens)
	if baseSym not in baseUnitMap: baseUnitMap[baseSym] = 0
	baseUnitMap[baseSym] += UC_Utils.parseInt(tokens)

	while UC_Utils.peekNextToken(tokens) == UC_Common.SEP_DELIMITER:
		UC_Utils.getNextToken(tokens)
		baseSym = UC_Utils.parseSymbol(tokens)
		if baseSym not in baseUnitMap: baseUnitMap[baseSym] = 0
		baseUnitMap[baseSym] += UC_Utils.parseInt(tokens)

	UC_Utils.getNextToken(tokens, UC_Common.END_DELIMITER)
	return baseUnitMap

def parseUnit(units, conversions, tokens, overwrite = False):
	"""
	Convert the next series of tokens into a unit
	@param units: a map of unit symbols to unit objects to be modified
	@param conversions: a map of unit symbols to scale factors to be modified
	@param tokens: a list of tokens
	"""
	baseUnitMap = {}

	# Handle base unit
	sym = UC_Utils.parseSymbol(tokens)
	if not overwrite and (sym in units):
		raise UC_Common.FileFormatError(f"Duplicate definition of unit '{sym}'")

	# Handle derived unit
	nextToken = UC_Utils.getNextToken(tokens)
	if nextToken == UC_Common.MAP_DELIMITER:
		scaleFactor = UC_Utils.parseFloat(tokens)
		UC_Utils.getNextToken(tokens, UC_Common.SEP_DELIMITER)
		baseUnitMap = parseBaseUnitMap(tokens)
		conversions[sym] = scaleFactor
	
	# Handle other tokens
	elif nextToken != UC_Common.END_DELIMITER: raise UC_Common.FileFormatError(f"Expected delimiter; received '{nextToken}'")

	# Create unit
	units[sym] = UC_Unit.Unit(sym, baseUnitMap)

def parsePrefixMapping(prefixes, tokens, base, overwrite = False):
	"""
	Convert the next series of tokens into a prefix-exponent pair
	@param prefixes: the prefix-exponent map to modify
	@param tokens: a list of tokens
	@param base: the base for the exponent
	"""
	prefix = UC_Utils.getNextToken(tokens)
	if not overwrite and (prefix in prefixes):
		raise UC_Common.FileFormatError(f"Duplicate definition of prefix '{prefix}'")
	prefixes[prefix] = (base, Decimal(UC_Utils.parseInt(tokens)))

def parsePrefix(prefixes, tokens, overwrite = False):
	"""
	Convert the next series of tokens into prefix-exponent pairs
	@param prefixes: the prefix-exponent map to modify
	@param tokens: a list of tokens
	"""
	base = UC_Utils.parseFloat(tokens)
	UC_Utils.getNextToken(tokens, UC_Common.MAP_DELIMITER)

	parsePrefixMapping(prefixes, tokens, base, overwrite)
	while UC_Utils.peekNextToken(tokens) == UC_Common.SEP_DELIMITER:
		UC_Utils.getNextToken(tokens)
		parsePrefixMapping(prefixes, tokens, base, overwrite)	
	UC_Utils.getNextToken(tokens, UC_Common.END_DELIMITER)

# Recursive descent parsing
def parseFile(tokens, units, conversions, prefixes, overwrite = False):
	"""
	Convert a list of tokens into maps of units, conversions, and prefixes
	@param tokens: a list of tokens
	@param units: a map of unit symbols to unit objects
	@param conversions: a map of derived unit symbols to scale factors
	@param prefixes: a map of prefixes to exponents
	"""
	while len(tokens):
		if UC_Utils.isValidSymbol(tokens[0]): parseUnit(units, conversions, tokens, overwrite)
		else: parsePrefix(prefixes, tokens, overwrite)

	# Return result of parsing
	return units, conversions, prefixes