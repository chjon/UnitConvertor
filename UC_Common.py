class UnitError(Exception): pass
class FileFormatError(Exception): pass

END_DELIMITER = ';'
SEP_DELIMITER = ','
MAP_DELIMITER = ':'
COMMENT_DELIMITER = '#'

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