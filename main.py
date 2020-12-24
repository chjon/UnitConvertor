import fileinput
import src.UC_FileIO as UC_FileIO
import src.UC_Convertor as UC_Convertor
import src.UC_StrParser as UC_StrParser
import src.UC_Common as UC_Common

DEFAULT_FILE = "standard.uc"

COMMAND_EXIT   = "exit"
COMMAND_HELP   = "help"
COMMAND_LOAD   = "load"
COMMAND_SAVE   = "save"
COMMAND_UNLOAD = "unload"
convertor = UC_Convertor.Convertor({}, {}, {})
INDENT = " -> "

def command_help(args):
	helpStrings = {
		COMMAND_EXIT  : "Exit the program",
		COMMAND_HELP  : "Print this text",
		COMMAND_LOAD  : "Load additional definitions from file",
		COMMAND_SAVE  : "Save currently-loaded definitions to file",
		COMMAND_UNLOAD: "Unload all currently-loaded definitions",
	}

	inputExamples = [
		"60 mph : m/s",
		"100 kg * 9.8 m/s^2 : N",
		"500 N / 12 mm^2 : kPa",
		"123.4 lb / (5 ft + 6 in)^2 : BMI",
	]

	print("--------------------------")
	print("Available commands:")
	for command, helpString in helpStrings.items(): print(f"{INDENT}{command}: {helpString}")
	print("Example input:")
	for example in inputExamples: print(f"{INDENT}{example}")
	print("--------------------------")

def command_load(args):
	validModes = {
		"0": "Unload all currently-loaded definitions before loading file",
		"1": "Load file and overwrite old definitions with new ones",
		"2": "Load file but do not overwrite old definitions",
	}

	if len(args) != 3 or args[2] not in validModes:
		print(f"Usage: {COMMAND_LOAD} <filename> <mode>")
		print(f"Modes:")
		for mode, helpString in validModes.items(): print(f"{INDENT}{mode}: {helpString}")
	else:
		try:
			global convertor
			units       = {} if args[2] == "0" else convertor.units.copy()
			conversions = {} if args[2] == "0" else convertor.conversions.copy()
			prefixes    = {} if args[2] == "0" else convertor.prefixes.copy()
			UC_FileIO.loadFile(args[1], units, conversions, prefixes, args[2] == "1")
			convertor = UC_Convertor.Convertor(units, conversions, prefixes)
			print(f"Successfully loaded definitions from '{args[1]}'")
		except (OSError, UC_Common.UnitError, UC_Common.FileFormatError) as err:
			print(f"Encountered error while loading from '{args[1]}': {err}")

def command_unload(args):
	if len(args) != 1: print(f"Usage: {COMMAND_UNLOAD}")
	else:
		global convertor
		convertor = UC_Convertor.Convertor({}, {}, {})
		print(f"Successfully unloaded definitions")

def command_save(args):
	if len(args) != 2: print(f"Usage: {COMMAND_SAVE} <filename>")
	else:
		try:
			UC_FileIO.writeFile(args[1], convertor.units, convertor.conversions, convertor.prefixes)
			print(f"Successfully saved definitions to '{args[1]}'")
		except OSError as err: print(f"Encountered error while saving to '{args[1]}': {err}")

commands = {
	COMMAND_EXIT  : (lambda args: exit()),
	COMMAND_HELP  : (lambda args: command_help(args)),
	COMMAND_LOAD  : (lambda args: command_load(args)),
	COMMAND_SAVE  : (lambda args: command_save(args)),
	COMMAND_UNLOAD: (lambda args: command_unload(args)),
}

def main():
	command_load([COMMAND_LOAD, DEFAULT_FILE, "0"])
	print(f"Type '{COMMAND_HELP}' for a list of commands")
	for line in fileinput.input():
		line = line.strip()
		command = line.split()
		if command and (command[0] in commands):
			commands[command[0]](command)
			print()
		elif line:
			try:
				ast = UC_StrParser.parse(line)
				print(f"Interpreting input as: '{str(ast)}'")
				print(f"{INDENT}{str(ast.evaluate(convertor))}")
			except UC_Common.UnitError as err:
				print(f"{INDENT}Error: {err}")
			finally: print()

if (__name__ == "__main__"):
	main()