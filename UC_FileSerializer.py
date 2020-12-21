from UC_Common import *

def serializePrefixes(prefixes):
	lines = []

	# Aggregate prefixes by base
	aggregatedPrefixes = {}
	for prefix, (base, exp) in prefixes.items():
		if base not in aggregatedPrefixes: aggregatedPrefixes[base] = {}
		aggregatedPrefixes[base][prefix] = exp
	
	# Serialize prefixes
	for base, prefixMapping in aggregatedPrefixes.items():
		line = f"{base}{MAP_DELIMITER}"
		for prefix, exp in prefixMapping.items():
			line += f"{prefix} {exp}{SEP_DELIMITER}"
		lines.append(f"{line[0:-1]}{END_DELIMITER}")

	return lines

def serializeUnitConversions(units, conversions):
	lines = []

	for sym, unit in units.items():
		line = f"{sym}{MAP_DELIMITER}"

		# Add conversion for derived units
		if sym in conversions:
			line += f"{conversions[sym]}{SEP_DELIMITER}"
			for baseUnit, exp in unit.baseUnits.items():
				line += f"{baseUnit} {exp}{SEP_DELIMITER}"

		lines.append(f"{line[0:-1]}{END_DELIMITER}")
	
	return lines
