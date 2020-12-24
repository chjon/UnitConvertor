# UnitConvertor
This is a program for performing arithmetic operations while accounting for the units associated with each quantity.

## Running the program
* `python3 main.py`: Run the main program
* `python3 test.py`: Run the unit tests

## Commands
* `exit`: Exit the program
* `help`: Print help text
* `load <filename> <mode>`: Load additional definitions from file
	* Modes:
		* `0`: Unload all currently-loaded definitions before loading file
		* `1`: Load file and overwrite old definitions with new ones
		* `2`: Load file but do not overwrite old definitions
* `save <filename>`: Save currently-loaded definitions to file
* `unload`: Unload all currently-loaded definitions

## Expressions
* `[0-9]`: Valid number inputs are integers and decimal values.
* `[a-z,A-Z,_]`: Valid unit symbols are composed of alphabetical characters and underscores
* `:`: Unit conversion
* `+`: Addition
* `-`: Subtraction
* `*`: Multiplication
* `/`: Division
* `^`: Exponentiation

## Sample Inputs
* `1 + 2.7 + 3e-1`
* `60 mph : m/s`
* `100 kg * 9.8 m/s^2 : N`
* `500 N / 12 mm^2 : kPa`
* `123.4 lb / (5 ft + 6 in)^2 : BMI`

## Supported Unit Conversions
The default units and unit conversions are specified in the `standard.uc` data file.
This contains the SI base units, SI derived units, units approved for use with the SI units, and a collection of non-SI units.
Conversions between temperature units are currently unsupported.