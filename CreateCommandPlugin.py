## CreateCommandPlugin.py
# This file creates boilerplate code for a command plugin

import FileCreator

## Class to create Maya command plugin files
class PluginFileCreator(FileCreator.FileCreator):

	## Constructor
	def __init__(self):
		FileCreator.FileCreator.__init__(self, "CommandPluginData.json")
		self.writePluginDetails()
		self.writeClass()
		self.writeInitialisation()

	## Create a separator for the plugin and then write the plugin details
	def writePluginDetails(self):
		# Write a separator for the plugin
		self.writeLine("#----------------------------------------------------------")
		self.writeLine("# Plugin")
		self.writeLine("#----------------------------------------------------------")
		self.writeLine()
		# write the plugin name
		self.writeLine("# The name of the command")
		kPluginCmdName = self.getFromJSON("functionName", "string")
		self.writeLine("kPluginCmdName = " + "\"" + kPluginCmdName + "\"")
		self.writeLine()
		# Get the flags if necessary
		if(self.getFromJSON("hasFlags", "bool")):
			self.writeLine("# Flag details")
			self.flags = self.getFromJSON("flags", "array")
			# Split an array of dict into separate arrays
			self.shortFlags = []
			self.longFlags = []
			self.flagTypes = []
			self.defaultValues = []
			# Create a string for the list
			shortNames = "["
			longNames = "["
			flagTypesStr = "["
			for flag in self.flags:
				# Append to the separate arrays
				self.shortFlags.append(flag["shortName"])
				self.longFlags.append(flag["longName"])
				self.flagTypes.append(flag["type"])
				self.defaultValues.append(flag["defaultValue"])
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

	## Write the class definition
	def writeClass(self):
		cDescription = self.getFromJSON("classDescription", "string")
		self.writeLine("## " + cDescription)
		cName = self.getFromJSON("className", "string")
		self.writeLine("class " + cName + "(om.MPxCommand):")
		self.writeLine()
		# Write the Constructor
		self.writeLine("## Constructor", 1)
		self.writeLine("def __init__(self):", 1)
		self.writeLine("om.MPxCommand.__init__(self)", 2)
		self.writeLine()
		# Write the DoIt function
		self.writeDoItFunction()
		# Write the parseArguments function
		self.writeParseArgumentsFunction()

	## Write the doIt class function
	def writeDoItFunction(self):
		# Declare the doIt function
		self.writeLine("## The doIt function", 1)
		self.writeLine("def doIt(self, args):", 1)
		# Check if the function is undoable
		if(self.getFromJSON("isUndoable", "bool")):
			# Write the doIt function
			if(self.getFromJSON("hasFlags", "bool")):
				# Define the default values
				self.writeLine("# Initialise the default values", 2)
				for flag in self.flags:
					self.writeLine("self." + flag["longName"][1:] + "Value = " + str(flag["defaultValue"]), 2)
				self.writeLine("# Parse the arguments", 2)
				self.writeLine("self.parseArguments(args)", 2)
			self.writeLine("self.redoIt()", 2)
			self.writeLine()
			self.writeReDoItFunction()
		else:
			# Write the doIt function
			if(self.getFromJSON("hasFlags", "bool")):
				# Define the default values
				self.writeLine("# Initialise the default values", 2)
				for flag in flags:
					self.writeLine("self." + flag["longName"][1:] + "Value = " + str(flag["defaultValue"]), 2)
				self.writeLine("self.parseArguments(args)", 2)
			else:
				self.writeLine("pass", 2)
		self.writeLine()

	## Write the redoIt, undoIt and isUndoable class functions
	def writeReDoItFunction(self):
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

	## Write the parseArguments class function
	def writeParseArgumentsFunction(self):
		if(self.getFromJSON("hasFlags", "bool")):
			self.writeLine("## This function is used for parsing arguments")
			self.writeLine("def parseArguments(self, args):", 1)
			self.writeLine("argData = om.MArgParser(self.syntax(), args)", 2)
			numArgs = len(self.shortFlags)
			for i in range(numArgs):
				typeCheck = self.flagTypes[i][0].upper() + self.flagTypes[i][1:]
				# Check for short flag
				self.writeLine("if argData.isFlagSet(\"" + self.shortFlags[i] + "\"):", 2)
				self.writeLine("self." + self.longFlags[i][1:] + "Value = argData.flagArgument" + typeCheck + "(\"" + self.shortFlags[i] + "\", 0)", 3)
				self.writeLine("if argData.isFlagSet(\"" + self.longFlags[i] + "\"):", 2)
				self.writeLine("self." + self.longFlags[i][1:] + "Value = argData.flagArgument" + typeCheck + "(\"" + self.longFlags[i] + "\", 0)", 3)
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
		cName = self.getFromJSON("className", "string")
		self.writeLine("return " + cName + "()", 1)
		self.writeLine()
		# Write the function syntaxCreator
		self.writeSyntaxCreatorFunction()
		# Write the functions initializePlugin and uninitializePlugin
		self.writeInitialiseUninitialiseFunctions()

	## Write the syntaxCreator function
	def writeSyntaxCreatorFunction(self):
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

	## Write the functions for initializePlugin and uninitializePlugin
	def writeInitialiseUninitialiseFunctions(self):
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
		self.writeLine("raise", 2)
		self.writeLine()
		# Write the function for uninitializePlugin
		self.writeLine("## Uninitialise the plugin when Maya unloads it")
		self.writeLine("def uninitializePlugin(mobject):")
		self.writeLine("mplugin = om.MFnPlugin(mobject)", 1)
		self.writeLine("try:", 1)
		self.writeLine("mplugin.deregisterCommand(kPluginCmdName)", 2)
		self.writeLine("except:", 1)
		self.writeLine("sys.stderr.write(\"Failed to unregister command: \" + kPluginCmdName)", 2)
		self.writeLine("raise", 2)

# Main
PluginFileCreator()
