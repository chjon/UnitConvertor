from decimal import Decimal
import src.UC_Unit as UC_Unit
import src.UC_Common as UC_Common
import src.UC_Utils as UC_Utils

def removeCancelledUnits(unitMap):
	toRemove = []
	for sym, exp in unitMap.items():
		if exp == 0: toRemove.append(sym)
	for sym in toRemove: unitMap.pop(sym)

class Convertor:
	def __init__(self, units = {}, conversions = {}, prefixes = {}):
		self.units = units
		self.conversions = conversions
		self.prefixes = prefixes

	def getPrefixScaleFactor(self, prefix):
		base, exp = self.prefixes[prefix]
		return (base)**(exp)

	def getUnitDefinitionStr(self, string):
		prefix, sym = UC_Utils.stripPrefix(self.units, string)
		if prefix:
			scaleFactor = self.getPrefixScaleFactor(prefix)
			return f"1 {string} = prefix: '{prefix}', unit: '{sym}' = {scaleFactor} {sym}"
		else:
			quantity = self.conversions[sym] if sym in self.conversions else 1
			return f"1 {string} = {quantity} {self.units[sym].__str__(True)}"
	
	def getPrefixDefinitionStr(self, string):
		base, exp = self.prefixes[string]
		return f"{string} = ({base})^({exp}) = {base**exp}"

	def processPrefixes(self, units):
		scaleFactor = Decimal(1)
		unitsToUpdate = {}
		for prefixedSym, exp in units.items():
			# Find prefix and base unit
			prefix, baseUnit = UC_Utils.stripPrefix(self.units, prefixedSym)
			if len(prefix) == 0: continue
			if prefix not in self.prefixes: raise UC_Common.UnitError(f"Unknown unit: '{prefixedSym}'")
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
		removeCancelledUnits(unitMap)

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
		
		# Remove cancelled units
		removeCancelledUnits(srcUnits)
		removeCancelledUnits(dstUnits)

		# Check for conversion error
		if len(srcUnits) > 0 or len(dstUnits) > 0:
			raise UC_Common.UnitError(f"Invalid conversion: {str(srcUnit)} to {str(dstUnit)}")

		return scaleFactor
	
	def addUnit(self, sym, scaleFactor, unit):
		if sym in self.units:
			quantity = self.conversions[sym] if sym in self.conversions else 1
			raise UC_Common.UnitError(f"Unit '{sym}' already exists: {self.getUnitDefinitionStr(sym)}")
		else:
			# Try adding unit
			units = self.units.copy()
			units[sym] = UC_Unit.Unit(sym, unit.reduce())
			conversions = self.conversions.copy()
			conversions[sym] = scaleFactor
			
			# Check that all dependencies exist and check for an acyclic dependency graph
			UC_Utils.validate(units, conversions, self.prefixes)
			self.units = units
			self.conversions = conversions
	
	def addPrefix(self, sym, base, exp):
		if sym in self.prefixes:
			base, exp = self.prefixes[sym]
			raise UC_Common.UnitError(f"Prefix '{sym}' already exists: '{sym}' = {base}^{exp} = {base**exp}")
		else:
			# Try adding prefix
			prefixes = self.prefixes.copy()
			prefixes[sym] = (base, exp)

			# Check that all dependencies exist and check for an acyclic dependency graph
			UC_Utils.validate(self.units, self.conversions, prefixes)
			self.prefixes = prefixes

	def delUnit(self, symToDelete):
		if symToDelete in self.units:
			unitsToDelete = {symToDelete}

			# Find all units to delete
			foundDependentUnit = True
			while foundDependentUnit:
				foundDependentUnit = False
				for sym, unit in self.units.items():
					if sym in unitsToDelete: continue
					for dependencySym in unit.baseUnits.keys():
						prefix, baseSym = UC_Utils.stripPrefix(self.units, dependencySym)
						if baseSym in unitsToDelete:
							unitsToDelete.add(sym)
							foundDependentUnit = True
							break

			# Delete all units which need to be deleted
			for sym in unitsToDelete:
				del self.units[sym]
				if sym in self.conversions: del self.conversions[sym]
			
			return unitsToDelete
		else:
			try: unitDefStr = self.getUnitDefinitionStr(symToDelete)
			except: raise UC_Common.UnitError(f"Cannot delete '{symToDelete}' - unit does not exist")
			raise UC_Common.UnitError(f"Cannot delete '{symToDelete}' - unit contains a prefix: {unitDefStr}")
	
	def delPrefix(self, symToDelete):
		if symToDelete in self.prefixes:
			unitsToDelete = set()

			# Find all units to delete
			foundDependentUnit = True
			while foundDependentUnit:
				foundDependentUnit = False
				for sym, unit in self.units.items():
					if sym in unitsToDelete: continue
					for dependencySym in unit.baseUnits.keys():
						prefix, baseSym = UC_Utils.stripPrefix(self.units, dependencySym)
						if prefix == symToDelete or baseSym in unitsToDelete:
							unitsToDelete.add(sym)
							foundDependentUnit = True
							break

			# Delete all units which need to be deleted
			for sym in unitsToDelete:
				del self.units[sym]
				if sym in self.conversions: del self.conversions[sym]
			
			# Delete from prefix map
			del self.prefixes[symToDelete]

			return unitsToDelete
		else: raise UC_Common.UnitError(f"Cannot delete '{symToDelete}' - prefix does not exist") 