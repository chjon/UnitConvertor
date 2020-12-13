from Unit import *
from UnitConvertor import *

def test_conversion(verbose = False):
	test_result = 0
	units, conversions, prefixes = loadConversions("standard.csv")
	# writeConversions("test.csv", units, conversions, prefixes)

	# Test topological sort
	convertor = Convertor(units, conversions, prefixes)
	print(convertor.convert(
		Unit("N"),
		Unit(baseUnits={"kg": 1, "m": 1, "s": -2})
	))

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_conversion: {test_conversion(verbose)} tests failed")

if (__name__ == "__main__"):
	main()