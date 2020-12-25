import src.UC_Common as UC_Common
import src.UC_Unit as UC_Unit

class AST_Add:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} + {str(self.right)})"

	def evaluate(self, convertor):
		leftResult = self.left.evaluate(convertor)
		rightResult = self.right.evaluate(convertor)
		if leftResult.unit != rightResult.unit:
			leftResult.value *= convertor.convert(leftResult.unit, rightResult.unit)
			leftResult.unit = rightResult.unit
		return leftResult + rightResult

class AST_Sub:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} - {str(self.right)})"

	def evaluate(self, convertor):
		leftResult = self.left.evaluate(convertor)
		rightResult = self.right.evaluate(convertor)
		leftResult.value *= convertor.convert(leftResult.unit, rightResult.unit)
		leftResult.unit = rightResult.unit
		return leftResult - rightResult

class AST_Mul:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} * {str(self.right)})"

	def evaluate(self, convertor):
		return self.left.evaluate(convertor) * self.right.evaluate(convertor)

class AST_Div:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} / {str(self.right)})"

	def evaluate(self, convertor):
		return self.left.evaluate(convertor) / self.right.evaluate(convertor)

class AST_Exp:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"(({str(self.left)})^({str(self.right)}))"

	def evaluate(self, convertor):
		exp = self.right.evaluate(convertor)
		try:
			scaleFactor = convertor.convert(exp.unit, UC_Unit.Unit())
			exp.value *= scaleFactor
			exp.unit = UC_Unit.Unit()
		except: pass
		return self.left.evaluate(convertor) ** exp

class AST_Eql:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} : {str(self.right)})"

	def evaluate(self, convertor):
		leftResult = self.left.evaluate(convertor)
		rightResult = self.right.evaluate(convertor)
		leftResult.value *= convertor.convert(leftResult.unit, rightResult.unit)
		leftResult.value /= rightResult.value
		leftResult.unit = rightResult.unit
		return leftResult