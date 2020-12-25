# UnitConvertor
This is a program for performing arithmetic operations while accounting for the units associated with each quantity.

## Running the program
* `python3 main.py`: Run the main program
* `python3 test.py`: Run the unit tests

## Commands
* `exit`: Exit the program
* `help`: Print help text
* `show <unit|prefix> [symbol]`: Show currently-loaded definitions
	* `show unit`: Show all currently-loaded unit definitions
	* `show unit [symbol]`: Show the definition of the requested symbol (e.g. `show unit mph`)
	* `show prefix`: Show all currently-loaded prefix definitions
	* `show prefix [symbol]`: Show the definition of the requested symbol (e.g. `show prefix k`)
* `add <unit|prefix> <symbol> [definition]`: Add a unit/prefix definition
	* `add unit <symbol> [definition]`: Define a new unit with the given symbol, equal to the result of evaluating the given definition (e.g. `add unit in 2.54 cm`)
	* `add prefix <symbol> <base> <exp>`: Define a new prefix with the given symbol, equal to multiplying by the given power of the given base (e.g. `add prefix k 10 3`)
* `del <unit|prefix> <symbol>`: Delete a unit/prefix definition and all definitions which depend on it
	* `del unit <symbol>`: Delete the unit with the given symbol, as well as all units whose definitions depend on it
	* `del prefix <symbol>`: Delete the prefix with the given symbol, as well as all units whose definitions depend on it
* `load <filename> <mode>`: Load additional definitions from file (e.g. `load misc.uc 2`)
	* Mode `0`: Unload all currently-loaded definitions before loading file
	* Mode `1`: Load file and overwrite old definitions with new ones
	* Mode `2`: Load file but do not overwrite old definitions
* `save <filename>`: Save currently-loaded definitions to file (e.g. `save customUnits.uc`)
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

Additional units and unit conversions are specified in the `misc.uc` data file, which is an extension to `standard.uc`.
This includes a variety of standard and non-standard units.
The conversions contained in this file are dependent on the units defined in `standard.uc`.
