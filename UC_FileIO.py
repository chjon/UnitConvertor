import UC_Common
import UC_FileParser
import UC_FileSerializer
import UC_Utils

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
			if char == UC_Common.COMMENT_DELIMITER:
				if token: tokens.append(token)
				break
			# Handle whitespace
			if UC_Utils.isWhitespace(char):
				if token:
					tokens.append(token)
					token = ''
			# Handle delimiters
			elif UC_Utils.isDelimiter(char):
				if token:
					tokens.append(token)
					token = ''
				tokens.append(char)
			# Build token
			else: token += char
		
		if token: tokens.append(token)

	return tokens

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

	# Parse tokens to generate maps
	units, conversions, prefixes = UC_FileParser.parseFile(tokens)

	# Check that all dependencies exist and check for an acyclic dependency graph
	UC_Utils.validate(units, conversions, prefixes)

	return units, conversions, prefixes

def writeFile(filename, units, conversions, prefixes):
	"""
	Write a file representined the unit conversion and prefix maps
	@param filename: the name of the file to write
	@param units: a map of unit symbols to unit objects
	@param conversions: a map of derived unit symbols to scale factors
	@param prefixes: a map of prefixes to exponents
	"""
	# Get lines to write
	lines = []
	lines.extend(UC_FileSerializer.serializePrefixes(prefixes))
	lines.extend(UC_FileSerializer.serializeUnitConversions(units, conversions))

	# Write lines
	file = open(filename, 'w')
	for line in lines:
		file.write(f"{line}\r\n")	
	file.close()