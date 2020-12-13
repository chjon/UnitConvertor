from Unit import *
from UnitConvertor import *

def test_conversion(verbose = False):
	test_result = 0

	units = {
		"m"  : Unit("m"  ),
		"g"  : Unit("g"  ),
		"s"  : Unit("s"  ),
		"A"  : Unit("A"  ),
		"K"  : Unit("K"  ),
		"mol": Unit("mol"),
		"cd" : Unit("cd" ),
		"N"  : Unit("N"  , {"m" : +1, "g": +1, "s": -2}),
		"Hz" : Unit("Hz" , {"s" : -1}),
		"J"  : Unit("J"  , {"N" : +1, "m": +1}),
		"Pa" : Unit("Pa" , {"N" : +1, "m": +2}),
		"W"  : Unit("W"  , {"J" : +1, "s": -1}),
		"C"  : Unit("C"  , {"s" : +1, "A": +1}),
		"V"  : Unit("V"  , {"W" : +1, "s": -1}),
		"F"  : Unit("F"  , {"C" : +1, "V": -1}),
		"Ohm": Unit("Ohm", {"V" : +1, "A": -1}),
		"S"  : Unit("S"  , {"A" : +1, "V": -1}),
		"Wb" : Unit("Wb" , {"V" : +1, "s": +1}),
		"T"  : Unit("T"  , {"Wb": +1, "m": -2}),
		"H"  : Unit("H"  , {"Wb": +1, "A": -1}),
		"Bq" : Unit("Bq" , {"s" : -1}),
		"Gy" : Unit("Gy" , {"J" : +1, "g": -1}),
	}

	conversions = {
		"N"  : 1000,
		"Hz" :    1,
		"J"  :    1,
		"Pa" :    1,
		"W"  :    1,
		"C"  :    1,
		"V"  :    1,
		"F"  :    1,
		"Ohm":    1,
		"S"  :    1,
		"Wb" :    1,
		"T"  :    1,
		"H"  :    1,
		"Bq" :    1,
		"Gy" :    1,
	}

	# Test topological sort
	convertor = Convertor(units, conversions)

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_conversion: {test_conversion(verbose)} tests failed")

if (__name__ == "__main__"):
	main()