import UC_Common
import UC_Utils

OPERATOR_EXP = '^'
OPERATOR_MUL = '*'
OPERATOR_DIV = '/'
OPERATOR_ADD = '+'
OPERATOR_SUB = '-'
BRACKET_OPEN = '('
BRACKET_SHUT = ')'

# Map of operator to precedence and associativity
# A larger precedence value means that the operator is higher precedence
# An associativity of 1 means that the operator is right associative
operatorPrecedences = {
	OPERATOR_EXP: (3, 1),
	OPERATOR_MUL: (2, 0),
	OPERATOR_DIV: (2, 0),
	OPERATOR_ADD: (1, 0),
	OPERATOR_SUB: (1, 0),
}

def isOperator(char):
	"""
	Determine whether a character is an operator
	@param char: the character to check
	"""
	if isinstance(char, tuple): return False
	return char in operatorPrecedences

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

def tokenize(line):
	"""
	Convert a string into a list of tokens
	@param line: the string to convert
	@return a list of tokens
	"""
	tokens = []
	token = ''
	
	# Identify tokens
	for char in line:
		if UC_Utils.isWhitespace(char):
			if token:
				tokens.append(token)
				token = ""
		elif isSpecialChar(char):
			if token:
				tokens.append(token)
				token = ""
			tokens.append(char)
		else:
			token += char
	
	if token:
		tokens.append(token)
		token = ""

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

def peekNextToken(tokens: list = []):
	"""
	Get the next token without removing it from the queue
	@param tokens: a list of tokens
	@return the next token
	"""
	if not tokens: raise UnitError(f"Expected token; none received")
	return tokens[0]

def getNextToken(tokens: list = [], expectedToken = None):
	"""
	Get the next token and remove it from the queue
	@param tokens: a list of tokens
	@param expectedToken: the expected token - an error is thrown if the next token
	does not equal the expected token
	@return the next token
	"""
	if not tokens: raise UnitError(f"Expected token; none received")
	token = tokens.pop(0)
	if expectedToken and token != expectedToken: raise UnitError(f"Expected '{expectedToken}'; received '{token}'")
	return token

def aggregateUnit(tokens):
	# Find the index of the next quantity
	index = 1
	openedBrackets = 0
	for i, token in enumerate(tokens):
		if token == BRACKET_OPEN: openedBrackets += 1
		elif token == BRACKET_SHUT: openedBrackets -= 1
		elif openedBrackets == -1:
			index = i - 1
			break
		elif openedBrackets == 0:
			try:
				float(token)
				index = i - 1
				break
			except: pass
	
	# Aggregate tokens belonging to the same unit
	index = max(1, index)
	aggregatedUnit = tokens[:index]

	# Pop used tokens from list
	del tokens[:index]
	return aggregatedUnit

def aggregateUnits(tokens):
	"""
	Combine tokens which constitute compound units
	@param tokens: a list of tokens
	"""
	aggregatedTokens = []

	while tokens:
		# Handle brackets
		closingBrackets = 0
		if tokens and tokens[0] == BRACKET_OPEN:
			aggregatedTokens.append(tokens.pop(0))
			continue

		# Get the quantity associated with the unit
		quantity = None
		try:
			quantity = float(tokens[0])
			tokens.pop(0)
			while tokens and tokens[0] == BRACKET_SHUT:
				tokens.pop(0)
				closingBrackets += 1
		except: pass

		# Get the unit
		unitTokens = []
		if tokens and UC_Utils.isValidSymbol(tokens[0]): unitTokens = aggregateUnit(tokens)
		while tokens and tokens[0] == BRACKET_SHUT:
			tokens.pop(0)
			closingBrackets += 1
		
		# Add the quantity to the list of aggregated tokens
		if quantity or unitTokens: aggregatedTokens.append((quantity, unitTokens))
		
		# Handle closing brackets
		for i in range(closingBrackets): aggregatedTokens.append(BRACKET_SHUT)

		# Get operator
		if tokens and isOperator(tokens[0]): aggregatedTokens.append(tokens.pop(0))

	return aggregatedTokens

def parseUnitStr(toParse):
	unitMap = {}
	toParse = toParse.strip()
	components = toParse.split(' ')
	for component in components:
		vals = component.split('^')
		sym = vals[0]
		if not (sym in unitMap): unitMap[sym] = 0
		if len(vals) == 1:
			unitMap[sym] += 1
		elif len(vals) == 2:
			unitMap[sym] += int(vals[1])
		else:
			raise UnitError(f"Invalid unit: '{component}'")
	
	return unitMap

# TODO: Implement this!
def parseUnitExpr(string): pass
