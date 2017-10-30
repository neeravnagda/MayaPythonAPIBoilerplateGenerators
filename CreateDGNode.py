## CreateDGNode.py
# This files creates the boilerplate code for a Dependency Graph Node

import FileCreator

## Class to create Maya DG node plugin files
class DGNodeFileCreator(FileCreator.FileCreator):

	## Constructor
	def __init__(self):
		FileCreator.FileCreator.__init__(self, "DGNodePluginData.json")
		self.writePluginDetails()
		self.writeClass()
		self.writeInitialisation()

	## Create a separator for the plugin and then write the node details
	def writePluginDetails(self):
		# Write a separator for the plugin
		self.writeLine("#----------------------------------------------------------")
		self.writeLine("# Plugin")
		self.writeLine("#----------------------------------------------------------")
		self.writeLine()
		# write the plugin name
		self.writeLine("# Node info")
		kPluginNodeName = self.getFromJSON("nodeName", "string")
		self.writeLine("kPluginNodeName = " + "\"" + kPluginNodeName + "\"")
		kPluginNodeID = self.getFromJSON("nodeID", "string")
		self.writeLine("kPluginNodeID = om.MTypeId(" + kPluginNodeID + ")")
		self.writeLine()
		# write the default attribute values if it is not None, i.e. it is defined
		self.writeLine("# Default attribute values")
		self.inputAttributes = self.getFromJSON("inputAttributes", "array")
		for attr in self.inputAttributes:
			if (attr["defaultValue"] != None):
				variableName = attr["longName"] + "DefaultValue"
				variableValue = attr["defaultValue"]
				self.writeLine(variableName + " = " + str(variableValue))
		self.writeLine()

	## Write the class definition
	def writeClass(self):
		cDescription = self.getFromJSON("classDescription", "string")
		self.writeLine("## " + cDescription)
		cName = self.getFromJSON("className", "string")
		self.writeLine("class " + cName + "(om.MPxNode):")
		self.writeLine("# Define the attributes", 1)
		# Write all the input attributes first with the prefix in
		for attr in self.inputAttributes:
			variableName = "in" + self.capitalise(attr["longName"])
			self.writeLine(variableName + " = om.MObject()", 1)
		# Write all the output attributes with the prefix out
		self.outputAttributes = self.getFromJSON("outputAttributes", "array")
		for attr in self.outputAttributes:
			variableName = "out" + self.capitalise(attr["longName"])
			self.writeLine(variableName + " = om.MObject()", 1)
		self.writeLine()
		# write the init function
		self.writeLine("def __init__(self):", 1)
		self.writeLine("om.MPxNode.__init__(self)", 2)
		self.writeLine()
		# write the compute function
		self.writeComputeFunction()

	## Write the compute class function
	def writeComputeFunction(self):
		# write the comments
		self.writeLine("## The function that is called when the node is dirty", 1)
		self.writeLine("# @param _plug A plug for one of the i/o attributes", 1)
		self.writeLine("# @param _dataBlock The data used for the computations", 1)
		self.writeLine("def compute(self, _plug, _dataBlock):", 1)
		# loop through each output attribute and create an if statement for each one
		className = self.getFromJSON("className", "string")
		for attr in self.outputAttributes:
			self.writeLine("# Check if the plug is the %s attribute" % attr["longName"], 2)
			self.writeLine("if (_plug == " + className + ".out" + self.capitalise(attr["longName"]) + "):", 2)
			# Get the handles for the attributes
			self.writeLine("# Get handles for the attributes", 3)
			# Get the input values
			for dependency in attr["dependencies"]:
				# Check if the dependency is an input attribute
				try:
					d = [x["longName"] for x in self.inputAttributes if (x["longName"] == dependency or x["shortName"] == dependency)][0]
					self.writeLine(d + "DataHandle = _dataBlock.inputValue(" + className + ".in" + self.capitalise(d) + ")", 3)
				except:
					print "Warning: ", dependency, "is not an input attribute."
			self.writeLine(attr["longName"] + "DataHandle = _dataBlock.outputValue(" + className + ".out" + self.capitalise(attr["longName"]) + ")", 3)
			self.writeLine()
			# Extract the values
			self.writeLine("# Get values for the attributes", 3)
			for dependency in attr["dependencies"]:
				# Check if the dependency is an input attribute
				try:
					dName = [x["longName"] for x in self.inputAttributes if (x["longName"] == dependency or x["shortName"] == dependency)][0]
					dType = [x["type"] for x in self.inputAttributes if (x["longName"] == dependency or x["shortName"] == dependency)][0]
					# Check for multiple values, e.g. 2Float, and put the digit at the end of the string
					if dType[0].isdigit():
						dType = dType[1:] + dType[0]
					self.writeLine(dName + "Value = " + dName + "DataHandle.as" + dType + "()", 3)
				except:
					pass
			self.writeLine()
			# Perform the desired computation
			self.writeLine("# Perform the desired computation here", 3)
			self.writeLine("# " + attr["longName"] + "Value =", 3)
			self.writeLine()
			# Set the output value
			self.writeLine("# Set the output value", 3)
			self.writeLine(attr["longName"] + "DataHandle.set" + attr["type"] + "(" + attr["longName"] + "Value)", 3)
			self.writeLine()
			# Mark the output data handle as clean
			self.writeLine("# Mark the output data handle as clean", 3)
			self.writeLine(attr["longName"] + "DataHandle.setClean()", 3)
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
		# node creator function
		self.writeLine("## Create an instance of the node")
		self.writeLine("def nodeCreator():")
		className = self.getFromJSON("className", "string")
		self.writeLine("return " + className + "()", 1)
		self.writeLine()
		# write the nodeInitializer function
		self.writeNodeInitialiser()
		# write the load and unload plugin functions
		self.writeInitialiseUninitialiseFunctions()

	## Write the nodeInitializer function
	def writeNodeInitialiser(self):
		self.writeLine("## Initialise the node attributes")
		self.writeLine("def nodeInitializer():")
		# Decide if a numeric function set or a typed function set is needed or both
		numericFn = False
		typedFn = False
		numericTypes = self.getFromJSON("validNumericTypes", "array")
		nonNumericTypes = self.getFromJSON("validNonNumericTypes", "array")
		for attr in self.inputAttributes + self.outputAttributes:
			if attr["type"] in numericTypes:
				numericFn = True
				break
			if attr["type"] in nonNumericTypes:
				typedFn = True
		# Check if there is a typed function set needed
		if typedFn == False:
			for attr in self.inputAttributes + self.outputAttributes:
				if attr["type"] in nonNumericTypes:
					typedFn = True
					break
		if (numericFn):
			self.writeLine("# Create a numeric attribute function set", 1)
			self.writeLine("mFnNumericAttribute = om.MFnNumericAttribute()", 1)
		if (typedFn):
			self.writeLine("# Create a non-numeric attribute function set", 1)
			self.writeLine("mFnTypedAttribute = om.MFnTypedAttribute()", 1)
		self.writeLine()
		className = self.getFromJSON("className", "string")
		# Write the input attributes
		self.writeLine("# Input node attributes", 1)
		for attr in self.inputAttributes:
			# Check if the attribute is numeric or non-numeric (typed)
			if attr["type"] in numericTypes:
				attrType = ["Numeric", "Numeric"]
			else:
				attrType = ["Typed", ""]
			variableName = className + ".in" + self.capitalise(attr["longName"])
			fnParameters = "\"" + attr["longName"] + "\", \"" + attr["shortName"] + "\", om.MFn" + attrType[1] + "Data.k" + attr["type"]
			if attr["defaultValue"] != None:
				fnParameters += ", " + attr["longName"] + "DefaultValue"
			self.writeLine(variableName + " = mFn" + attrType[0] + "Attribute.create(" + fnParameters  + ")", 1)
			self.writeLine("mFn" + attrType[0] + "Attribute.readable = False", 1)
			self.writeLine("mFn" + attrType[0] + "Attribute.writable = True", 1)
			self.writeLine("mFn" + attrType[0] + "Attribute.storable = True", 1)
			if attr["keyable"]:
				self.writeLine("mFn" + attrType[0] + "Attribute.keyable = True", 1)
			else:
				self.writeLine("mFn" + attrType[0] + "Attribute.keyable = False", 1)
			if attr["minValue"] != None:
				self.writeLine("mFn" + attrType[0] + "Attribute.minValue = " + str(attr["minValue"]), 1)
			if attr["maxValue"] != None:
				self.writeLine("mFn" + attrType[0] + "Attribute.maxValue = " + str(attr["minValue"]), 1)
			self.writeLine()
		# Write the output node attributes
		self.writeLine("# Output node attributes", 1)
		for attr in self.outputAttributes:
			# Check if the attribute is numeric or non-numeric (typed)
			if attr["type"] in numericTypes:
				attrType = ["Numeric", "Numeric"]
			else:
				attrType = ["Typed", ""]
			variableName = className + ".out" + self.capitalise(attr["longName"])
			fnParameters = "\"" + attr["longName"] + "\", \"" + attr["shortName"] + "\", om.MFn" + attrType[1] + "Data.k" + attr["type"]
			self.writeLine(variableName + " = mFn" + attrType[0] + "Attribute.create(" + fnParameters + ")", 1)
			self.writeLine("mFn" + attrType[0] + "Attribute.readable = True", 1)
			self.writeLine("mFn" + attrType[0] + "Attribute.writable = False", 1)
			self.writeLine("mFn" + attrType[0] + "Attribute.storable = False", 1)
			self.writeLine()
		# Add the attributes to the class
		self.writeLine("# Add the attributes to the class", 1)
		for attr in self.inputAttributes:
			self.writeLine(className + ".addAttribute(" + className + ".in" + self.capitalise(attr["longName"]) + ")", 1)
		for attr in self.outputAttributes:
			self.writeLine(className + ".addAttribute(" + className + ".out" + self.capitalise(attr["longName"]) + ")", 1)
		self.writeLine()
		# Write the dependencies
		self.writeLine("# Connect input/output dependencies", 1)
		for attr in self.outputAttributes:
			for dependency in attr["dependencies"]:
				# Check if the dependency is an input attribute
				try:
					d = [x["longName"] for x in self.inputAttributes if (x["longName"] == dependency or x["shortName"] == dependency)][0]
					self.writeLine(className + ".attributeAffects(" + className + ".in" + self.capitalise(d) + ", " + className + ".out" + self.capitalise(attr["longName"]) + ")", 1)
				except:
					pass
		self.writeLine()

	## Write the functions for initializePlugin and uninitializePlugin
	def writeInitialiseUninitialiseFunctions(self):
		# Write the function for initializePlugin
		self.writeLine("## Initialise the plugin when Maya loads it")
		self.writeLine("def initializePlugin(mobject):")
		self.writeLine("mplugin = om.MFnPlugin(mobject)", 1)
		self.writeLine("try:", 1)
		self.writeLine("mplugin.registerNode(kPluginNodeName, kPluginNodeID, nodeCreator, nodeInitializer)", 2)
		self.writeLine("except:", 1)
		self.writeLine("sys.stderr.write(\"Failed to register node: \" + kPluginNodeName)", 2)
		self.writeLine("raise", 2)
		self.writeLine()
		# Write the function for uninitializePlugin
		self.writeLine("## Uninitialise the plugin when Maya unloads it")
		self.writeLine("def uninitializePlugin(mobject):")
		self.writeLine("mplugin = om.MFnPlugin(mobject)", 1)
		self.writeLine("try:", 1)
		self.writeLine("mplugin.deregisterNode(kPluginNodeID)", 2)
		self.writeLine("except:", 1)
		self.writeLine("sys.stderr.write(\"Failed to unregister node: \" + kPluginNodeName)", 2)
		self.writeLine("raise", 2)
		self.writeLine()

# Main
DGNodeFileCreator()
