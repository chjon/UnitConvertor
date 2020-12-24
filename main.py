import fileinput
import UC_FileIO
import UC_Convertor
import UC_StrParser
from UC_Common import *

DEFAULT_FILE = "standard.uc"

COMMAND_EXIT = "exit"
COMMAND_HELP = "help"
COMMAND_LOAD = "load"
COMMAND_SAVE = "save"
convertor = UC_Convertor.Convertor({}, {}, {})
INDENT = " -> "

def command_help(args):
	helpStrings = {
		COMMAND_EXIT: "Exit the program",
		COMMAND_HELP: "Print this text",
		COMMAND_LOAD: "Unload current definitions and load definitions from file",
		COMMAND_SAVE: "Save currently-loaded definitions to file",
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
	if len(args) != 2: print("Usage: load <filename>")
	else:
		try:
			units, conversions, prefixes = UC_FileIO.loadFile(args[1])
			global convertor
			convertor = UC_Convertor.Convertor(units, conversions, prefixes)
			print(f"Successfully loaded definitions from '{args[1]}'")
		except: print(f"Encountered error while loading from '{args[1]}'")

def command_save(args):
	if len(args) != 2: print("Usage: save <filename>")
	else:
		try:
			UC_FileIO.writeFile(args[1], convertor.units, convertor.conversions, convertor.prefixes)
			print(f"Successfully saved definitions to '{args[1]}'")
		except: print(f"Encountered error while saving to '{args[1]}'")

commands = {
	COMMAND_EXIT: (lambda args: exit()),
	COMMAND_HELP: (lambda args: command_help(args)),
	COMMAND_LOAD: (lambda args: command_load(args)),
	COMMAND_SAVE: (lambda args: command_save(args)),
}

def main():
	command_load(["load","standard.csv"])
	print(f"Type '{COMMAND_HELP}' for a list of commands")
	for line in fileinput.input():
		line = line.strip()
		command = line.split()
		if command and (command[0] in commands): commands[command[0]](command)
		elif line:
			try:
				ast = UC_StrParser.parse(line)
				print(f"Interpreting input as: '{str(ast)}'")
				print(f"{INDENT}{str(ast.evaluate(convertor))}")
			except UnitError as err:
				print(f"{INDENT}Error: {err}")
			finally: print()

if (__name__ == "__main__"):
	main()