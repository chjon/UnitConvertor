import UC_FileParser

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
			if char == UC_FileParser.COMMENT_DELIMITER:
				if token: tokens.append(token)
				break
			# Handle whitespace
			if UC_FileParser.isWhitespace(char):
				if token:
					tokens.append(token)
					token = ''
			# Handle delimiters
			elif UC_FileParser.isDelimiter(char):
				if token:
					tokens.append(token)
					token = ''
				tokens.append(char)
			# Build token
			else: token += char

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
	validate(units, conversions, prefixes)

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