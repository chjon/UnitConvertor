from Unit import *

class FileFormatError(Exception): pass

END_DELIMITER = ';'
SEP_DELIMITER = ','
MAP_DELIMITER = ':'
COMMENT_DELIMITER = '#'

# Determine whether a string is a valid unit symbol
def isValidSymbol(sym):
	for char in sym:
		if (not char.isalpha()) and (char != '_'): return False
	return True

# Determine whether a character is whitespace
def isWhitespace(char):
	return char == ' ' or char == '\t' or char == '\r' or char == '\n'

# Determine whether a character is a delimiter
def isDelimiter(char):
	return char == END_DELIMITER or char == SEP_DELIMITER or char == MAP_DELIMITER

# Generate tokens from lines
def tokenize(lines):
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

def peekNextToken(tokens):
	if not tokens: raise FileFormatError(f"Expected token; none received")
	return tokens[0]

def getNextToken(tokens, expectedToken = None):
	if not tokens: raise FileFormatError(f"Expected token; none received")
	token = tokens.pop(0)
	if expectedToken and token != expectedToken: raise FileFormatError(f"Expected '{expectedToken}'; received '{token}'")
	return token

def parseFloat(tokens):
	scaleFactorStr = getNextToken(tokens)
	try: scaleFactor = float(scaleFactorStr)
	except: raise FileFormatError(f"Expected float; received '{scaleFactorStr}'")
	return scaleFactor

def parseInt(tokens):
	scaleFactor = getNextToken(tokens)
	try: scaleFactor = int(scaleFactor)
	except: raise FileFormatError(f"Expected integer; received '{scaleFactor}'")
	return scaleFactor

def parseSymbol(tokens):
	sym = getNextToken(tokens)
	if not isValidSymbol(sym):
		raise FileFormatError(f"Expected alphabetical symbol; received '{sym}'")
	return sym

def parseBaseUnitMap(tokens):
	scaleFactor = parseFloat(tokens)
	baseUnitMap = {}

	while peekNextToken(tokens) == SEP_DELIMITER:
		getNextToken(tokens)
		baseSym = parseSymbol(tokens)
		if baseSym not in baseUnitMap: baseUnitMap[baseSym] = 0
		baseUnitMap[baseSym] += parseInt(tokens)

	getNextToken(tokens, END_DELIMITER)
	return scaleFactor, baseUnitMap

def parseUnit(units, conversions, tokens):
	baseUnitMap = {}

	# Handle base unit
	sym = parseSymbol(tokens)
	if sym in units: raise FileFormatError(f"Duplicate definition of unit '{sym}'")

	# Handle derived unit
	nextToken = getNextToken(tokens)
	if nextToken == MAP_DELIMITER:
		scaleFactor, baseUnitMap = parseBaseUnitMap(tokens)
		conversions[sym] = scaleFactor
	
	# Handle other tokens
	elif nextToken != END_DELIMITER: raise FileFormatError(f"Expected delimiter; received '{nextToken}'")

	# Create unit
	units[sym] = Unit(sym, baseUnitMap)

def parsePrefixMapping(prefixes, tokens):
	prefix = getNextToken(tokens)
	if prefix in prefixes: raise FileFormatError(f"Duplicate definition of prefix '{prefix}'")
	prefixes[prefix] = parseInt(tokens)

def parsePrefix(prefixes, tokens):
	base = parseFloat(tokens)
	if base not in prefixes: prefixes[base] = {}

	getNextToken(tokens, MAP_DELIMITER)
	parsePrefixMapping(prefixes[base], tokens)
	while peekNextToken(tokens) == SEP_DELIMITER:
		getNextToken(tokens)
		parsePrefixMapping(prefixes[base], tokens)	
	getNextToken(tokens, END_DELIMITER)

# Recursive descent parsing
def loadFile(filename):
	# Preprocess file to generate a list of tokens
	file = open(filename, 'r')
	tokens = tokenize(file.readlines())
	file.close()

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