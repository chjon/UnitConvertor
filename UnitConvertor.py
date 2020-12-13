from Unit import *

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
		self.topologicalSort()
