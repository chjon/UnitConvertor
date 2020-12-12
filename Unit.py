class UnitError(Exception): pass

class Unit:
	def reduce(self):
		tmp1 = {}
		for sym, exp in self.units.items():
			if sym in tmp1:
				tmp1[sym] += exp
			else:
				tmp1[sym] = exp
		
		tmp2 = {}
		for sym, exp in tmp1.items():
			if tmp1[sym] != 0:
				tmp2[sym] = exp
		
		return tmp2

	def __init__(self, units: dict = {}):
		self.units = units

	def __str__(self):
		outStr = ''
		for sym, exp in self.units.items():
			outStr += f"{sym}{'' if exp == 1 else f'^({exp})'} "
		
		return outStr.strip()

	def __eq__(self, other):
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
		units = self.units.copy()
		for unit, exp in other.units.items():
			if unit in units:
				units[unit] += exp
			else:
				units[unit] = exp

		return Unit(units)

	def __truediv__(self, other):
		units = self.units.copy()
		for unit, exp in other.units.items():
			if unit in units:
				units[unit] -= exp
			else:
				units[unit] = -exp

		return Unit(units)

	def clone(self):
		return Unit(self.units.copy())

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

class Conversion:
	def __init__(self, derivedUnit: Unit, value: float, baseUnits: dict):
		self.value = value
		self.unit  = unit