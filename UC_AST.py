class AST_Add:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} + {str(self.right)})"

	def evaluate(self):
		return self.left.evaluate() + self.right.evaluate()

class AST_Sub:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} - {str(self.right)})"

	def evaluate(self):
		return self.left.evaluate() - self.right.evaluate()

class AST_Mul:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} * {str(self.right)})"

	def evaluate(self):
		return self.left.evaluate() * self.right.evaluate()

class AST_Div:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} / {str(self.right)})"

	def evaluate(self):
		return self.left.evaluate() / self.right.evaluate()

class AST_Exp:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"({str(self.left)} ^ {str(self.right)})"

	def evaluate(self):
		return self.left.evaluate() ** self.right.evaluate()

class AST_Eql:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return f"{str(self.left)} = {str(self.right)}"

	def evaluate(self):
		raise UC_Common.UnitError("Not implemented!")