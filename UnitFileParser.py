from Unit import *

class FileFormatError(Exception): pass

END_DELIMITER = ';'
SEP_DELIMITER = ','
MAP_DELIMITER = ':'
COMMENT_DELIMITER = '#'

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

def tokenize(lines: list = []):
	"""
	Generate a list of tokens from a list of strings
	@param lines: the list of strings from which to generate tokens
	@return a list of tokens
	"""
	tokens = []
	for line in lines:
		token = ''
		for char in line:
			# Stop processing line if there is a comment
			if char == COMMENT_DELIMITER:
				if token: tokens.append(token)
				break
			# Handle whitespace
			if isWhitespace(char):
				if token:
					tokens.append(token)
					token = ''
			# Handle delimiters
			elif isDelimiter(char):
				if token:
					tokens.append(token)
					token = ''
				tokens.append(char)
			# Build token
			else: token += char

	return tokens

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
		baseUnitMap = parseBaseUnitMap(tokens)
		conversions[sym] = scaleFactor
	
	# Handle other tokens
	elif nextToken != END_DELIMITER: raise FileFormatError(f"Expected delimiter; received '{nextToken}'")

	# Create unit
	units[sym] = Unit(sym, baseUnitMap)

def parsePrefixMapping(prefixes, tokens):
	"""
	Convert the next series of tokens into a prefix-exponent pair
	@param prefixes: the prefix-exponent map to modify
	@param tokens: a list of tokens
	"""
	prefix = getNextToken(tokens)
	if prefix in prefixes: raise FileFormatError(f"Duplicate definition of prefix '{prefix}'")
	prefixes[prefix] = parseInt(tokens)

def parsePrefix(prefixes, tokens):
	"""
	Convert the next series of tokens into prefix-exponent pairs
	@param prefixes: the prefix-exponent map to modify
	@param tokens: a list of tokens
	"""
	base = parseFloat(tokens)
	if base not in prefixes: prefixes[base] = {}

	getNextToken(tokens, MAP_DELIMITER)
	parsePrefixMapping(prefixes[base], tokens)
	while peekNextToken(tokens) == SEP_DELIMITER:
		getNextToken(tokens)
		parsePrefixMapping(prefixes[base], tokens)	
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
	# Parse tokens to generate output
	units = {}
	conversions = {}
	prefixes = {}
	while len(tokens):
		if isValidSymbol(tokens[0]):
			parseUnit(units, conversions, tokens)
		else:
			parsePrefix(prefixes, tokens)
	
	# Check that all dependencies exist and check for an acyclic dependency graph
	validate(units, conversions, prefixes)

	# Return result of parsing
	return units, conversions, prefixes

def loadFile(filename):
	"""
	Read a file and generate maps of units, conversions, and prefixes
	@param filename: the name of the file to load
	@return units: a map of unit symbols to unit objects
	@return conversions: a map of derived unit symbols to scale factors
	@return prefixes: a map of prefixes to exponents
	"""
	# Generate a list of tokens from the file
	file = open(filename, 'r')
	tokens = tokenize(file.readlines())
	file.close()

	return parseFile(tokens)

def writeFile(filename, units, conversions, prefixes):
	file = open(filename, 'w')

	# Write exponents
	for base, prefixMapping in prefixes.items():
		prefixStr = ''
		for prefix, exp in prefixMapping.items():
			prefixStr += f"{prefix}{L3_DELIMITER}{exp}{L2_DELIMITER}"
		file.write(f"{base}{L1_DELIMITER}{prefixStr[0:-1]}\n")		

	for sym, unit in units.items():
		if len(unit.baseUnits) == 0:
			# Write base units
			file.write(f"{sym}\n")
		else:
			# Write derived units
			baseUnitStr = ''
			for baseUnitSym, exponent in unit.baseUnits.items():
				baseUnitStr += f"{baseUnitSym}{L3_DELIMITER}{exponent}{L2_DELIMITER}"
			file.write(f"{unit.sym}{L1_DELIMITER}{conversions[unit.sym]}{L1_DELIMITER}{baseUnitStr[0:-1]}\n")

	file.close()

def parseUnitStr(toParse):
	unitMap = {}
	toParse = toParse.strip()
	components = toParse.split(' ')
	for component in components:
		vals = component.split('^')
		sym = vals[0]
		if not (sym in unitMap): unitMap[sym] = 0
		if len(vals) == 1:
			unitMap[sym] += 1
		elif len(vals) == 2:
			unitMap[sym] += int(vals[1])
		else:
			raise UnitError(f"Invalid unit: '{component}'")
	
	return unitMap