from UC_Errors import *

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
def topologicalSortVisit(units: dict, derivedUnit: str, toSort: list, sortedValues: list, visited: set):
	prefix, derivedUnit = stripPrefix(units, derivedUnit)
	if derivedUnit in visited: return
	visited[derivedUnit] = True

	if derivedUnit in units:
		for baseUnit in units[derivedUnit].baseUnits.keys():
			topologicalSortVisit(units, baseUnit, toSort, sortedValues, visited)

	if derivedUnit in toSort: sortedValues.insert(0, derivedUnit)

# Perform a topological sort over the conversions
def topologicalSort(units: dict, toSort: list):
	sortedValues = []
	visited = {}
	for derivedUnit in toSort:
		topologicalSortVisit(units, derivedUnit, toSort, sortedValues, visited)
	return sortedValues

# TODO: Implement this!
def validate(units, conversions, prefixes): pass