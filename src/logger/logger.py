import copy
from colorama import Fore, Back, Style
from datetime import datetime

class LogLevel:
	name: str
	value: int
	funcName: str
	defaultFore: str = Fore.WHITE
	levelColor: str = ""
	colorLevel: bool = True
	tagColor: str = Fore.LIGHTMAGENTA_EX
	colorTags: bool = True
	msgColor: str = ""
	highlightLine: bool = False
	highlightColor: str = ""

	def __init__(self, name, value, funcName, levelColor, highlightLine, highlightColor):
		self.name = name
		self.value = value
		self.funcName = funcName
		self.levelColor = levelColor
		self.highlightLine = highlightLine
		self.highlightColor = highlightColor

class LogOutput:
	isConsole: bool = True
	useColors: bool = True
	isFile: bool = False
	filePath: str = ""
	fp = None
	minLevel: int = 0

	def __init__(self, isConsole, useColors, isFile, filePath, minLevel):
		self.isConsole = isConsole
		self.useColors = useColors
		self.isFile = isFile
		self.filePath = filePath
		if isFile:
			try:
				self.fp = open(filePath, "a")
			except:
				print("Could not open log file")
		self.minLevel = minLevel
	
	def __del__(self):
		if self.fp is not None:
			try:
				self.fp.write("#############################################################################\n")
				self.fp.close()
			except:
				print("Could not close log file")


class Logger:
	active: bool = True
	showName: bool = True
	name: str = "LOG"
	levels: [LogLevel] = [
		LogLevel("DEBUG", 0, "dbg", "", False, ""),
		LogLevel("INFO", 1, "inf", Fore.GREEN, False, ""),
		LogLevel("WARNNING", 2, "wrn", "", True, Back.YELLOW),
		LogLevel("ERROR", 3, "err", "", True, Back.RED),
		]
	showTags: bool = True
	tags: [str] = []
	useColors: bool = True
	outputs: [LogOutput] = [
		LogOutput(True, True, False, None, 1),
		LogOutput(False, False, True, "log.txt", 0)
	]
	widestLevel: int = 10


	def log(self, level:LogLevel = None, msg:str = None) -> None:
		if level is None or not self.active:
			return
		for out in self.outputs:
			if level.value < out.minLevel:
				continue
			useColors = self.useColors and out.useColors
			line = ""
			if useColors:
				line += level.defaultFore
			if useColors and level.highlightLine:
				line += level.highlightColor
			line += self.name + ": "
			line += str(datetime.now()) + "| "
			if useColors and level.colorLevel:
				line += level.levelColor
			line += f"{level.name:<{self.widestLevel+2}}: "
			if useColors:
				line += level.defaultFore
			if useColors and level.colorTags:
				line += level.tagColor
			for t in self.tags:
				line += t + ": "
			if useColors:
				line += level.defaultFore
			line += msg
			if useColors:
				line += Style.RESET_ALL

			if out.isConsole:
				print(line)
			if out.isFile:
				out.fp.write(line+"\n")

	def createLogLevelFunc(self, level:LogLevel):
		def new_logger(msg:str):
			self.log(level, msg)
		
		setattr(self, level.funcName, new_logger)
	
	def registerFuncs(self) -> None:
		for level in self.levels:
			self.createLogLevelFunc(level)

	def __init__(self, name:str=None):
		if name is not None:
			self.name = name
		self.registerFuncs()

		# Get the width of the longest level name
		self.widestLevel = 0
		for level in self.levels:
			if len(level.name) > self.widestLevel:
				self.widestLevel = len(level.name)

		

	def addTag(self, tag):
		d = copy.copy(self)
		d.tags = []
		d.tags.append(tag)
		d.registerFuncs()
		return d



# MARK: Testing function (Main)
if __name__ == '__main__':
	log = Logger()
	log.dbg("message 1")
	log.inf("message 2")

	log2 = log.addTag("function")
	log2.wrn("This is a warning with tags")
	log.err("This is an error")

	log.tags.append("Why")
	log2.inf("This should not have why tag")

	log.log(log.levels[2], "This is a test")
	print(Back.RED + Fore.WHITE + "This is a message"+Style.RESET_ALL)