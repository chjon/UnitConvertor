from Unit import *
from UnitConvertor import *

def test_conversion(verbose = False):
	test_result = 0
	units, conversions = loadConversions("standard.csv")
	# writeConversions("test2.csv", units, conversions)

	# Test topological sort
	convertor = Convertor(units, conversions)
	print(convertor.convert(
		Unit("mph"),
		Unit(baseUnits={"yd": 1, "min": -1})
	))

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_conversion: {test_conversion(verbose)} tests failed")

if (__name__ == "__main__"):
	main()