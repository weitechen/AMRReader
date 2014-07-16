import re

class Concept:
	varMatchPattern = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
	def __init__(self, var, name, parentConcept = None):
		self.var = var
		self.name = name
		self.relations = {}
		self.parent = parentConcept
		self.conceptTable = {}
	
	def _setParent(self, parent):
		"""
		Set the parent Concept
		"""
		self.parent = parent

	def addParent(self, parent):
		if not isinstance(self.parent, list):
			self.parent = [self.parent]
		
		self.parent.append(parent)

	def getParent(self, parentIdx = 0):
		if isinstance(self.parent, list):
			return self.parent[parentIdx]
		return self.parent
	
	def addRelation(self, relName, addValue):
		"""
		Add relation (child) Concept or Property
		"""
		if relName in self.relations:
			if isinstance(self.relations[relName], list):
				self.relations[relName].append(addValue)
			else:
				self.relations[relName] = [self.relations[relName], addValue]
			#else:
			#	raise Exception("relation name `" + relName + "' conflict under Concept `" + self.name + "'")
		else:
			self.relations[relName] = addValue

		# update root concept table
		if isinstance(addValue, Concept):
			rootConcept = self
			while rootConcept.getParent() != None:
				rootConcept = rootConcept.getParent()
			if addValue.var in rootConcept.conceptTable:
				if isinstance(addValue, EmptyConcept):
					rootConcept.conceptTable[addValue.var].append(addValue)
				elif isinstance(rootConcept.conceptTable[addValue.var], list):
					for emptyConcept in rootConcept.conceptTable[addValue.var]:
						for tRelName in emptyConcept.getParent().relations:
							if emptyConcept.getParent().relations[tRelName] == emptyConcept:
								emptyConcept.parent.relations[tRelName] = addValue
								addValue.addParent(emptyConcept.parent)
					rootConcept.conceptTable[addValue.var] = addValue
				else:
					if rootConcept.conceptTable[addValue.var] != addValue:
						raise Exception("var '" + var + "' duplicated ")
			else:
				if isinstance(addValue, EmptyConcept):
					rootConcept.conceptTable[addValue.var] = [addValue]
				else:
					rootConcept.conceptTable[addValue.var] = addValue


	def searchConceptTable(self, var):
		if self.getParent() != None:
			return self.parent.searchConceptTable(var)

		if var in self.conceptTable:
			return self.conceptTable[var]
	
		return None
	
	@classmethod
	def parse(cls, parsingString, startIdx = 0, parentConcept = None):
		variable = ""
		name = ""

		idx = startIdx
		conceptStart = False
		conceptComplete = False
		variableStart = False
		nameStart = False
		relationStart = False
		valueStart = False
		relationName = ""
		value = ""
		rConcept = None

		def assignName():
			if nameStart:
				if name == "":
					raise Exception("format error: %s" % parsingString[startIdx:idx+1])
				if variable == "":
					raise Exception("format error: %s" % parsingString[startIdx:idx+1])

		def assignValue():
			if valueStart:
				# add new value to concept table
				if relationName == "":
					raise Exception("format error: %s" % parsingString[startIdx:idx+1])

				if relationName == "mode":
					if value not in ["imperative", "interrogative", "expressive"]:
						raise Exception("parsing error: the property of mode error: %s" % parsingString[startIdx:idx+1])
					rConcept.addRelation(relationName, value)
				elif Concept.varMatchPattern.match(value):
					tConcept = rConcept
					while tConcept.getParent() != None:
						tConcept = tConcept.getParent()
					addedConcept = rConcept.searchConceptTable(value)
					if addedConcept == None or isinstance(addedConcept, list):
						rConcept.addRelation(relationName, EmptyConcept(value, None, rConcept))
					else:
						addedConcept.addParent(rConcept)
						rConcept.addRelation(relationName, addedConcept)
				else:
					# string -> add
					rConcept.addRelation(relationName, value)

				
		while idx < len(parsingString):
			tChar = parsingString[idx]

			if tChar == '"' or tChar == "'" and (not nameStart):
				if valueStart and (not (variableStart or nameStart or relationStart)):
					value += tChar
					if len(value) > 0 and (value[0] == tChar and value[-2] != "\\"):
					
						assignValue()
						valueStart = False
						relationName = ""
						value = ""
				else:
					valueStart = True
					value += tChar
			elif (tChar == " " or tChar == "\r" or tChar == "\n" or tChar == "\t"):
				if conceptStart:
					if variableStart and (not (nameStart or relationStart or valueStart)):
						variableStart = False
					elif nameStart and name != "" and (not (variableStart or relationStart or valueStart)):
						assignName()
						nameStart = False
						rConcept = cls(variable, name, parentConcept)
					elif relationStart and relationName != "" and (not (variableStart or nameStart or valueStart)):
						relationStart = False
					elif valueStart:
						if len(value) > 0 and value[0] != '"' and value[0] != "'":
							assignValue()
							valueStart = False
							relationName = ""
							value = ""
						else:
							value += tChar
						
			elif tChar == "(":
				if conceptStart:
					if nameStart:
						assignName()
						nameStart = False
						rConcept = cls(variable, name, parentConcept)
					if relationStart:
						relationStart = False

					if variable == "" or name == "" or relationName == "":
						raise Exception("format error: %s" % parsingString[startIdx:idx+1])
					if valueStart:
						if value[0] == '"' or value[0] == "'":
							value += tChar
							idx += 1
							continue
						else:
							raise Exception("format error: %s" % parsingString[startIdx:idx+1])

					(childConcept, idx) = Concept.parse(parsingString, idx, rConcept)
					rConcept.addRelation(relationName, childConcept)

					relationName = ""
				else:
					conceptStart = True
					variableStart = True

			elif tChar == ")":
				if valueStart:
					if len(value) > 0 and (value[0] == '"' or value[0] == "'"):
						value += tChar
						idx += 1
						continue
					else:
						assignValue()
						valueStart = False
						relationName = ""
						value = ""
				if nameStart:
					assignName()
					nameStart = False
					rConcept = cls(variable, name, parentConcept)

				if conceptStart == False:
					raise Exception("un-match bracket: %s" % parsingString[startIdx:idx+1] )
				if conceptComplete:
					raise Exception("un-match bracket: %s" % parsingString[startIdx:idx+1] )

				conceptComplete = True
				if rConcept.getParent() == None:
					rConcept.conceptTable[rConcept.var] = rConcept

					for var in rConcept.conceptTable:
						if isinstance(rConcept.conceptTable[var], EmptyConcept) or isinstance(rConcept.conceptTable[var], list):
							raise Exception("could not find var '" + var + "' : %s" % parsingString)
				break
			elif tChar == ":":
				# Start new relation
				if relationStart:
					print (relationStart, relationName)
					raise Exception("un-match relation: %s" % parsingString[startIdx:idx+1])
				elif valueStart and value[0] != '"':
					print (variableStart,  nameStart,  relationStart,  valueStart)
					raise Exception("un-match relation: '%s'" % parsingString[startIdx:idx+1])

				relationStart = True

				if nameStart:
					assignName()
					nameStart = False
					rConcept = cls(variable, name, parentConcept)

				if valueStart:
					if value[0] == '"' and value[-1] == '"':
						assignValue()
						valueStart = False
						relationName = ""
						value = ""
					else:
						value += tChar
						relationStart = False

			elif tChar == "/" and valueStart != True:
				if variable == "":
					raise Exception("format error: %s" % parsingString[startIdx:idx+1])
				if name != "" or relationName != "" or value != "" or nameStart or relationStart or valueStart:
					raise Exception("format error: %s" % parsingString[startIdx:idx+1])
				if Concept.varMatchPattern.match(variable) == None:
					raise Exception("variable format error: %s" % parsingString[startIdx:idx+1])

				variableStart = False

				nameStart = True
			else:
				if variableStart and (not ( nameStart or relationStart or valueStart)):
					variable += tChar
				elif nameStart and (not ( variableStart or relationStart or valueStart)):
					name += tChar
				elif relationStart and (not ( variableStart or nameStart or valueStart)):
					relationName += tChar
				elif valueStart and (not (variableStart or nameStart or relationStart)):
					value += tChar
				elif (not ( variableStart or nameStart or relationStart)):
					value += tChar
					valueStart = True
				else:
					print (variableStart, nameStart,  relationStart ,  valueStart)
					raise Exception("format error: %s" % parsingString[startIdx:idx+1])

			idx += 1

		if variableStart or nameStart or relationStart or valueStart:
			print variableStart
			print nameStart
			print relationStart
			print valueStart
			raise Exception("format error: %s" % parsingString[startIdx:idx+1])

		if (conceptStart or conceptComplete) != True:
			print conceptStart
			print conceptComplete
			raise Exception("format error: %s" % parsingString[startIdx:idx+1])
		
		if idx+1 == len(parsingString):
			if rConcept.getParent() == None:
				return rConcept
			else:
				raise Exception("Parsing error: %s" % parsingString[startIdx:idx])
		else:
			if rConcept.getParent() == None:
				raise Exception("Parsing error: %s" % parsingString[startIdx:idx])
			else:
				return (rConcept, idx)

	def casting(self):
		"""
		Casting a Concept to an Expression object
		"""
		self.__class__ == Expression
	
	def refactorVariable(self):
		"""
		Return the variable mapping table
		"""
		rVars = {self.var: self}
		for relName in self.relations:
			if isinstance(self.relations[relName], Concept):
				childVars = self.relations[relName].refactorVariable()
				tVars = dict(rVars, **childVars)
				if len(tVars) != len(rVars) + len(childVars):
					for interSectionVar in set(childVars.keys()).intersection(rVars.keys()):
						if childVars[interSectionVar] != rVars[interSectionVar]:
							raise Exception("Variable '" + interSectionVar + "' is duplicated")
				rVars = tVars

		return rVars

class EmptyConcept(Concept):
	pass


class Expression(Concept):
	def __init__(self, var, name, parentConcept = None):
		pass
	
	@classmethod
	def parse(cls, parseString):
		parseString = parseString.strip()
		rootConcept = Concept.parse(parseString)
		rootConcept.casting()
		return rootConcept
		
