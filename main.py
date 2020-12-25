import fileinput
import src.UC_FileIO as UC_FileIO
import src.UC_Convertor as UC_Convertor
import src.UC_StrParser as UC_StrParser
import src.UC_Common as UC_Common
import src.UC_Utils as UC_Utils

DEFAULT_FILE = "standard.uc"

COMMAND_EXIT   = "exit"
COMMAND_HELP   = "help"
COMMAND_EVAL   = "eval"
COMMAND_SHOW   = "show"
COMMAND_ADD    = "add"
COMMAND_DEL    = "del"
COMMAND_LOAD   = "load"
COMMAND_SAVE   = "save"
COMMAND_UNLOAD = "unload"
convertor = UC_Convertor.Convertor({}, {}, {})
INDENT = " -> "

def command_help(args):
	helpStrings = {
		COMMAND_EXIT  : "Exit the program",
		COMMAND_HELP  : "Print this text",
		COMMAND_EVAL  : "Evaluate an expression from file",
		COMMAND_SHOW  : "Show currently-loaded definitions",
		COMMAND_ADD   : "Add a unit/prefix definition",
		COMMAND_DEL   : "Delete a unit/prefix definition and all definitions which depend on it",
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

def command_eval(args):
	if len(args) == 2:
		try:
			file = open(args[1], 'r')
			line = " ".join(file.readlines())
			file.close()
			ast = UC_StrParser.parse(line)
			print(f"Interpreting input as: '{str(ast)}'")
			print(f"{INDENT}{str(ast.evaluate(convertor))}")
		except (OSError, UC_Common.UnitError) as err: print(err)
	else: print(f"Usage: {COMMAND_EVAL} <filename>")

def command_show(args):
	usage = f"Usage: {COMMAND_SHOW} <unit|prefix> [symbol]"
	global convertor
	if len(args) < 2 or len(args) > 3: print(usage)
	elif args[1] == "unit":
		if len(args) > 2:
			try: print(convertor.getUnitDefinitionStr(args[2]))
			except: print(f"Unit '{args[2]}' is not defined")
		else:
			for sym in convertor.units.keys(): print(convertor.getUnitDefinitionStr(sym))
	elif args[1] == "prefix":
		if len(args) > 2:
			try: print(convertor.getPrefixDefinitionStr(args[2]))
			except: print(f"Prefix '{args[2]}' is not defined")
		else:
			for sym in convertor.prefixes.keys(): print(convertor.getPrefixDefinitionStr(sym))
	else: print(usage)

def command_add(args):
	usage = f"Usage: {COMMAND_ADD} <unit|prefix> <symbol> [definition]"
	global convertor
	if len(args) < 3: print(usage)
	elif args[1] == "unit":
		sym = args[2]
		string = " ".join(args[3:]) if len(args) > 3 else ""
		try:
			ast = UC_StrParser.parse(string)
			print(f"Interpreting input as: 1 {sym} = {str(ast)}")
			quantity = ast.evaluate(convertor)
			convertor.addUnit(sym, quantity.value, quantity.unit)
			print(f"Successfully added unit: {convertor.getUnitDefinitionStr(sym)}")
		except UC_Common.UnitError as err: print(err)
	elif args[1] == "prefix":
		if len(args) == 5:
			sym = args[2]
			try: base = Decimal(args[3])
			except: return print(f"Expected float; received {args[3]}")
			try: exp = Decimal(int(args[4]))
			except: return print(f"Expected int; received {args[4]}")
			try:
				convertor.addPrefix(sym, base, exp)
				print(f"Successfully added prefix: {convertor.getPrefixDefinitionStr(sym)}")
			except UC_Common.UnitError as err: return print(err)
		else: print(f"Usage: {COMMAND_ADD} prefix {args[2]} <base> <exponent>")
	else: print(usage)

def command_del(args):
	usage = f"Usage: {COMMAND_DEL} <unit|prefix> <symbol>"
	global convertor
	if len(args) != 3: print(usage)
	elif args[1] == "unit":
		sym = args[2]
		try:
			deletedUnits = convertor.delUnit(sym)
			print(f"Successfully deleted unit(s): {deletedUnits}")
		except UC_Common.UnitError as err: return print(err)
	elif args[1] == "prefix":
		sym = args[2]
		try:
			deletedUnits = convertor.delPrefix(sym)
			print(f"Successfully deleted prefix: '{sym}' and units: {deletedUnits}")
		except UC_Common.UnitError as err: return print(err)
	else: print(usage)

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
	COMMAND_EVAL  : (lambda args: command_eval(args)),
	COMMAND_SHOW  : (lambda args: command_show(args)),
	COMMAND_ADD   : (lambda args: command_add(args)),
	COMMAND_DEL   : (lambda args: command_del(args)),
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