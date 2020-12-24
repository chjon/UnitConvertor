import src.UC_Common as UC_Common

class Unit:
	def isBaseUnit(self):
		return self.sym != None and len(self.baseUnits) == 0

	def isDerivedUnit(self):
		return len(self.baseUnits) > 0

	def reduce(self):
		tmp1 = {}
		if self.sym != None:
			tmp1[self.sym] = 1
		else:
			for sym, exp in self.baseUnits.items():
				if sym in tmp1:
					tmp1[sym] += exp
				else:
					tmp1[sym] = exp
		
		tmp2 = {}
		for sym, exp in tmp1.items():
			if tmp1[sym] != 0:
				tmp2[sym] = exp
		
		return tmp2

	def __init__(self, sym: str = None, baseUnits: dict = {}):
		"""
		Unit constructor
		@param sym: The symbol for the unit
		@param baseUnits: The base units for the derived unit
		"""
		self.sym = sym
		self.baseUnits = baseUnits
		if sym == None and len(baseUnits) == 1 and [*baseUnits.values()][0] == 1:
			self.sym = [*baseUnits.keys()][0]
			self.baseUnits = {}

	def __str__(self, showDefinition = False):
		if (showDefinition and self.baseUnits) or not self.sym:
			outStr = ''
			for sym, exp in self.baseUnits.items():
				outStr += f"{sym}{'' if exp == 1 else f'^({exp})'} "
			return outStr.strip()
		return self.sym

	def __eq__(self, other):
		if other is None: return False
		if self.sym == other.sym: return True
		selfUnits = self.reduce()
		otherUnits = other.reduce()
		if len(selfUnits) != len(otherUnits): return False
		for	sym, exp in selfUnits.items():
			if (not sym in otherUnits) or (exp != otherUnits[sym]):
				return False
		return True

	def __ne__(self, other):
		return not (self == other)

	def __mul__(self, other):
		units = {}

		if self.sym:
			units[self.sym] = 1
		else:
			for unit, exp in self.baseUnits.items():
				units[unit] = exp
		
		if other.sym:
			if not (other.sym in units): units[other.sym] = 0
			units[other.sym] += 1
		else:
			for unit, exp in other.baseUnits.items():
				if not (unit in units): units[unit] = 0
				units[unit] += exp

		return Unit(baseUnits = Unit(baseUnits = units).reduce())

	def __truediv__(self, other):
		units = {}

		if self.sym:
			units[self.sym] = 1
		else:
			for unit, exp in self.baseUnits.items():
				units[unit] = exp

		if other.sym:
			if not (other.sym in units): units[other.sym] = 0
			units[other.sym] -= 1
		else:
			for unit, exp in other.baseUnits.items():
				if not (unit in units): units[unit] = 0
				units[unit] -= exp

		return Unit(baseUnits = Unit(baseUnits = units).reduce())

	def __pow__(self, power):
		if self.sym: return Unit(baseUnits = {self.sym: power})
		units = {}
		for sym, exp in self.baseUnits.items():
			units[sym] = exp * power
		return Unit(baseUnits = units)

	def clone(self):
		return Unit(self.sym, self.baseUnits.copy())

class Quantity:
	def __init__(self, value: float, unit: Unit):
		self.value = value
		self.unit  = unit
	
	def __str__(self):
		unitStr = str(self.unit)
		if unitStr: return f'{self.value} {unitStr}'
		return f'{self.value}'

	def __eq__(self, other):
		if other is None: return False
		return self.value == other.value and self.unit == other.unit

	def __ne__(self, other):
		return not (self == other)

	def __add__(self, other):
		if self.unit != other.unit: raise UC_Common.UnitError('Incompatible units')
		return Quantity(self.value + other.value, self.unit.clone())

	def __sub__(self, other):
		if self.unit != other.unit: raise UC_Common.UnitError('Incompatible units')
		return Quantity(self.value - other.value, self.unit.clone())

	def __mul__(self, other):
		return Quantity(self.value * other.value, self.unit * other.unit)
	
	def __truediv__(self, other):
		return Quantity(self.value / other.value, self.unit / other.unit)

	def __pow__(self, other):
		if other.unit.reduce(): raise UC_Common.UnitError(f"Cannot exponentiate with unit '{str(other.unit)}'")
		return Quantity(self.value ** other.value, self.unit ** other.value)
	
	def evaluate(self, convertor): return self