# UnitConvertor
This is a program for performing arithmetic operations while accounting for the units associated with each quantity.

## Commands
* `exit`: Exit the program
* `help`: Print help text
* `load <filename>`: Unload current definitions and load definitions from file
* `save <filename>`: Save currently-loaded definitions to file

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