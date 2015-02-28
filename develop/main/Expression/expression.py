import re
import sys
from sets import Set

class Concept(object):
	varMatchPattern = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
	_traverseLevel = 0
	def __init__(self, var, name, parentConcept = None):
		self.conceptIdx = -1
		self.var = var
		self.name = name
		self.relations = {}
		self.relationLabel = []
		self.relationLabelIdx = []
		self.relationLabelIsReentrance = []
		self.parent = parentConcept
		self.conceptTable = {}
		self.isInversed = False
	
	def setConceptIdx(self, conceptIdx):
		if self.conceptIdx != -1:
			raise Exception("Concept ID has been setted multiple times: %s" % self.name)
		self.conceptIdx = conceptIdx

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
		labelIdx = 0
		if relName in self.relations:
			if isinstance(self.relations[relName], list):
				self.relations[relName].append(addValue)
			else:
				self.relations[relName] = [self.relations[relName], addValue]
			labelIdx = len(self.relations[relName]) - 1
		else:
			self.relations[relName] = addValue

		self.relationLabel.append(relName)
		self.relationLabelIdx.append(labelIdx)
		self.relationLabelIsReentrance.append(False)

		# update root concept table
		if isinstance(addValue, Concept):
			rootConcept = self

			while rootConcept.getParent() != None:
				rootConcept = rootConcept.getParent()

			if addValue.var in rootConcept.conceptTable:
				# already in concept table
				#  -> new concept is still emptyConcept -> just append
				#  -> new concept is not emptyConcept -> update all old emptyConcpet in concept table, update their parent
				if isinstance(addValue, EmptyConcept):
					rootConcept.conceptTable[addValue.var].append(addValue)
					self.relationLabelIsReentrance[-1] = True
				elif isinstance(rootConcept.conceptTable[addValue.var], list):
					for emptyConcept in rootConcept.conceptTable[addValue.var]:
						for tRelName in emptyConcept.getParent().relations:
							if emptyConcept.getParent().relations[tRelName] == emptyConcept:
								emptyConcept.parent.relations[tRelName] = addValue
								addValue.addParent(emptyConcept.parent)
							elif isinstance(emptyConcept.getParent().relations[tRelName], list):
								for (tIdx, ttConcept) in enumerate(emptyConcept.getParent().relations[tRelName]):
									if ttConcept == emptyConcept:
										emptyConcept.getParent().relations[tRelName][tIdx] = addValue
								addValue.addParent(emptyConcept.parent)
					rootConcept.conceptTable[addValue.var] = addValue
				else:

					if rootConcept.conceptTable[addValue.var] != addValue:
						raise Exception("var '" + var + "' duplicated ")
					self.relationLabelIsReentrance[-1] = True

			else:
				if isinstance(addValue, EmptyConcept):
					rootConcept.conceptTable[addValue.var] = [addValue]
					self.relationLabelIsReentrance[-1] = True
				else:
					rootConcept.conceptTable[addValue.var] = addValue


	def searchConceptTable(self, var):
		if self.getParent() != None:
			return self.parent.searchConceptTable(var)

		if var in self.conceptTable:
			return self.conceptTable[var]
	
		return None
	
	@classmethod
	def parse(cls, parsingString, startIdx = 0, parentConcept = None, ParseClass = None):
		if ParseClass == None:
			ParseClass = cls
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

		def assignValue(value):
			if valueStart:
				# add new value to concept table
				if relationName == "":
					raise Exception("format error: %s" % parsingString[startIdx:idx+1])

				if relationName == "mode":
					if (value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"):
						value = value[1:-1]

					if value not in ["imperative", "interrogative", "expressive"]:
						raise Exception("parsing error: the property of mode error: %s" % parsingString[startIdx:idx+1])
					rConcept.addRelation(relationName, Constant(value, rConcept))
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
					rConcept.addRelation(relationName, Constant(value, rConcept))

		while idx < len(parsingString):
			tChar = parsingString[idx]

			if tChar == '"' or tChar == "'" and (not nameStart):
				if valueStart and (not (variableStart or nameStart or relationStart)):
					value += tChar
					if len(value) > 0 and (value[0] == tChar and value[-2] != "\\"):
					
						assignValue(value)
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
						rConcept = ParseClass(variable, name, parentConcept)
					elif relationStart and relationName != "" and (not (variableStart or nameStart or valueStart)):
						relationStart = False
					elif valueStart:
						if len(value) > 0 and value[0] != '"' and value[0] != "'":
							assignValue(value)
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
						rConcept = ParseConcept(variable, name, parentConcept)
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
						assignValue(value)
						valueStart = False
						relationName = ""
						value = ""
				if nameStart:
					assignName()
					nameStart = False
					rConcept = ParseClass(variable, name, parentConcept)

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
					rConcept = ParseClass(variable, name, parentConcept)

				if valueStart:
					if value[0] == '"' and value[-1] == '"':
						assignValue(value)
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

	def getConceptFromIdxList(self, idxList):
		if isinstance(idxList, str):
			idxList = [int(i) for i in idxList.split(".")]

		if len(idxList) == 0:
			raise Exception("Wrong Index List %s" % str(idxList))

		if self.parent == None:
			if len(idxList) == 1:
				if idxList[0] != 0:
					raise Exception("Wrong Index List %s" % str(idxList))
				return self
			else:
				idxList = idxList[1:]

		try:
			currentIdx = idxList[0]
			(relIndex, relLabel, labelIdx, isReentrance) = [t for t in zip(xrange(len(self.relationLabel)), self.relationLabel, self.relationLabelIdx, self.relationLabelIsReentrance) if t[-1] == False][currentIdx]

			nextConcept = None
			if isinstance(self.relations[relLabel], list):
				labelIdx = self.relationLabelIdx[relIndex]
				nextConcept = self.relations[relLabel][labelIdx]
			elif isinstance(self.relations[relLabel], Concept):
				nextConcept = self.relations[relLabel]
			elif isinstance(self.relations[relLabel], Constant):
				nextConcept = self.relations[relLabel]
		#	else:
		#		raise Exception("Item in relation table is neither list nor Concept: %s" % str(self.relations[relLabel]))
		except KeyError:
			raise Exception("Find Concept error in relation: %s" % str(idxList))
		except:
			print self.name
			print currentIdx
			print idxList
			print self.relationLabel
			print self.relationLabelIdx
			exc_info = sys.exc_info()
			raise exc_info[0], exc_info[1], exc_info[2]

		if len(idxList) == 1:
			return nextConcept
		else:
			return nextConcept.getConceptFromIdxList(idxList[1:])

	def traverse(self, callerConcept = None):
		Concept._traverseLevel += 1
		#for relationName in self.relations:



		propagation = None
		subPropagation = None

		if hasattr(self, 'alignedDep'):
			propagation = Set()
			for depNode in self.alignedDep:
				propagation = propagation | Set(depNode.wordSpan)
		for (relIdx, (relationName, labelIdx, isReentrance)) in enumerate(zip(self.relationLabel, self.relationLabelIdx, self.relationLabelIsReentrance)):

			#labelIdx = self.relationLabelIdx[relIdx]
			value = self.relations[relationName][labelIdx] if isinstance(self.relations[relationName], list) else self.relations[relationName]
			
			subPropagation = None
			if hasattr(value, 'alignedDep'):
				subPropagation = Set()
				for depNode in value.alignedDep:
					subPropagation = subPropagation | Set(depNode.wordSpan)

			if isinstance(value, Concept):
				traverseChild = False
				if (not isinstance(value.parent, list)) or (value.parent[0] == self) and (not isReentrance):

					for childValue in value.traverse(self):
						traverseChild = True
						
						(a, childConcept, childReentrance, childPropagation) = childValue
						if subPropagation != None and childPropagation != None and (not isinstance(childConcept.parent, list)) :
							subPropagation = subPropagation | (childPropagation) 
						yield childValue
				else:
					traverseChild = False
				yield (relationName, value, isReentrance, subPropagation)
			elif isinstance(value, Constant):
				yield (relationName, value, False, subPropagation)
			else:
				raise

			if subPropagation != None and propagation != None:
				propagation = propagation | subPropagation
		Concept._traverseLevel -= 1
		if self.parent == None:
			yield (None, self, False, propagation)
		
	def toString(self, callerConcept = None):
		rStr = self.var

		Concept._traverseLevel += 1
		if not isinstance(self.parent, list) or self.parent[0] == callerConcept:
			rStr = "(" + rStr + " / %s" % (self.name)
			
			#for relationName in self.relations:
			for (relIdx, relationName) in enumerate(self.relationLabel):
				labelIdx = self.relationLabelIdx[relIdx]
				value = self.relations[relationName][labelIdx] if isinstance(self.relations[relationName], list) else self.relations[relationName]
				rStr += "\n" + "\t"*Concept._traverseLevel + ":%s " % (relationName)
				if isinstance(value, Concept):
					rStr += value.toString(self)
				elif isinstance(value, Constant):
					rStr += str(value.value)
				else:
					raise
			rStr += ")"
		Concept._traverseLevel -= 1

		return rStr

	def inverseConcept(self):
		print self.conceptTable
			
class EmptyConcept(Concept):
	pass


class Expression(object):
	def __init__(rootConcept, rootConceptList = None):
		self.rootConcept = rootConcept
		if rootConceptList == None:
			self.rootConceptList = [self.rootConcept]
		else:
			self.rootConceptList = self.rootConceptList

	@classmethod
	def parse(cls, parseString):
		parseString = parseString.strip()
		rootConcept = Concept.parse(parseString)
		#rootConcept.casting()
		return cls(rootConcept)
	
class Constant(object):
	def __init__(self, value, parentConcept):
		self.conceptIdx = -1
		self.value = value
		self.parent = parentConcept
	
	def setConceptIdx(self, conceptIdx):
		self.conceptIdx = conceptIdx
