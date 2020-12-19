from Unit import *
from UnitConvertor import *
import UnitParser

def test_conversion(verbose = False):
	test_result = 0
	units, conversions, prefixes = loadConversions("standard.csv")
	# writeConversions("test.csv", units, conversions, prefixes)

	# Test topological sort
	convertor = Convertor(units, conversions, prefixes)
	print(convertor.convert(
		Unit(baseUnits=UnitParser.parseUnitStr("uJ^-2")),
		Unit(baseUnits=UnitParser.parseUnitStr("eV^-1 kW^-1 hr^-1"))
	))

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_conversion: {test_conversion(verbose)} tests failed")

if (__name__ == "__main__"):
	main()