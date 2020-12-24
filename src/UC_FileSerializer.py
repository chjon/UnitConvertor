import src.UC_Common as UC_Common

def serializePrefixes(prefixes):
	"""
	Generate strings representing the prefix map
	@param prefixes: the prefixes to convert to strings
	@return a list of lines representing the prefix map
	"""
	lines = []

	# Aggregate prefixes by base
	aggregatedPrefixes = {}
	for prefix, (base, exp) in prefixes.items():
		if base not in aggregatedPrefixes: aggregatedPrefixes[base] = {}
		aggregatedPrefixes[base][prefix] = exp
	
	# Serialize prefixes
	for base, prefixMapping in aggregatedPrefixes.items():
		line = f"{base}{UC_Common.MAP_DELIMITER}"
		for prefix, exp in prefixMapping.items():
			line += f"{prefix} {exp}{UC_Common.SEP_DELIMITER}"
		lines.append(f"{line[0:-1]}{UC_Common.END_DELIMITER}")

	return lines

def serializeUnitConversions(units, conversions):
	"""
	Generate strings representing the unit conversion maps
	@param units: the units to convert to strings
	@param conversions: the scale factors to convert to strings
	@return a list of lines representing the unit conversion maps
	"""
	lines = []

	for sym, unit in units.items():
		line = f"{sym}{UC_Common.MAP_DELIMITER}"

		# Add conversion for derived units
		if sym in conversions:
			line += f"{conversions[sym]}{UC_Common.SEP_DELIMITER}"
			for baseUnit, exp in unit.baseUnits.items():
				line += f"{baseUnit} {exp}{UC_Common.SEP_DELIMITER}"

		lines.append(f"{line[0:-1]}{UC_Common.END_DELIMITER}")
	
	return lines
