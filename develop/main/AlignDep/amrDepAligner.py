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
		self.amrReader = ISIReader(amrFile)
		self.amrReader.reading()

		print len(self.amrReader.amrRepository)

		self.depReader = DepTreeReader(depFile)
		self.depReader.readDepFile()

		print len(self.depreader.depTreeRepository)


if __name__ == "__main__":
	amrDepAligner = AMRDepAligner("../../../data/amr-bank.txt", "../../../data/amrEng.dep")
