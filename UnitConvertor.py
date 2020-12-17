from Unit import *

class FileFormatError(Exception): pass

L1_DELIMITER = ';'
L2_DELIMITER = ','
L3_DELIMITER = ' '
COMMENT_DELIMITER = '#'

def stripPrefix(units, prefixedSym):
	# Find longest matching suffix
	longestSuffix = ""
	for sym in units.keys():
		if prefixedSym.endswith(sym) and len(sym) > len(longestSuffix):
			longestSuffix = sym
			if len(longestSuffix) == len(prefixedSym): break
	
	if len(longestSuffix) == 0: raise UnitError(f"Invalid unit: received '{prefixedSym}'")
	return prefixedSym[0:len(prefixedSym)-len(longestSuffix)], longestSuffix

def removeComment(s):
	if COMMENT_DELIMITER not in s: return s
	s = s.strip()
	s = s[0:s.index(COMMENT_DELIMITER)]
	return s

def loadBaseUnit(units, components):
	# Create base unit
	sym = components[0].strip()
	if not sym.isalpha():
		raise FileFormatError(f"Improper format: units must be alphabetical, received '{sym}'")
	units[sym] = Unit(sym)

def loadPrefix(prefixes, components):
	# Create prefix mapping
	base = int(components[0].strip())
	prefixMapping = {}
	baseExpPairs = components[1].split(L2_DELIMITER)
	for baseExpPair in baseExpPairs:
		prefix, exp = baseExpPair.strip().split(L3_DELIMITER, 1)
		prefix = prefix.strip()
		exp = exp.strip()
		prefixMapping[prefix] = int(exp)
	prefixes[base] = prefixMapping

def loadDerivedUnit(units, conversions, components):
	# Create derived unit
	sym = components[0].strip()
	if not sym.isalpha():
		raise FileFormatError(f"Improper format: units must be alphabetical, received '{sym}'")
	val = float(components[1])
	baseUnits = {}
	for baseUnitStr in components[2].split(L2_DELIMITER):
		baseUnitComponents = baseUnitStr.strip().split(L3_DELIMITER, 1)
		if len(baseUnitComponents) != 2:
			raise FileFormatError(f"Improper format: expected 2 components, received '{baseUnitStr}'")
		baseUnit = baseUnitComponents[0].strip()
		exponent = baseUnitComponents[1].strip()
		if not baseUnit.isalpha():
			raise FileFormatError(f"Improper format: units must be alphabetical, received '{baseUnit}'")
		try: stripPrefix(units, baseUnit)
		except: raise FileFormatError(f"Improper format: '{sym}' requires definition of '{baseUnit}'")
		baseUnits[baseUnit] = int(exponent)
	if sym in units:
		raise FileFormatError(f"Multiple definition of unit '{sym}'")
	units[sym] = Unit(sym, baseUnits)
	conversions[sym] = val

def loadConversions(filename):
	units = {}
	conversions = {}
	prefixes = {}
	file = open(filename, 'r')
	lines = [ line[0:-1] for line in file.readlines() ]
	for line in lines:
		# Strip comments
		line = removeComment(line)
		if len(line) == 0: continue

		# Parse line
		components = line.split(L1_DELIMITER)
		if len(components) == 1: loadBaseUnit(units, components)
		elif len(components) == 2: loadPrefix(prefixes, components)
		elif len(components) == 3: loadDerivedUnit(units, conversions, components)
		else: raise FileFormatError(f"Improper format: expected 3 components, received {len(components)}")

	file.close()
	return units, conversions, prefixes

def writeConversions(filename, units, conversions, prefixes):
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

class Convertor:
	# Topological sort implemented using DFS
	def topologicalSortVisit(self, derivedUnit: str, toSort: list, sortedValues: list, visited: set):
		prefix, derivedUnit = stripPrefix(self.units, derivedUnit)
		if derivedUnit in visited: return
		visited[derivedUnit] = True

		if derivedUnit in self.conversions.keys():
			for baseUnit in self.units[derivedUnit].baseUnits.keys():
				self.topologicalSortVisit(baseUnit, toSort, sortedValues, visited)

		if derivedUnit in toSort: sortedValues.insert(0, derivedUnit)

	# Perform a topological sort over the conversions
	def topologicalSort(self, toSort: list):
		sortedValues = []
		visited = {}
		for derivedUnit in toSort:
			self.topologicalSortVisit(derivedUnit, toSort, sortedValues, visited)
		return sortedValues

	def __init__(self, units = {}, conversions = {}, prefixes = {}):
		self.units = units
		self.conversions = conversions
		self.prefixes = prefixes

	def getPrefixScaleFactor(self, prefix):
		for base, candidatePrefixMapping in self.prefixes.items():
			for candidatePrefix, exp in candidatePrefixMapping.items():
				if prefix == candidatePrefix: return (base)**(exp)

	def processPrefixes(self, units):
		scaleFactor = 1
		unitsToUpdate = {}
		for prefixedSym, exp in units.items():
			# Find prefix and base unit
			prefix, baseUnit = stripPrefix(self.units, prefixedSym)
			if len(prefix) == 0: continue
			unitsToUpdate[prefixedSym] = baseUnit

			# Calculate scale factor
			scaleFactor *= self.getPrefixScaleFactor(prefix)**(exp)
			
		# Update unit map
		for fromSym, toSym in unitsToUpdate.items():
			if not (toSym in units): units[toSym] = 0
			units[toSym] += units[fromSym]
			units.pop(fromSym)

		return scaleFactor

	def factorUnits(self, srcUnits, dstUnits):
		# Find common factors
		commonUnits = {}
		for srcUnitSym, srcUnitExp in srcUnits.items():
			if srcUnitSym in dstUnits:
				if not (srcUnitSym in commonUnits): commonUnits[srcUnitSym] = 0
				commonUnits[srcUnitSym] += min(srcUnitExp, dstUnits[srcUnitSym])

		# Factor out common factors
		for commonUnitSym, commonUnitExp in commonUnits.items():
			srcUnits[commonUnitSym] -= commonUnitExp
			dstUnits[commonUnitSym] -= commonUnitExp
			if srcUnits[commonUnitSym] == 0: srcUnits.pop(commonUnitSym)
			if dstUnits[commonUnitSym] == 0: dstUnits.pop(commonUnitSym)
	
	def reduceUnit(self, reducedUnitSym, unitMap):
		# Calculate scale factor
		scaleFactor = 1
		if reducedUnitSym in self.conversions:
			tmp = (self.conversions[reducedUnitSym])**(unitMap[reducedUnitSym])
			scaleFactor *= tmp

		# Reduce unit
		reducedUnitExp = unitMap.pop(reducedUnitSym)
		for sym, exp in self.units[reducedUnitSym].baseUnits.items():
			if not (sym in unitMap): unitMap[sym] = 0
			unitMap[sym] += reducedUnitExp * exp
		
		# Remove cancelled units
		toRemove = []
		for sym, exp in unitMap.items():
			if exp == 0: toRemove.append(sym)
		for sym in toRemove: unitMap.pop(sym)

		return scaleFactor

	def convert(self, srcUnit, dstUnit):
		srcUnits = srcUnit.reduce()
		dstUnits = dstUnit.reduce()

		# Reduce all units to irreducible
		performedReduction = True
		scaleFactor = 1
		while performedReduction:
			# Simplify units using SI prefixes
			scaleFactor *= self.processPrefixes(srcUnits)
			scaleFactor /= self.processPrefixes(dstUnits)

			# Factor out common units and perform a topological sort to find the next unit to reduce
			self.factorUnits(srcUnits, dstUnits)
			unitsToReduce = self.topologicalSort([*srcUnits.keys()] + [*dstUnits.keys()])

			# Reduce units
			if len(unitsToReduce) == 0: break
			performedReduction = self.units[unitsToReduce[0]].isDerivedUnit()
			if performedReduction:
				if unitsToReduce[0] in srcUnits: scaleFactor *= self.reduceUnit(unitsToReduce[0], srcUnits)
				else: scaleFactor /= self.reduceUnit(unitsToReduce[0], dstUnits)
		
		# Check for conversion error
		if len(srcUnits) > 0 or len(dstUnits) > 0:
			raise UnitError(f"Invalid conversion: {str(srcUnit)} to {str(dstUnit)}")

		return scaleFactor