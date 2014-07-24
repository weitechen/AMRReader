#!/usr/bin/python
import sys
sys.path.append("../../main")
sys.path.append("../../../../SRL/develop/main/Dep/")

from depTreeReader import *
from Expression.expressionReader import *

class AMRDepAligner(object):
	"""
	Align AMR Node with Dep Node
	"""
	def __init__(self, amrFile, depFile):
		print "Reading AMR File %s..." % amrFile,
		self.amrReader = ISIReader(amrFile)
		self.amrReader.reading()


		print "Reading Dep File %s..." % depFile,
		self.depReader = DepTreeReader(depFile)
		self.depReader.readDepFile()
		print "done"

		if len(self.amrReader.amrRepository) != len(self.depReader.depTreeRepository):
			raise Exception("Number of AMR instance and DepTree is not identical")
	
	def alignNode(self):
		for idx in xrange(len(self.amrReader.amrRepository)):
			amr = self.amrReader.amrRepository[idx]
			depTree = self.depReader.depTreeRepository[idx]

			
			# Read Alignment

			alignment = amr.alignments
			alignTerms = alignment.split(" ")

			for alignTerm in alignTerms:
				wordIdx, amrNodeIdx = alignTerm.split("|")
				print wordIdx, amrNodeIdx

			if idx >4:
				break

if __name__ == "__main__":
	amrDepAligner = AMRDepAligner("/data/home/verbs/student/wech5560/Source/jamr/data/amr-release-proxy.dev.aligned", "/data/home/verbs/student/wech5560/data/amr/amr-release-proxy.dep")
	amrDepAligner.alignNode()
