from UC_Unit import *
from UC_Common import *
import UC_Utils

class Convertor:
	def __init__(self, units = {}, conversions = {}, prefixes = {}):
		self.units = units
		self.conversions = conversions
		self.prefixes = prefixes

	def getPrefixScaleFactor(self, prefix):
		base, exp = self.prefixes[prefix]
		return (base)**(exp)

	def processPrefixes(self, units):
		scaleFactor = 1
		unitsToUpdate = {}
		for prefixedSym, exp in units.items():
			# Find prefix and base unit
			prefix, baseUnit = UC_Utils.stripPrefix(self.units, prefixedSym)
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
			unitsToReduce = UC_Utils.topologicalSort(self.units, [*srcUnits.keys()] + [*dstUnits.keys()])

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