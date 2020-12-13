class UnitError(Exception): pass

class Unit:
	def isBaseUnit(self):
		return sym != None and len(baseUnits) == 0

	def isDerivedUnit(self):
		return sym != None and len(baseUnits) > 0

	def reduce(self):
		tmp1 = {}
		if self.isBaseUnit(): tmp1[self.sym] = 1
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

	def __str__(self):
		if self.sym: return self.sym
		outStr = ''
		for sym, exp in self.baseUnits.items():
			outStr += f"{sym}{'' if exp == 1 else f'^({exp})'} "
		return outStr.strip()

	def __eq__(self, other):
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

	def clone(self):
		return Unit(self.sym, self.baseUnits.copy())

class Quantity:
	def __init__(self, value: float, unit: Unit):
		self.value = value
		self.unit  = unit
	
	def __str__(self):
		return f'{self.value} {str(self.unit)}'

	def __eq__(self, other):
		return self.value == other.value and self.unit == other.unit

	def __ne__(self, other):
		return not (self == other)

	def __add__(self, other):
		if self.unit != other.unit: raise UnitError('Incompatible units')
		return Quantity(self.value + other.value, self.unit.clone())

	def __sub__(self, other):
		if self.unit != other.unit: raise UnitError('Incompatible units')
		return Quantity(self.value - other.value, self.unit.clone())

	def __mul__(self, other):
		return Quantity(self.value * other.value, self.unit * other.unit)
	
	def __truediv__(self, other):
		return Quantity(self.value / other.value, self.unit / other.unit)