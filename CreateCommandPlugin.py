## CreatePlugin.py

import json

## Class to create Maya plugin files
class PluginFileCreator(object):

	## Constructor
	def __init__(self):
		self.initFile()
		self.writeClass()
		self.writeInitialisation()
		self.m_fOut.close()

	## Write a line to the file
	# By default it writes an empty line
	# @param _line The text to write in a line
	# @param _indent The number of indents to use
	def writeLine(self, _line = "", _indent = 0):
		if (_line == ""):
			self.m_fOut.write("\n")
		else:
			self.m_fOut.write("\t"*_indent + _line + "\n")

	## Get the variable from the JSON file
	# @param _variableName The name of the variable in the file
	# @param _type The type of the variable
	# @return The value of the variable from the JSON file
	def getFromJSON(self, _variableName, _type = "str"):
		# Get the value from the JSON file
		value = self.m_jsonFile.get(_variableName)
		# Typecast the variable
		if (_type == "str"):
			value = str(value)
		elif (_type == "bool"):
			value = bool(value)
		elif (_type == "array"):
			return value
		# Return the value
		return value

	## This function loads the JSON file and then create the python file
	def initFile(self):
		# Open the JSON file
		fIn = open("CommandPluginData.json", "r")
		self.m_jsonFile = json.load(fIn)
		fIn.close()
		# Get the output file path, name and type
		fPath = self.getFromJSON("filePath")
		fName = self.getFromJSON("fileName")
		fDescription = self.getFromJSON("fileDescription")
		fOut = fPath + "/" + fName + ".py"
		# Create an output file
		self.m_fOut = file(fOut, "w")
		# Add file imports
		self.writeLine("## " + fName + ".py")
		self.writeLine("# " + fDescription)
		self.writeLine()
		# Add imports
		self.writeLine("import sys\nimport maya.api.OpenMaya as om")
		self.writeLine()

	## Write the function definition
	def writeClass(self):
		# Write a separator for the plugin
		self.writeLine("#----------------------------------------------------------")
		self.writeLine("# Plugin")
		self.writeLine("#----------------------------------------------------------")
		self.writeLine()
		# Get the flags if necessary
		if(self.getFromJSON("hasFlags", "bool")):
			self.writeLine("# Flag details")
			flags = self.getFromJSON("flags", "array")
			# Split an array of dict into separate arrays
			self.shortFlags = []
			self.longFlags = []
			self.flagTypes = []
			# Create a string for the list
			shortNames = "["
			longNames = "["
			flagTypesStr = "["
			for flag in flags:
				# Append to the separate arrays
				self.shortFlags.append(flag["shortName"])
				self.longFlags.append(flag["longName"])
				self.flagTypes.append(flag["type"])
				# Append to the string
				shortNames += "\"" + flag["shortName"] + "\","
				longNames += "\"" + flag["longName"] + "\","
				flagTypesStr += "\"" + flag["type"] + "\","
			shortFlagNames = shortNames[:-1] + "]"
			longFlagNames = longNames[:-1] + "]"
			flagTypesString = flagTypesStr[:-1] + "]"
			self.writeLine("shortFlagNames = " + shortFlagNames)
			self.writeLine("longFlagNames = " + longFlagNames)
			self.writeLine("flagTypes = " + flagTypesString)
			self.writeLine()
		# Write the class definition
		cDescription = self.getFromJSON("classDescription")
		self.writeLine("## " + cDescription)
		cName = self.getFromJSON("className")
		self.writeLine("class " + cName + "(om.MPxCommand):")
		self.writeLine()
		# Write the Constructor
		self.writeLine("## Constructor", 1)
		self.writeLine("def __init__(self):", 1)
		self.writeLine("om.MPxCommand.__init__(self)", 2)
		self.writeLine()
		# Declare the doIt function
		self.writeLine("## The doIt function", 1)
		self.writeLine("def doIt(self, args):", 1)
		# Check if the function is undoable
		if(self.getFromJSON("isUndoable", "bool")):
			# Write the doIt function
			if(self.getFromJSON("hasFlags", "bool")):
				self.writeLine("self.parseArguments(args)", 2)
			self.writeLine("self.redoIt()", 2)
			self.writeLine()
			# Write the redoIt function
			self.writeLine("## The redo function", 1)
			self.writeLine("def redoIt(self):", 1)
			self.writeLine("pass", 2)
			self.writeLine()
			# Write the undoIt function
			self.writeLine("## The undo function", 1)
			self.writeLine("def undoIt(self):", 1)
			self.writeLine("pass", 2)
			self.writeLine()
			# Write the isUndoable function
			self.writeLine("## This function is needed to make the command undoable", 1)
			self.writeLine("def isUndoable(self):", 1)
			self.writeLine("return True", 2)
		else:
			# Write the doIt function
			if(self.getFromJSON("hasFlags", "bool")):
				self.writeLine("self.parseArguments(args)", 2)
			else:
				self.writeLine("pass", 2)
		self.writeLine()
		# Create the parse arguments function
		if(self.getFromJSON("hasFlags", "bool")):
			self.writeLine("## This function is used for parsing arguments")
			self.writeLine("def parseArguments(self, args):", 1)
			self.writeLine("argData = om.MArgParser(self.syntax(), args)", 2)
			self.writeLine("numArgs = len(shortFlags)", 2)
			self.writeLine("for i in range(numArgs):", 2)
			numArgs = len(self.shortFlags)
			for i in range(numArgs):
				typeCheck = self.flagTypes[i][0].upper() + self.flagTypes[i][1:]
				# Check for short flag
				self.writeLine("if argData.isFlagSet(" + self.shortFlags[i] + "):", 3)
				self.writeLine("self." + self.longFlags[i][1:] + "Value = argData.flagArgument" + typeCheck + "(\"" + self.shortFlags[i] + "\")", 4)
				self.writeLine("if argData.isFlagSet(" + self.longFlags[i] + "):", 3)
				self.writeLine("self." + self.longFlags[i][1:] + "Value = argData.flagArgument" + typeCheck + "(\"" + self.longFlags[i] + "\")", 4)
			self.writeLine()

	## Write the plugin initialisation functions
	def writeInitialisation(self):
		# Write a separator for the plugin initialisation
		self.writeLine("#----------------------------------------------------------")
		self.writeLine("# Plugin Initialisation")
		self.writeLine("#----------------------------------------------------------")
		self.writeLine()
		# Function to use API 2.0
		self.writeLine("## This function tells Maya to use the Python API 2.0")
		self.writeLine("def maya_useNewAPI():")
		self.writeLine("pass", 1)
		self.writeLine("")
		# cmds creator function
		self.writeLine("## Create an instance of the command")
		self.writeLine("def cmdCreator():")
		cName = self.getFromJSON("className")
		self.writeLine("return " + cName + "()", 1)
		self.writeLine()
		# Syntax creator function
		if(self.getFromJSON("hasFlags", "bool")):
			self.writeLine("## This defines argument and flag syntax for the command")
			self.writeLine("def syntaxCreator():")
			self.writeLine("syntax = om.MSyntax()", 1)
			numFlags = len(self.shortFlags)
			for i in range(numFlags):
				# Check the type of variable
				flagType = self.flagTypes[i]
				if (flagType == "int") or (flagType == "float") or (flagType == "double"):
					syntaxType = "kDouble"
				elif (flagType == "bool"):
					syntaxType = "kBoolean"
				elif (flagType == "MAngle"):
					syntaxType = "kAngle"
				elif (flagType == "MDistance"):
					syntaxType = "kDistance"
				elif (flagType == "MTime"):
					syntaxType = "kTime"
				elif (flagType == "string"):
					syntaxType = "kString"
				self.writeLine("syntax.addFlag(shortFlagNames[%i], longFlagNames[%i], om.MSyntax.%s)" % (i, i, syntaxType), 1)
			self.writeLine("return syntax", 1)
		self.writeLine()
		# write the plugin name
		self.writeLine("# The name of the command")
		kPluginCmdName = self.getFromJSON("functionName")
		self.writeLine("kPluginCmdName = " + "\"" + kPluginCmdName + "\"")
		self.writeLine()
		# Write the function for initializePlugin
		self.writeLine("## Initialise the plugin when Maya loads it")
		self.writeLine("def initializePlugin(mobject):")
		self.writeLine("mplugin = om.MFnPlugin(mobject)", 1)
		self.writeLine("try:", 1)
		if(self.getFromJSON("hasFlags", "bool")):
			self.writeLine("mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)", 2)
		else:
			self.writeLine("mplugin.registerCommand(kPluginCmdName, cmdCreator)", 2)
		self.writeLine("except:", 1)
		self.writeLine("sys.stderr.write(\"Failed to register command: \" + kPluginCmdName)", 2)
		self.writeLine()
		# Write the function for uninitializePlugin
		self.writeLine("## Uninitialise the plugin when Maya unloads it")
		self.writeLine("def uninitializePlugin(mobject):")
		self.writeLine("mplugin = om.MFnPlugin(mobject)", 1)
		self.writeLine("try:", 1)
		self.writeLine("mplugin.deregisterCommand(kPluginCmdName)", 2)
		self.writeLine("except:", 1)
		self.writeLine("sys.stderr.write(\"Failed to unregister command: \" + kPluginCmdName)", 2)

## Main
PluginFileCreator()
