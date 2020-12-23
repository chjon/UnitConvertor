import fileinput
import UC_FileIO
import UC_Convertor
import UC_StrParser
from UC_Common import *

COMMAND_EXIT = "exit"
COMMAND_HELP = "help"
COMMAND_LOAD = "load"
COMMAND_SAVE = "save"
units, conversions, prefixes = {}, {}, {}

helpStrings = {
	COMMAND_EXIT: "Exit the program",
	COMMAND_HELP: "Print this text",
	COMMAND_LOAD: "Unload current definitions and load definitions from file",
	COMMAND_SAVE: "Save currently-loaded definitions to file",
}

inputExamples = [
	"100 kg * 9.8 m/s^2 : N",
	"500 N / 12 mm^2 : kPA",
	"123.4 lb / (5 ft + 6 in)^2 : BMI",
]

def command_help(args):
	print("--------------------------")
	print("Available commands:")
	for command, helpString in helpStrings.items(): print(f"   {command}: {helpString}")
	print("Example input:")
	for example in inputExamples: print(f"   {example}")
	print("--------------------------")

def command_load(args):
	if len(args) != 2: print("Usage: load <filename>")
	else: units, conversions, prefixes = UC_FileIO.loadFile(args[1])

def command_save(args):
	if len(args) != 2: print("Usage: save <filename>")
	else: UC_FileIO.writeFile(args[1], units, conversions, prefixes)

commands = {
	COMMAND_EXIT: (lambda args: exit()),
	COMMAND_HELP: (lambda args: command_help(helpStrings)),
	COMMAND_LOAD: (lambda args: command_load(args)),
	COMMAND_SAVE: (lambda args: command_save(args)),
}

def main():
	units, conversions, prefixes = UC_FileIO.loadFile("standard.csv")

	print(f"Type '{COMMAND_HELP}' for a list of commands")
	for line in fileinput.input():
		command = line.strip().split()
		if command and (command[0] in commands): commands[command[0]](command)
		else:
			try:
				ast = UC_StrParser.parseExpr(line)
				print(f"Interpreting input as: '{str(ast)}'")
			except UnitError as err:
				print(err)

if (__name__ == "__main__"):
	main()