from Unit import *

def test_fail(msg, verbose):
	if verbose: print(f"Test failed: {msg}")
	return 1

def test_equality(verbose = False):
	test_result = 0
	unit_m = Unit("m")
	unit_g = Unit("g")
	q1 = Quantity(1, unit_m)
	q2 = Quantity(1, unit_m)
	q3 = Quantity(1, unit_g)
	q4 = Quantity(2, unit_m)

	# Test equality reflexivity
	if (not q1 == q1) or (not q1 == q2):
		test_result += test_fail("equality reflexivity", verbose)
	
	if (q1 != q1) or (q1 != q2):
		test_result += test_fail("inequality reflexivity", verbose)
	
	# Test unit inequality
	if q1 == q3:
		test_result += test_fail("equality of unequal units", verbose)
	
	if not q1 != q3:
		test_result += test_fail("inequality of unequal units", verbose)

	# Test equality of equivalent units
	if not (Quantity(1, Unit(baseUnits = {"m": 0})) == Quantity(1, Unit(baseUnits = {}))):
		test_result += test_fail("equality of equivalent units", verbose)

	# Test value inequality
	if q1 == q4:
		test_result += test_fail("equality of unequal values", verbose)
	
	if not q1 != q4:
		test_result += test_fail("inequality of unequal values", verbose)

	return test_result

def test_addition(verbose = False):
	test_result = 0
	unit_g = Unit("g")
	unit_m1 = Unit("m")
	unit_m2 = Unit(baseUnits = {"m": 2})

	# Try adding two values with the same unit
	if Quantity(1, unit_m1) + Quantity(1, unit_m1) != Quantity(2, unit_m1):
		test_result += test_fail("adding two values with the same unit", verbose)

	# Try adding two values with different units
	try:
		Quantity(1, unit_m1) + Quantity(1, unit_g)
		test_result += test_fail("adding two values with different units", verbose)
	except: pass

	try:
		Quantity(1, unit_m1) + Quantity(1, unit_m2)
		test_result += test_fail("adding two values with different unit exponents", verbose)
	except: pass

	# Try subtracting two values with the same unit
	if Quantity(2, unit_m1) - Quantity(1, unit_m1) != Quantity(1, unit_m1):
		test_result += test_fail("subtracting two values with the same unit", verbose)
	
	# Try subtracting two values with different units
	try:
		Quantity(1, unit_m1) - Quantity(1, unit_g)
		test_result += test_fail("subtracting two values with different units", verbose)
	except: pass

	try:
		Quantity(1, unit_m1) - Quantity(1, unit_m2)
		test_result += test_fail("subtracting two values with different units exponents", verbose)
	except: pass

	return test_result

def test_multiplication(verbose = False):
	test_result = 0
	unit_m = Unit("m")
	unit_g = Unit("g")
	q1 = Quantity(4, unit_m)
	q2 = Quantity(2, unit_m)
	q3 = Quantity(2, unit_g)

	# Try multiplying two values with the same unit
	if q1 * q2 != Quantity(8, Unit(baseUnits = {"m": 2})):
		test_result += test_fail("multiplying two values with the same unit", verbose)
	
	# Try multiplying two values with different units
	if q1 * q3 != Quantity(8, Unit(baseUnits = {"m": 1, "g": 1})):
		test_result += test_fail("multiplying two values with different units", verbose)
	
	# Try dividing two values with the same unit
	if q1 / q2 != Quantity(2, Unit()):
		test_result += test_fail("dividing two values with the same unit", verbose)
	
	# Try dividing two values with different units
	if q1 / q3 != Quantity(2, Unit(baseUnits = {"m": 1, "g": -1})):
		test_result += test_fail("dividing two values with different units", verbose)

	return test_result

def main():
	# Run tests
	verbose = True
	print(f"test_equality: {test_equality(verbose)} tests failed")
	print(f"test_addition: {test_addition(verbose)} tests failed")
	print(f"test_multiplication: {test_multiplication(verbose)} tests failed")

if (__name__ == "__main__"):
	main()