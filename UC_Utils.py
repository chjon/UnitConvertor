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
def topologicalSortVisit(units, derivedUnit: str, toSort: list, sortedValues: list, visited: set):
	prefix, derivedUnit = stripPrefix(units, derivedUnit)
	if derivedUnit in visited: return
	visited[derivedUnit] = True

	if derivedUnit in units:
		for baseUnit in self.units[derivedUnit].baseUnits.keys():
			self.topologicalSortVisit(baseUnit, toSort, sortedValues, visited)

	if derivedUnit in toSort: sortedValues.insert(0, derivedUnit)

# Perform a topological sort over the conversions
def topologicalSort(toSort: list):
	sortedValues = []
	visited = {}
	for derivedUnit in toSort:
		topologicalSortVisit(derivedUnit, toSort, sortedValues, visited)
	return sortedValues