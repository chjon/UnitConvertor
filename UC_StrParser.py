import UC_Common
import UC_Utils
import UC_Unit
import UC_AST

OPERATOR_EXP = '^'
OPERATOR_MUL = '*'
OPERATOR_DIV = '/'
OPERATOR_ADD = '+'
OPERATOR_SUB = '-'
OPERATOR_EQL = ':'
BRACKET_OPEN = '('
BRACKET_SHUT = ')'

# Map of operator to precedence and associativity
# A larger precedence value means that the operator is higher precedence
# An associativity of 1 means that the operator is left associative
operatorPrecedences = {
	OPERATOR_EXP: (3, 0),
	OPERATOR_MUL: (2, 1),
	OPERATOR_DIV: (2, 1),
	OPERATOR_ADD: (1, 1),
	OPERATOR_SUB: (1, 1),
	OPERATOR_EQL: (0, 1),
}

def isOperator(char):
	"""
	Determine whether a character is an operator
	@param char: the character to check
	"""
	return str(char) in operatorPrecedences

def isSpecialChar(char):
	"""
	Determine whether a character is its own token
	@param char: the character to check
	"""
	return (
		isOperator(char) or
		char == BRACKET_OPEN or
		char == BRACKET_SHUT
	)

def hasHigherPrecedence(operatorA, operatorB):
	"""
	Determine whether an operator has higher precedence
	@param operatorA: the first operator
	@param operatorB: the second operator
	@return True if operatorA has higher precedence
	"""
	precedenceA, associativityA = operatorPrecedences[operatorA]
	precedenceB, associativityB = operatorPrecedences[operatorB]
	return (precedenceA > precedenceB) or (precedenceA == precedenceB and associativityB == 1)

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
		elif UC_Utils.isWhitespace(char):
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
				raise UC_Common.UnitError(f"Detected mismatched parentheses: '{BRACKET_SHUT}'")
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
			raise UC_Common.UnitError(f"Detected mismatched parentheses: '{BRACKET_OPEN}'")
		outputQueue.append(operatorStack.pop())

	return outputQueue

def replaceNegation(tokens):
	"""
	Replace the negation operator '-' with a multiplication by -1
	@param tokens: a list of tokens
	"""
	updatedTokens = []
	while tokens:
		token = tokens.pop(0)
		if ((token == OPERATOR_ADD or token == OPERATOR_SUB) and
			(not updatedTokens or isSpecialChar(updatedTokens[-1]))
		):
			if tokens and UC_Utils.isFloat(tokens[0]):
				updatedTokens.append(f"{token}{tokens.pop(0)}")
			else:
				updatedTokens.extend([f"{token}1", OPERATOR_MUL])
		else: updatedTokens.append(token)
	return updatedTokens

def aggregateUnits(tokens):
	"""
	Combine tokens which constitute compound units
	@param tokens: a list of tokens
	"""
	aggregatedTokens = []
	unitTokens = []
	parsingExp = 0

	while tokens:
		token = UC_Utils.getNextToken(tokens)
		if token == BRACKET_OPEN:
			if parsingExp:
				parsingExp += 1
				unitTokens.append(token)
			else:
				if unitTokens:
					if unitTokens[-1] == OPERATOR_MUL or unitTokens[-1] == OPERATOR_DIV:
						operator = unitTokens.pop()
						aggregatedTokens.append(unitTokens)
						aggregatedTokens.append(operator)
					else: aggregatedTokens.append(unitTokens)
				unitTokens = []
				aggregatedTokens.append(token)
		elif token == BRACKET_SHUT:
			if parsingExp:
				parsingExp -= 1
				unitTokens.append(token)
				if parsingExp == 1:
					parsingExp = 0
					if tokens:
						if isOperator(tokens[0]):
							unitTokens.append(tokens.pop(0))
						elif UC_Utils.isValidSymbol(tokens[0]):
							unitTokens.append(OPERATOR_MUL)
			else:
				if unitTokens:
					if unitTokens[-1] == OPERATOR_MUL or unitTokens[-1] == OPERATOR_DIV:
						operator = unitTokens.pop()
						aggregatedTokens.append(unitTokens)
						aggregatedTokens.append(operator)
					else: aggregatedTokens.append(unitTokens)
				unitTokens = []
				aggregatedTokens.append(token)
		elif UC_Utils.isFloat(token):
			if parsingExp:
				if not UC_Utils.isInt(token): raise UC_Common.UnitError(f"Expected int; received '{token}'")
				unitTokens.append(token)
				if parsingExp == 1:
					parsingExp = 0
					if tokens:
						if isOperator(tokens[0]):
							unitTokens.append(tokens.pop(0))
						elif UC_Utils.isValidSymbol(tokens[0]):
							unitTokens.append(OPERATOR_MUL)
			else:
				if unitTokens:
					if unitTokens[-1] == OPERATOR_MUL or unitTokens[-1] == OPERATOR_DIV:
						operator = unitTokens.pop()
						aggregatedTokens.append(unitTokens)
						aggregatedTokens.append(operator)
					else: aggregatedTokens.append(unitTokens)
				unitTokens = []
				aggregatedTokens.append(token)
		elif UC_Utils.isValidSymbol(token):
			if parsingExp: raise UC_Common.UnitError(f"Expected int; received '{token}'")
			unitTokens.append(token)
			if tokens:
				operator = tokens[0]
				if operator == OPERATOR_EXP:
					unitTokens.append(tokens.pop(0))
					parsingExp = True
				elif operator == OPERATOR_MUL or operator == OPERATOR_DIV:
					unitTokens.append(tokens.pop(0))
				elif UC_Utils.isValidSymbol(operator):
					unitTokens.append(OPERATOR_MUL)
		elif isOperator(token):
			if parsingExp: raise UC_Common.UnitError(f"Expected int; received '{token}'")
			else:
				if unitTokens:
					if unitTokens[-1] == OPERATOR_MUL or unitTokens[-1] == OPERATOR_DIV:
						operator = unitTokens.pop()
						aggregatedTokens.append(unitTokens)
						aggregatedTokens.append(operator)
					else: aggregatedTokens.append(unitTokens)
				unitTokens = []
				aggregatedTokens.append(token)
		else:
			raise UC_Common.UnitError(f"Unknown token; received '{token}'")

	if unitTokens: aggregatedTokens.append(unitTokens)
	return aggregatedTokens

def aggregateQuantities(tokens):
	"""
	Combine tokens which constitute a quantity
	@param tokens: a list of tokens
	"""
	aggregatedTokens = []
	needsValue = False

	while tokens:
		if isOperator(tokens[0]):
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
			except: pass

			# Get unit
			unit = []
			if tokens and isinstance(tokens[0], list):
				unit = tokens.pop(0)

			aggregatedTokens.append((quantity, unit))
	if needsValue: raise UC_Common.UnitError(f"Expected float; no tokens received")

	return aggregatedTokens

def parseUnit(tokens):
	tokens = convertToRPN(tokens)

	stack = []
	for token in tokens:
		if token == OPERATOR_ADD:
			a = stack.pop()
			if not isinstance(a, int): raise UC_Common.UnitError(f"Expected int; received '{a}'")
			b = stack.pop()
			if not isinstance(b, int): raise UC_Common.UnitError(f"Expected int; received '{b}'")
			stack.append(b + a)
		elif token == OPERATOR_SUB:
			a = stack.pop()
			if not isinstance(a, int): raise UC_Common.UnitError(f"Expected int; received '{a}'")
			b = stack.pop()
			if not isinstance(b, int): raise UC_Common.UnitError(f"Expected int; received '{b}'")
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
			for sym, exp in b.items():
				if sym not in a: a[sym] = 0
				a[sym] -= exp
			stack.append(a)
		elif token == OPERATOR_EXP:
			a = stack.pop()
			b = stack.pop()
			if not isinstance(a, int): raise UC_Common.UnitError(f"Expected int; received '{a}'")
			stack.append({b: a})
		else:
			if UC_Utils.isInt(token): stack.append(int(token))
			else: stack.append(token)

	# Aggregate into a single map
	units = {}
	while stack:
		top = stack.pop()
		if isinstance(top, dict):
			for sym, exp in top.items():
				if sym not in units: units[sym] = 0
				units[sym] += exp
		elif UC_Utils.isValidSymbol(top):
			if top not in units: units[top] = 0
			units[top] += 1
		else: raise UC_Common.UnitError("Invalid expression")
	return units

def parseExpr(string):
	tokens = tokenize(string)
	tokens = replaceNegation(tokens)
	tokens = aggregateUnits(tokens)
	tokens = aggregateQuantities(tokens)
	tokens = convertToRPN(tokens)

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
			baseUnits = parseUnit(unitTokens)
			unit = UC_Unit.Unit(baseUnits = baseUnits)
			stack.append(UC_Unit.Quantity(val, unit))
	if not stack: return ""
	if len(stack) != 1: raise UC_Common.UnitError("Invalid expression")
	return stack[0]
