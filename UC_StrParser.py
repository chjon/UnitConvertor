import UC_Common
import UC_Utils

OPERATOR_EXP = '^'
OPERATOR_MUL = '*'
OPERATOR_DIV = '/'
OPERATOR_ADD = '+'
OPERATOR_SUB = '-'
OPERATOR_EQL = '='
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
	OPERATOR_EQL: (0, 0),
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

def aggregateUnits(tokens):
	"""
	Combine tokens which constitute compound units
	@param tokens: a list of tokens
	"""
	aggregatedTokens = []

	while tokens:
		if UC_Utils.isValidSymbol(tokens[0]):
			aggregatedUnit = []
			while tokens and UC_Utils.isValidSymbol(tokens[0]):
				aggregatedUnit.append(getNextToken(tokens))
				if len(tokens) > 1 and isOperator(tokens[0]):
					if tokens[0] == OPERATOR_EXP:
						try:
							int(tokens[1])
							aggregatedUnit.append(getNextToken(tokens))
							aggregatedUnit.append(getNextToken(tokens))
							continue
						except: pass
					elif tokens[0] == OPERATOR_MUL or tokens[0] == OPERATOR_DIV:
						if UC_Utils.isValidSymbol(tokens[1]):
							aggregatedUnit.append(getNextToken(tokens))
							continue
				break
			aggregatedTokens.append(aggregatedUnit)
		else:
			aggregatedTokens.append(getNextToken(tokens))

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
