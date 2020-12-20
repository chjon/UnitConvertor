from UC_Unit import *
from UC_Convertor import *
from UC_FileIO import *

def test_conversion(verbose = False):
	test_result = 0
	units, conversions, prefixes = loadFile("standard.csv")
	# writeConversions("test.csv", units, conversions, prefixes)

	# Test topological sort
	convertor = Convertor(units, conversions, prefixes)
	print(convertor.convert(
		Unit(baseUnits=parseUnitStr("uJ^-2")),
		Unit(baseUnits=parseUnitStr("eV^-1 kW^-1 hr^-1"))
	))

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_conversion: {test_conversion(verbose)} tests failed")

if (__name__ == "__main__"):
	main()