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
	def topologicalSortVisit(self, derivedUnit: str, visited: set):
		if derivedUnit in visited: return
		visited[derivedUnit] = True

		if derivedUnit in self.conversions.keys():
			for baseUnit in self.units[derivedUnit].baseUnits.keys():
				self.topologicalSortVisit(baseUnit, visited)

		self.topology.insert(0, derivedUnit)

	# Perform a topological sort over the conversions
	def topologicalSort(self):
		self.topology = []
		visited = {}

		for derivedUnit in self.conversions.keys():
			self.topologicalSortVisit(derivedUnit, visited)
		
	def __init__(self, units = {}, conversions = {}):
		self.units = units
		self.conversions = conversions
		self.topology = []
		self.topologicalSort()