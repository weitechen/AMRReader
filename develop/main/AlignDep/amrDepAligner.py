#!/usr/bin/python
import sys
sys.path.append("../../main")
sys.path.append("../../../../SRL/develop/main/")

from Dep.depTreeReader import *
from Expression.expressionReader import *
from alignedDepTreeNode import *
from alignedExpression import *
from sets import Set


class AMRDepAligner(object):
	"""
	Align AMR Node with Dep Node
	"""
	def __init__(self, amrFile, depFile):
		print "Reading AMR File %s..." % amrFile,
		self.amrReader = ISIReader(amrFile)
		self.amrReader.reading()

		print "Reading Dep File %s..." % depFile,
		DepTreeReader.DepTreeNodeCls = AlignedDepTreeNode
		self.depReader = DepTreeReader(depFile)
		self.depReader.readDepFile()
		print "done"

		if len(self.amrReader.amrRepository) != len(self.depReader.depTreeRepository):
			raise Exception("Number of AMR instance and DepTree is not identical")

		self.alignmentCandidate = []

		self.depNodeHasAligned = []
		self.amrHasAligned = []

		self.lexiconProb = {}
		self.labelProb = {}
		self.roleLabelProb = {}
	
	def findAlignmentCandidate(self, amrConcept, depTree, amrHasAligned, depNodeHasAligned):
		for depIdx in depNodeHasAligned:
			depNode = depTree.wordList[depIdx]
			conceptIdx = depNode.alignedConcept[0]
		
		for (relationName, concept, isReentrance, propagation) in amrConcept.expression.traverse():
			currentWordSpan = (reduce(lambda x,y: x | y, [Set(depNode.wordSpan) for depNode in concept.alignedDep])) if len(concept.alignedDep) > 0 else Set()
			currentDepNode = None if len(concept.alignedDep) == 0 else concept.alignedDep[0]
			while( (not (currentWordSpan >= propagation)) and currentDepNode!= None and currentDepNode.parentNode != None): 
				currentDepNode = currentDepNode.parentNode
				currentWordSpan = reduce(lambda x,y: x | y, [Set(depNode.wordSpan) for depNode in (concept.alignedDep + [currentDepNode])])
			if currentDepNode != (None if len(concept.alignedDep) == 0 else concept.alignedDep[0]):
				print "update aligned concept"
				print (relationName, concept.name if isinstance(concept, Concept) else concept.value, propagation, currentWordSpan, currentDepNode.word)
				if len(concept.alignedDep) == 0:
					amrHasAligned.append(concept.conceptIdx)
				concept.alignedDep.append(currentDepNode)

		print [([depNode.word for depNode in concept.alignedDep], concept.name if isinstance(concept, Concept) else concept.value) for concept in amrConcept.conceptList]
		#updateDepIdx = len(depTree.wordList) - 1


		return (amrConcept, depTree, amrHasAligned, depNodeHasAligned)

	def processDefaultAlignment(self):
		"""
		Read the default word level - AMR Alignment, process the AMR and DEP nodes
		"""
		for idx in xrange(len(self.amrReader.amrRepository)):
			amr = self.amrReader.amrRepository[idx]
			depTree = self.depReader.depTreeRepository[idx]

			
			self.alignDefaultTree(amr, depTree)
			self.depReader.depTreeRepository[idx] = depTree


	@staticmethod
	def alignNode(amrConcept, depTreeNode, rootConcept, depTree):
		amrConcept.alignedDep.append(depTreeNode)
		depTreeNode.alignedConcept.append(amrConcept)


	def alignDefaultTree(self, amr, depTree):
		amrExpression = amr.expression
		AlignedConcept.derivedFromConcept(amrExpression)
		#AlignedDepTreeNode.derived(depTree)
		alignment = amr.alignments
		depNodeHasAligned = []
		amrHasAligned = []
		if alignment != None:
			alignTerms = alignment.split(" ")
			for alignTerm in [t.strip() for t in alignTerms if t.strip() != ""]:
				wordIdxStr, amrNodeIdxStr = alignTerm.split("|")
				amrNodes = [amrExpression.getConceptFromIdxList(idxStr) for idxStr in amrNodeIdxStr.split("+")]
	
				wordSpan = [int(i) for i in wordIdxStr.split("-")]
				depNode = depTree.wordList[wordSpan[0]]
	
				if reduce(lambda x,y: y - x, wordSpan) > 1:
					# find parent dep node that covers all the word span
					while depNode.parentNode != None and (depNode.wordSpan[0] > wordSpan[0] or depNode.wordSpan[-1]+1 < wordSpan[1]):
						depNode = depNode.parentNode

				while depNode.parentNode != None and len(depNode.parentNode.childNode) == 1 and isinstance(amrNodes[0], Concept) and len(amrNodes[0].relations) > 0:
					depNode = depNode.parentNode

				AMRDepAligner.alignNode(amrNodes[0], depNode, amr, depTree)
				depNodeHasAligned.append(depNode.wordIdx)
				amrHasAligned.append(amrNodes[0].conceptIdx)

				#[AMRDepAligner.alignNode(amrNode, depNode, amr, depTree) for amrNode in amrNodes]
				
		self.depNodeHasAligned.append(depNodeHasAligned)
		self.amrHasAligned.append(amrHasAligned)

if __name__ == "__main__":
	amrDepAligner = AMRDepAligner("/data/home/verbs/student/wech5560/data/amr/Little_Prince/amr-release-proxy.train.aligned", "/data/home/verbs/student/wech5560/data/amr/Little_Prince/amr-release-proxy.train.dep")
	amrDepAligner.processDefaultAlignment()
	#amrDepAligner.alignDefaultTree(amrDepAligner.amrReader.amrRepository[6], amrDepAligner.depReader.depTreeRepository[6])
#	for idx in xrange(10):
	for idx in xrange(len(amrDepAligner.amrReader.amrRepository)):
		print idx
		if idx < 1:
			continue

		amrConcept = amrDepAligner.amrReader.amrRepository[idx]
		depTree = amrDepAligner.depReader.depTreeRepository[idx]
		amrHasAligned = amrDepAligner.amrHasAligned[idx]
		depNodeHasAligned = amrDepAligner.depNodeHasAligned[idx]

		print "Aligned Node"
		print [depTree.wordList[depIdx].word for depIdx in depNodeHasAligned]

		(amrConcept, depTree, amrHasAligned, depNodeHasAligned) = amrDepAligner.findAlignmentCandidate(amrConcept, depTree ,amrHasAligned ,depNodeHasAligned)
		amrDepAligner.amrReader.amrRepository[idx] = amrConcept 
		amrDepAligner.depReader.depTreeRepository[idx] = depTree
		amrDepAligner.amrHasAligned[idx] = amrHasAligned
		amrDepAligner.depNodeHasAligned[idx] = depNodeHasAligned

		for nonAlignedAmrIdx in list(Set(xrange(1, len(amrConcept.conceptList)+1)) - Set(amrHasAligned) ) :
			nonAlignedConcept = amrConcept.conceptList[nonAlignedAmrIdx - 1]
			if isinstance(nonAlignedConcept, Concept) and len(nonAlignedConcept.relations) > 0 and nonAlignedConcept.parent != None:
				print "non aligned amr"
				print (nonAlignedAmrIdx, nonAlignedConcept.conceptIdx, nonAlignedConcept.name if isinstance(nonAlignedConcept, Concept) else nonAlignedConcept.value)
				bottomNode = None
				for (relIndex, relLabel, labelIdx, isReentrance) in [t for t in zip(xrange(len(nonAlignedConcept.relationLabel)), nonAlignedConcept.relationLabel, nonAlignedConcept.relationLabelIdx, nonAlignedConcept.relationLabelIsReentrance) if t[-1] == False]:
					if isinstance(nonAlignedConcept.relations[relLabel], list):
						labelIdx = self.relationLabelIdx[relIndex]
						childConcept = self.relations[relLabel][labelIdx]
					else:
						childConcept = nonAlignedConcept.relations[relLabel]

					if len(childConcept.alignedDep) > 0:
						if bottomNode == None:
							bottomNode = childConcept.alignedDep[-1]
						else:
							bottomNode = DepTree.findCommonAncestor(childConcept.alignedDep[-1], bottomNode)


				tNonAConcept = nonAlignedConcept.parent
				while tNonAConcept != None and len(tNonAConcept.alignedDep) == 0:
					tNonAConcept = tNonAConcept.parent

				if tNonAConcept == None:
					tNonAConcept = amrConcept.expression

				topNode = tNonAConcept.alignedDep[-1]
				print topNode.word

				if bottomNode == None and topNode == None:
					raise Exception("qq")
					

		break
			
	#amrDepAligner.alignAll()
