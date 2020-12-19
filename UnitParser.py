from Unit import UnitError

# Recursive descent parsing
def parseFile(filename):
	# Preprocess file to generate a list of tokens
	file = open(filename, 'r')
	tokens = tokenize(file.readline())
	file.close()

	# Parse tokens to generate output
	units = {}
	conversions = {}
	prefixes = {}
	while len(tokens):
		if isValidSymbol(tokens[0]):
			parseUnit(units, conversions, tokens)
		else
			parsePrefix(prefixes, tokens)
	
	# Check that all dependencies exist and check for an acyclic dependency graph
	validate(units, conversions, prefixes)

	# Return result of parsing
	return units, conversions, prefixes

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