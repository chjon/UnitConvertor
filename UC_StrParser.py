from UC_Common import *
from UC_Utils import *
import UC_Unit
import UC_AST

def tokenizeFloat(token, tokens, char, parseFloatState):
	"""
	Incrementally parse floats as a single token
	Floats are a special case of tokenization because '+' and '-' are valid components
	@param token: the token that has been built so far
	@param tokens: the list of tokens to modify
	@param char: the next character
	@param parseFloatState: the current state of the state machine
	@return token: the modified token after advancing one character
	@return parseFloatState: the next state machine state to move to 
	"""
	if parseFloatState == 0:
		if char.isnumeric():
			parseFloatState = 1
			if token: tokens.append(token)
			token = ""
		elif char == '.': parseFloatState = 2
	elif parseFloatState == 1:
		if char == '.': parseFloatState = 2
		elif char == 'e': parseFloatState = 3
		elif not char.isnumeric():
			parseFloatState = 0
			if token: tokens.append(token)
			token = ""
	elif parseFloatState == 2:
		if char == 'e': parseFloatState = 3
		elif not char.isnumeric():
			parseFloatState = 0
			if token: tokens.append(token)
			token = ""
	elif parseFloatState == 3:
		if char == '+' or char == '-' or char.isnumeric(): parseFloatState = 4
		else:
			parseFloatState = 0
			if token: tokens.append(token[:-1])
			token = token[-1]
	elif parseFloatState == 4:
		if not char.isnumeric():
			tmp = []
			if token[-1] == '+' or token[-1] == '-':
				tmp.append(token[-1])
				token = token[:-1]
			if token[-1] == 'e':
				tmp.append(token[-1])
				token = token[:-1]
			if token: tokens.append(token)
			token = ""
			while tmp: tokens.append(tmp.pop())
			parseFloatState = 0
	
	return token, parseFloatState

def tokenize(line):
	"""
	Convert a string into a list of tokens
	@param line: the string to convert
	@return a list of tokens
	"""
	tokens = []
	token = ''
	
	# Identify tokens
	parseFloatState = 0
	for char in line:
		# Handle float-like tokens
		token, parseFloatState = tokenizeFloat(token, tokens, char, parseFloatState)

		# Handle non-float tokens
		if parseFloatState: token += char
		elif isWhitespace(char):
			if token: tokens.append(token)
			token = ""
		elif isSpecialChar(char):
			if token: tokens.append(token)
			token = ""
			tokens.append(char)
		else: token += char
	
	token, parseFloatState = tokenizeFloat(token, tokens, "", parseFloatState)
	if token: tokens.append(token)
	return tokens

def convertToRPN(tokens):
	"""
	Convert infix notation into Reverse Polish Notation for building the AST
	@param tokens: the list of tokens in infix notation order
	@post: this implementation uses the Shunting-yard algorithm
	"""
	outputQueue = []
	operatorStack = []
	for token in tokens:
		if token == BRACKET_OPEN: operatorStack.append(token)
		elif token == BRACKET_SHUT:
			while operatorStack and operatorStack[-1] != BRACKET_OPEN:
				outputQueue.append(operatorStack.pop())
			if operatorStack.pop() != BRACKET_OPEN:
				raise UnitError(f"Detected mismatched parentheses: '{BRACKET_SHUT}'")
		elif isOperator(token):
			while (
				operatorStack and
				operatorStack[-1] != BRACKET_OPEN and
				hasHigherPrecedence(operatorStack[-1], token)
			): outputQueue.append(operatorStack.pop())
			operatorStack.append(token)
		else:
			outputQueue.append(token)
	
	while operatorStack:
		if operatorStack[-1] == BRACKET_OPEN:
			raise UnitError(f"Detected mismatched parentheses: '{BRACKET_OPEN}'")
		outputQueue.append(operatorStack.pop())

	return outputQueue

def aggregateSign(tokens, updatedTokens = []):
	"""
	Replace the negation operator '-' with a multiplication by -1
	@param tokens: a list of tokens
	"""
	def aggregateSignHelper(tokens, updatedTokens):
		while tokens:
			token = tokens.pop(0)
			if token == BRACKET_OPEN:
				updatedTokens.append(token)
				aggregateSignHelper(tokens, updatedTokens)
			elif token == BRACKET_SHUT:
				updatedTokens.append(token)
				return updatedTokens
			elif ((token == OPERATOR_ADD or token == OPERATOR_SUB) and
				(not updatedTokens or isSpecialChar(updatedTokens[-1]))
			):
				if tokens and isFloat(tokens[0]):
					updatedTokens.append(f"{token}{tokens.pop(0)}")
				else:
					updatedTokens.extend([BRACKET_OPEN, f"{token}1", OPERATOR_MUL])
					aggregateSignHelper(tokens, updatedTokens)
					updatedTokens.append(BRACKET_SHUT)
			else: updatedTokens.append(token)
	
	updatedTokens = []
	aggregateSignHelper(tokens, updatedTokens)
	if tokens: raise UnitError(f"Detected mismatched parentheses: '{BRACKET_SHUT}'")
	return updatedTokens

def aggregateUnits(tokens):
	"""
	Combine tokens which constitute compound units
	@param tokens: a list of tokens
	"""
	aggregatedTokens = []
	unitTokens = []
	parsingExp = 0

	def appendUnitTokens(aggregatedTokens, unitTokens, token = None):
		# Append unit tokens to list of aggregated tokens
		if unitTokens:
			if unitTokens[-1] == OPERATOR_MUL or unitTokens[-1] == OPERATOR_DIV:
				operator = unitTokens.pop()
				aggregatedTokens.append(unitTokens)
				aggregatedTokens.append(operator)
			else: aggregatedTokens.append(unitTokens)
		if token is not None:
			# Inject multiplication if needed
			if ((aggregatedTokens) and
				(not isSpecialChar(aggregatedTokens[-1])) and
				(token == BRACKET_OPEN)
			): aggregatedTokens.append(OPERATOR_MUL)
			aggregatedTokens.append(token)
		return []
	
	def handleParseExpDecrement(tokens, unitTokens, parsingExp):
		# Check if multiplication needs to be injected between adjacent units
		if parsingExp != 1: return parsingExp
		if tokens:
			if tokens[0] == OPERATOR_MUL or tokens[0] == OPERATOR_DIV:
				unitTokens.append(tokens.pop(0))
			elif isValidSymbol(tokens[0]):
				unitTokens.append(OPERATOR_MUL)
		return 0
	
	def handleAppendUnitSymbol(tokens, unitTokens, parsingExp):
		if tokens:
			token = tokens[0]
			if token == OPERATOR_EXP:
				unitTokens.append(tokens.pop(0))
				return 1
			elif token == OPERATOR_MUL or token == OPERATOR_DIV:
				unitTokens.append(tokens.pop(0))
			elif isValidSymbol(token):
				unitTokens.append(OPERATOR_MUL)
		return parsingExp

	while tokens:
		token = getNextToken(tokens)
		if token == BRACKET_OPEN:
			if parsingExp:
				unitTokens.append(token)
				parsingExp += 1
			else: unitTokens = appendUnitTokens(aggregatedTokens, unitTokens, token)
		elif token == BRACKET_SHUT:
			if parsingExp:
				unitTokens.append(token)
				parsingExp = handleParseExpDecrement(tokens, unitTokens, parsingExp - 1)
			else: unitTokens = appendUnitTokens(aggregatedTokens, unitTokens, token)
		elif isFloat(token):
			if parsingExp:
				if not isInt(token): raise UnitError(f"Expected int; received '{token}'")
				unitTokens.append(token)
				parsingExp = handleParseExpDecrement(tokens, unitTokens, parsingExp)
			else: unitTokens = appendUnitTokens(aggregatedTokens, unitTokens, token)
		elif isValidSymbol(token):
			if parsingExp: raise UnitError(f"Expected int; received '{token}'")
			unitTokens.append(token)
			parsingExp = handleAppendUnitSymbol(tokens, unitTokens, parsingExp)
		elif isOperator(token):
			if parsingExp: raise UnitError(f"Expected int; received '{token}'")
			else: unitTokens = appendUnitTokens(aggregatedTokens, unitTokens, token)
		else: raise UnitError(f"Unknown token; received '{token}'")

	appendUnitTokens(aggregatedTokens, unitTokens)
	return aggregatedTokens

def aggregateQuantities(tokens):
	"""
	Combine tokens which constitute a quantity
	@param tokens: a list of tokens
	"""
	aggregatedTokens = []
	needsValue = True

	while tokens:
		if isOperator(tokens[0]):
			if needsValue: raise UnitError(f"Expected float; received '{tokens[0]}'")
			aggregatedTokens.append(tokens.pop(0))
			needsValue = True
		elif isSpecialChar(tokens[0]):
			aggregatedTokens.append(tokens.pop(0))
		else:
			needsValue = False

			# Get value
			quantity = '1'
			try:
				float(tokens[0])
				quantity = tokens.pop(0)
			except:
				# Inject multiplication where needed
				if aggregatedTokens and aggregatedTokens[-1] == BRACKET_SHUT:
					aggregatedTokens.append(OPERATOR_MUL)

			# Get unit
			unit = []
			if tokens and isinstance(tokens[0], list):
				unit = tokens.pop(0)

			aggregatedTokens.append((quantity, unit))
	if needsValue and aggregatedTokens: raise UnitError(f"Expected float; no tokens received")

	return aggregatedTokens

def aggregate(tokens):
	tokens = aggregateSign(tokens)
	tokens = aggregateUnits(tokens)
	tokens = aggregateQuantities(tokens)
	return tokens

def parseUnit(tokens):
	tokens = convertToRPN(tokens)

	stack = []
	for token in tokens:
		if token == OPERATOR_ADD:
			a = stack.pop()
			if not isinstance(a, int): raise UnitError(f"Expected int; received '{a}'")
			b = stack.pop()
			if not isinstance(b, int): raise UnitError(f"Expected int; received '{b}'")
			stack.append(b + a)
		elif token == OPERATOR_SUB:
			a = stack.pop()
			if not isinstance(a, int): raise UnitError(f"Expected int; received '{a}'")
			b = stack.pop()
			if not isinstance(b, int): raise UnitError(f"Expected int; received '{b}'")
			stack.append(b - a)
		elif token == OPERATOR_MUL:
			a = stack.pop()
			if not isinstance(a, dict): a = {a: 1}
			b = stack.pop()
			if not isinstance(b, dict): b = {b: 1}
			for sym, exp in b.items():
				if sym not in a: a[sym] = 0
				a[sym] += exp
			stack.append(a)
		elif token == OPERATOR_DIV:
			a = stack.pop()
			if not isinstance(a, dict): a = {a: 1}
			b = stack.pop()
			if not isinstance(b, dict): b = {b: 1}
			for sym, exp in a.items():
				if sym not in b: b[sym] = 0
				b[sym] -= exp
			stack.append(b)
		elif token == OPERATOR_EXP:
			a = stack.pop()
			b = stack.pop()
			if not isinstance(a, int): raise UnitError(f"Expected int; received '{a}'")
			stack.append({b: a})
		else:
			if isInt(token): stack.append(int(token))
			else: stack.append(token)

	# Aggregate into a single map
	units = {}
	while stack:
		top = stack.pop()
		if isinstance(top, dict):
			for sym, exp in top.items():
				if sym not in units: units[sym] = 0
				units[sym] += exp
		elif isValidSymbol(top):
			if top not in units: units[top] = 0
			units[top] += 1
		else: raise UnitError("Invalid expression")
	return units

def parseExpr(tokens):
	stack = []
	for token in tokens:
		if token == OPERATOR_ADD:
			a = stack.pop()
			b = stack.pop()
			stack.append(UC_AST.AST_Add(b, a))
		elif token == OPERATOR_SUB:
			a = stack.pop()
			b = stack.pop()
			stack.append(UC_AST.AST_Sub(b, a))
		elif token == OPERATOR_MUL:
			a = stack.pop()
			b = stack.pop()
			stack.append(UC_AST.AST_Mul(b, a))
		elif token == OPERATOR_DIV:
			a = stack.pop()
			b = stack.pop()
			stack.append(UC_AST.AST_Div(b, a))
		elif token == OPERATOR_EXP:
			a = stack.pop()
			b = stack.pop()
			stack.append(UC_AST.AST_Exp(b, a))
		elif token == OPERATOR_EQL:
			a = stack.pop()
			b = stack.pop()
			stack.append(UC_AST.AST_Eql(b, a))
		else:
			valStr, unitTokens = token
			val = float(valStr)
			baseUnits = UC_Unit.Unit(baseUnits = parseUnit(unitTokens)).reduce()
			unit = UC_Unit.Unit(baseUnits = baseUnits)
			stack.append(UC_Unit.Quantity(val, unit))
	if not stack: return ""
	if len(stack) != 1: raise UnitError("Invalid expression")
	return stack[0]

def parse(string):
	tokens = tokenize(string)
	tokens = aggregate(tokens)
	tokens = convertToRPN(tokens)
	return parseExpr(tokens)