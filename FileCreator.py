## FileCreator.py
# This is the base class for the boilerplate creators

import json

class FileCreator(object):

	## Load the JSON file, create the output file and set up the headers
	# @param _fileName The JSON file to load
	def __init__(self, _fileName):
		# Open the JSON file
		fileIn = open(_fileName, "r")
		self.m_jsonFile = json.load(fileIn)
		fileIn.close()
		# Get the output file path and name
		fPath = self.getFromJSON("filePath", "string")
		fName = self.getFromJSON("fileName", "string")
		fDescription = self.getFromJSON("fileDescription", "string")
		fOut = fPath + "/" + fName + ".py"
		# Create the output file
		self.m_fOut = file(fOut, "w")
		# Add file description
		self.writeLine("## " + fName + ".py")
		self.writeLine("# " + fDescription)
		self.writeLine()
		# Add imports
		self.writeLine("import sys\nimport maya.api.OpenMaya as om")
		self.writeLine()


	## Get a variable from the JSON file
	# @param _variableName The name of the variable in the JSON file
	# @param _type The type of the variable
	# @return The typecasted value of the variable
	def getFromJSON(self, _variableName, _type):
		# Get the value from the JSON file
		value = self.m_jsonFile.get(_variableName)
		# Typecast the variable
		if (_type == "string"):
			value = str(value)
		elif (_type == "float"):
			value == float(value)
		elif (_type == "bool"):
			value = bool(value)
		elif (_type == "array"):
			return value
		return value

	## Write a line to the output file
	# By default this writes an empty line
	# @param _text The text to write
	# @param _indent The indentation for the line as a number of tabs
	def writeLine(self, _text = "", _indent = 0):
		self.m_fOut.write("\t"*_indent + _text + "\n")
