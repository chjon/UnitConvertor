import UC_Common

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
	return (
		char == UC_Common.END_DELIMITER or
		char == UC_Common.SEP_DELIMITER or
		char == UC_Common.MAP_DELIMITER
	)

def stripPrefix(units, string):
	# Find longest matching suffix
	longestSuffix = ""
	for sym in units.keys():
		if string.endswith(sym) and len(sym) > len(longestSuffix):
			longestSuffix = sym
			if len(longestSuffix) == len(string): break
	
	if len(longestSuffix) == 0: raise UnitError(f"Invalid unit: received '{string}'")
	return string[0:len(string)-len(longestSuffix)], longestSuffix

# Topological sort implemented using DFS
def topologicalSortVisit(units: dict, unit: str, sortedValues: list, permVisited: set, tempVisited: set):
	if unit in permVisited: return
	if unit in tempVisited: raise UnitError(f"Dependency cycle detected for unit '{unit}'")
	tempVisited[unit] = True

	for baseUnit in units[unit].baseUnits.keys():
		prefix, sym = stripPrefix(units, baseUnit)
		topologicalSortVisit(units, sym, sortedValues, permVisited, tempVisited)

	del tempVisited[unit]
	permVisited[unit] = True

	sortedValues.insert(0, unit)

# Perform a topological sort over the conversions
def topologicalSort(units: dict, toSort: list = None):
	sortedValues = []
	permVisited = {}
	tempVisited = {}

	# Sort the entire graph
	for unit in ([*units.keys()] if toSort == None else toSort):
		prefix, sym = stripPrefix(units, unit)
		if sym not in permVisited:
			topologicalSortVisit(units, sym, sortedValues, permVisited, tempVisited)
	if toSort == None: return sortedValues

	# Generate a filter from the desired values
	desiredValues = {}
	for unit in toSort:
		prefix, sym = stripPrefix(units, unit)
		if sym not in desiredValues: desiredValues[sym] = []
		desiredValues[sym].append(prefix)

	# Filter the topological sort to the desired values
	filteredValues = []
	for unit in sortedValues:
		if unit in desiredValues:
			filteredValues.extend([f"{prefix}{unit}" for prefix in desiredValues[unit]])

	return filteredValues

def validate(units, conversions, prefixes):
	# Ensure that all units and dependencies are defined
	for unit in units.values():
		for baseUnit in unit.baseUnits.keys():
			prefix, sym = stripPrefix(units, baseUnit)
			if sym not in units: raise UnitError(f"Invalid unit symbol: '{sym}'")
			if prefix and (prefix not in prefixes): raise UnitError(f"Invalid prefix: '{prefix}'")
	
	# Ensure that all conversion units are defined
	for unit in conversions.keys():
		if unit not in units: raise UnitError(f"No unit defined for conversion from: '{unit}'")
	
	# Ensure that there are no cycles in the dependency graph
	topologicalSort(units)