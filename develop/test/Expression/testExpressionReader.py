# -*- coding: utf-8 -*-
import sys
sys.path.append("../../main")

import unittest
from Expression.expressionReader import *

class TestExpressionReader(unittest.TestCase):
	def setUp(self):
		amrSampleFile = "../../../data/amrSample.txt"
		self.reader = ISIReader(amrSampleFile)	

	def testAMRReader(self):
		self.reader.reading()

		self.assertEqual(len(self.reader.amrRepository), 8)
		for amr in self.reader.amrRepository:
			self.assertTrue(amr, isinstance(amr, AMR))

		firstAMR = self.reader.amrRepository[0]

		self.assertEqual(firstAMR.id, "lpp_1943.289")
		self.assertEqual(firstAMR.sent, "Chapter 7 .")
		self.assertEqual(firstAMR.zhSent, "VII。")
		self.assertEqual(firstAMR.expression.name, "chapter")
		self.assertEqual(firstAMR.expression.var, "c")
		self.assertEqual(firstAMR.expression.relations["mod"], "7")

		lastAMR = self.reader.amrRepository[-1]
		self.assertEqual(lastAMR.id, "lpp_1943.296")
		self.assertEqual(lastAMR.sent, '" Then the thorns -- what use are they ? "')
		self.assertEqual(lastAMR.zhSent, "“那么刺有什么用呢？”")
	
if __name__=="__main__":
	unittest.main()
