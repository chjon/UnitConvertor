from Unit import *

class FileFormatError(Exception): pass

L1_DELIMITER = ';'
L2_DELIMITER = ','
L3_DELIMITER = ' '

def loadConversions(filename):
	units = {}
	conversions = {}
	file = open(filename, 'r')
	lines = [ line[0:-1] for line in file.readlines() ]
	for line in lines:
		components = line.split(L1_DELIMITER)
		if len(components) == 1:
			# Create base unit
			sym = components[0]
			if not sym.isalpha():
				raise FileFormatError(f"Improper format: units must be alphabetical, received '{sym}'")
			units[sym] = Unit(sym)
		elif len(components) == 3:
			# Create derived unit
			sym = components[0]
			if not sym.isalpha():
				raise FileFormatError(f"Improper format: units must be alphabetical, received '{sym}'")
			val = float(components[1])
			baseUnits = {}
			for baseUnitStr in components[2].split(L2_DELIMITER):
				baseUnitComponents = baseUnitStr.split(L3_DELIMITER)
				if len(baseUnitComponents) != 2:
					raise FileFormatError(f"Improper format: expected 2 components, received '{baseUnitStr}'")
				baseUnit, exponent = baseUnitComponents
				if not baseUnit.isalpha():
					raise FileFormatError(f"Improper format: units must be alphabetical, received '{baseUnit}'")
				baseUnits[baseUnit] = int(exponent)
			units[sym] = Unit(sym, baseUnits)
			conversions[sym] = val
		else:
			print(components)
			raise FileFormatError(f"Improper format: expected 3 components, received {len(components)}")

	file.close()
	return units, conversions

def writeConversions(filename, units, conversions):
	file = open(filename, 'w')
	for sym, unit in units.items():
		if len(unit.baseUnits) == 0:
			file.write(f"{sym}\n")
		else:
			baseUnitStr = ''
			for baseUnitSym, exponent in unit.baseUnits.items():
				baseUnitStr += f"{baseUnitSym}{L3_DELIMITER}{exponent}{L2_DELIMITER}"
			file.write(f"{unit.sym}{L1_DELIMITER}{conversions[unit.sym]}{L1_DELIMITER}{baseUnitStr[0:-1]}\n")

	file.close()

class Convertor:
	# Topological sort implemented using DFS
	def topologicalSortVisit(self, derivedUnit: str, toSort: list, sortedValues: list, visited: set):
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
		
	def __init__(self, units = {}, conversions = {}):
		self.units = units
		self.conversions = conversions
	
	def convert(self, srcUnit, dstUnit):
		commonUnits = {}
		srcUnits = srcUnit.reduce()
		dstUnits = dstUnit.reduce()

		# Reduce all units to irreducible
		performedReduction = True
		scaleFactor = 1
		while performedReduction:
			# Factor out common units
			localCommonUnits = {}
			for srcUnitSym, srcUnitExp in srcUnits.items():
				if srcUnitSym in dstUnits:
					if not (srcUnitSym in localCommonUnits): localCommonUnits[srcUnitSym] = 0
					localCommonUnits[srcUnitSym] += min(srcUnitExp, dstUnits[srcUnitSym])
			for commonUnitSym, commonUnitExp in localCommonUnits.items():
				srcUnits[commonUnitSym] -= commonUnitExp
				dstUnits[commonUnitSym] -= commonUnitExp
				if srcUnits[commonUnitSym] == 0: srcUnits.pop(commonUnitSym)
				if dstUnits[commonUnitSym] == 0: dstUnits.pop(commonUnitSym)
				if not (commonUnitSym in commonUnits): commonUnits[commonUnitSym] = 0
				commonUnits[commonUnitSym] += localCommonUnits[commonUnitSym]

			# Perform a topological sort to find the next unit to reduce
			unitsToReduce = []
			for sym in srcUnits.keys(): unitsToReduce.append(sym)
			for sym in dstUnits.keys(): unitsToReduce.append(sym)
			unitsToReduce = self.topologicalSort(unitsToReduce)

			# Reduce units
			if len(unitsToReduce) == 0: break
			performedReduction = self.units[unitsToReduce[0]].isDerivedUnit()
			if performedReduction:
				reducedUnitSym = unitsToReduce[0]
				if reducedUnitSym in srcUnits:
					unitMap = srcUnits
					if reducedUnitSym in self.conversions:
						scaleFactor *= self.conversions[reducedUnitSym]**srcUnits[reducedUnitSym]
				else:
					unitMap = dstUnits
					if reducedUnitSym in self.conversions:
						scaleFactor /= self.conversions[reducedUnitSym]**dstUnits[reducedUnitSym]
				
				reducedUnitExp = unitMap[reducedUnitSym]
				unitMap.pop(reducedUnitSym)
				for sym, exp in self.units[reducedUnitSym].baseUnits.items():
					if not (sym in unitMap): unitMap[sym] = 0
					unitMap[sym] += reducedUnitExp * exp
		
		if len(srcUnits) > 0 or len(dstUnits) > 0:
			raise UnitError(f"Invalid conversion: {str(srcUnit)} to {str(dstUnit)}")

		return scaleFactor