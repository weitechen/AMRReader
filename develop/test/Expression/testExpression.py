import sys
sys.path.append("../../main")

import unittest
from Expression.expression import *

class TestExpression(unittest.TestCase):
	def setUp(self):
		pass

	def testTraverse(self):
		inputString1 = '(k / name :op1 "Kent")'
		concept1 = Concept.parse(inputString1)
		nodeGenerator = concept1.traverse()
		node0 = nodeGenerator.next()
		self.assertEqual(node0[0], "op1")
		#self.assertTrue(isinstance(node0[1], Constant))
		self.assertEqual(node0[1].value, '"Kent"')
		self.assertEqual(node0[1].parent, concept1)
		self.assertFalse(node0[2])
		node1 = nodeGenerator.next()
		self.assertEqual(node1[0], None)
		self.assertEqual(node1[1].name, "name")
		self.assertFalse(node1[2])
		self.assertRaises(StopIteration, nodeGenerator.next)

		inputString2 = '(h / have-concession-91\
		      :ARG1 (a3 / and\
		            :op1 (d2 / do-02\
		                  :ARG0 p5\
		                  :ARG0 (n / nothing)\
		                  :mod (o2 / only :polarity -))\
		            :op2 (r / respond-01\
		                  :ARG0 p5\
		                  :ARG1 (t4 / thing\
		                        :ARG2-of (q / query-01\
		                              :ARG0 (p4 / public)))\
				))\
		      :ARG2 (d / do-02\
		            :ARG0 (p5 / political-party :name (n2 / name :op1 "CCP"))\
		            ))'

		concept2 = Concept.parse(inputString2)

		nodeGenerator = concept2.traverse()
		node = nodeGenerator.next()
		self.assertEqual(node[0], "ARG0")
		self.assertEqual(node[1].name, "political-party")
		self.assertTrue(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "ARG0")
		self.assertEqual(node[1].name, "nothing")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "polarity")
		self.assertTrue(isinstance(node[1], Constant))
		self.assertEqual(node[1].value, "-")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "mod")
		self.assertEqual(node[1].name, "only")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "op1")
		self.assertEqual(node[1].name, "do-02")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "ARG0")
		self.assertEqual(node[1].name, "political-party")
		self.assertTrue(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "ARG0")
		self.assertEqual(node[1].name, "public")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "ARG2-of")
		self.assertEqual(node[1].name, "query-01")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "ARG1")
		self.assertEqual(node[1].name, "thing")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "op2")
		self.assertEqual(node[1].name, "respond-01")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "ARG1")
		self.assertEqual(node[1].name, "and")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "op1")
		self.assertTrue(isinstance(node[1], Constant))
		self.assertEqual(node[1].value, "\"CCP\"")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "name")
		self.assertEqual(node[1].name, "name")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "ARG0")
		self.assertEqual(node[1].name, "political-party")
		self.assertFalse(node[2])
		node = nodeGenerator.next()
		self.assertEqual(node[0], "ARG2")
		self.assertEqual(node[1].name, "do-02")
		self.assertFalse(node[2])

		node = nodeGenerator.next()
		self.assertEqual(node[0], None)
		self.assertEqual(node[1].name, "have-concession-91")
		self.assertFalse(node[2])
		self.assertRaises(StopIteration, nodeGenerator.next)

	def testToString(self):
		inputString1 = '(k / name :op1 "Kent")'
		concept1 = Concept.parse(inputString1)
		self.assertEqual(inputString1, concept1.toString().replace("\t", "").replace("\n", " "))

		inputString2 = '(h / have-concession-91\
	:ARG1 (a3 / and\
	:op1 (d2 / do-02\
		 :ARG0 p5\
		 :ARG0 (n / nothing)\
		 :mod (o2 / only :polarity -))\
		 :op2 (r / respond-01\
		 :ARG0 p5\
		 :ARG1 (t4 / thing\
		 :ARG2-of (q / query-01\
		 :ARG0 (p4 / public)))\
				))\
		 :ARG2 (d / do-02\
		 :ARG0 (p5 / political-party :name (n2 / name :op1 "CCP"))))'
		concept2 = Concept.parse(inputString2)
		self.assertEqual(inputString2.replace("\t", "").replace("\n", "").replace(" :", ":"), concept2.toString().replace("\t", "").replace("\n", ""))
		
	def testConcept(self):
		concept = Concept("r", "realize-01")
		self.assertEqual(concept.var, "r")
		self.assertEqual(concept.name, "realize-01")
		conceptVar = concept.refactorVariable()
		self.assertEqual(len(conceptVar), 1)
		self.assertEqual(conceptVar["r"], concept)
		self.assertEqual(len(concept.relations), 0)
		self.assertListEqual(concept.relationLabel, [])
		self.assertListEqual(concept.relationLabelIdx, [])

		concept1_1 = Concept("h", "he")
		concept1_2 = Concept("r3", "research-01")

		concept.addRelation("ARG1", concept1_2)
		concept.addRelation("ARG0", concept1_1)
		concept.addRelation("polarity", "-")
		
		self.assertListEqual(concept.relationLabel, ["ARG1", "ARG0", "polarity"])
		self.assertListEqual(concept.relationLabelIdx, [0, 0, 0])
		self.assertTrue("ARG0" in concept.relations)
		self.assertEqual(concept.relations["ARG0"], concept1_1)
		self.assertTrue("ARG1" in concept.relations)
		self.assertEqual(concept.relations["ARG1"], concept1_2)
		self.assertTrue("polarity" in concept.relations)
		self.assertEqual(concept.relations["polarity"], "-")
		self.assertTrue(len(concept.relations), 3)

	def subTestAssert1(self, concept):
		# Test expression "(h / he)"
		self.checkBasicConcept(concept, "h", "he", [], None, ["h"], [], relationLabelIsReentrance = [])
		conceptVar = concept.conceptTable
		self.assertEqual(conceptVar["h"], concept)
		conceptVar = concept.refactorVariable()
		self.assertEqual(len(conceptVar), 1)
		self.assertEqual(conceptVar["h"], concept)

	def subTestAssert2(self, concept):
		# Test expression \(k / name:op1 "Kent")'
		self.checkBasicConcept(concept, "k", "name", ["op1"], None, ["k"], [0], relationLabelIsReentrance = [False])
		self.assertTrue(isinstance(concept.relations["op1"], Constant))
		self.assertEqual(concept.relations["op1"].value, '"Kent"')
		self.assertEqual(concept.relations["op1"].parent, concept)

		conceptVar = concept.conceptTable
		self.assertEqual(conceptVar["k"], concept)
		conceptVar = concept.refactorVariable()
		self.assertEqual(conceptVar["k"], concept)

	def subTestAssert3(self, concept):
		# Test expression
		# (r / realize-01 \
		#	:polarity -\
		#	:ARG0 (h / he))')
		self.checkBasicConcept(concept, "r", "realize-01", ["polarity", "ARG0"], None, ["r", "h"], [0, 0], relationLabelIsReentrance = [False, False])
		self.assertTrue(isinstance(concept.relations["polarity"], Constant))
		self.assertEqual(concept.relations["polarity"].value, "-")
		self.checkBasicConcept(concept.relations["ARG0"], "h", "he", [], concept, relationLabelIdx = [], relationLabelIsReentrance = [])
		conceptVar = concept.conceptTable
		self.assertEqual(conceptVar["r"], concept)
		self.assertEqual(conceptVar["h"], concept.relations["ARG0"])
		conceptVar = concept.refactorVariable()
		self.assertEqual(conceptVar["r"], concept)
		self.assertEqual(conceptVar["h"], concept.relations["ARG0"])

	def subTestAssert4(self, concept):
		# Test expression
		# (s / see-01\
		#  :ARG0 (i / i)\
		#  :ARG1 (p / picture\
		#          :mod (m / magnificent)\
		#          :location (b2 / book\
		#                      :name (n / name\
		#                              :op1 "True"\
		#                              :op2 "Stories"\
		#                              :op3 "from"\
		#                              :op4 "Nature")\
		#                      :topic (f / forest\
		#                               :mod (p2 / primeval))))\
		#  :mod (o / once)\
		#  :time (a / age-01\
		#          :ARG1 i\
		#          :ARG2 (t / temporal-quantity\
		#                  :unit (y / year)\
		#                  :quant 6)))'
		self.checkBasicConcept(concept, "s", "see-01", ["ARG0", "ARG1", "mod", "time"], None, ["s", "i", "p", "m", "b2", "n", "f", "p2", "o", "a", "t", "y"], relationLabelIdx =[0,0,0,0], relationLabelIsReentrance = [False, False, False, False] )
		arg0Concept = concept.relations["ARG0"]
		self.checkBasicConcept(arg0Concept, "i", "i", [], [concept, concept.relations["time"] ], relationLabelIdx = [], relationLabelIsReentrance = [])
		arg1Concept = concept.relations["ARG1"]
		self.checkBasicConcept(arg1Concept, "p", "picture", ["mod", "location"], concept, relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		arg1ModConcept = arg1Concept.relations["mod"]
		self.checkBasicConcept(arg1ModConcept, "m", "magnificent", [], arg1Concept, relationLabelIdx = [], relationLabelIsReentrance = [])
		arg1LocationConcept = arg1Concept.relations["location"]
		self.checkBasicConcept(arg1LocationConcept, "b2", "book", ["name", "topic"], arg1Concept, relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		arg1LocationNameConcept = arg1LocationConcept.relations["name"]
		self.checkBasicConcept(arg1LocationNameConcept, "n", "name", ["op1", "op2", "op3", "op4"], arg1LocationConcept, relationLabelIdx = [0, 0, 0, 0], relationLabelIsReentrance = [False, False, False, False])
		self.assertTrue(isinstance(arg1LocationNameConcept.relations["op1"], Constant))
		self.assertEqual(arg1LocationNameConcept.relations["op1"].value, '"True"')
		self.assertTrue(isinstance(arg1LocationNameConcept.relations["op2"], Constant))
		self.assertEqual(arg1LocationNameConcept.relations["op2"].value, '"Stories"')
		self.assertTrue(isinstance(arg1LocationNameConcept.relations["op3"], Constant))
		self.assertEqual(arg1LocationNameConcept.relations["op3"].value, '"from"')
		self.assertTrue(isinstance(arg1LocationNameConcept.relations["op4"], Constant))
		self.assertEqual(arg1LocationNameConcept.relations["op4"].value, '"Nature"')
		arg1LocationTopicConcept = arg1LocationConcept.relations["topic"]
		self.checkBasicConcept(arg1LocationTopicConcept, "f", "forest", ["mod"], arg1LocationConcept, relationLabelIdx = [0], relationLabelIsReentrance = [False])
		self.checkBasicConcept(arg1LocationTopicConcept.relations["mod"], "p2", "primeval", [], arg1LocationTopicConcept, relationLabelIdx = [], relationLabelIsReentrance = [])
		self.checkBasicConcept(concept.relations["mod"], "o", "once", [], concept, relationLabelIdx = [], relationLabelIsReentrance = [])
		timeConcept = concept.relations["time"]
		self.checkBasicConcept(timeConcept, "a", "age-01", ["ARG1", "ARG2"], concept, relationLabelIdx = [0, 0], relationLabelIsReentrance = [True, False])
		self.assertEqual(timeConcept.relations["ARG1"], arg0Concept)
		timeArg2Concept = timeConcept.relations["ARG2"]
		self.checkBasicConcept(timeArg2Concept, "t", "temporal-quantity", ["unit", "quant"], timeConcept, relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		self.checkBasicConcept(timeArg2Concept.relations["unit"], "y", "year", [], timeArg2Concept, relationLabelIdx = [], relationLabelIsReentrance = [])
		self.assertTrue(isinstance(timeArg2Concept.relations["quant"], Constant))
		self.assertEqual(timeArg2Concept.relations["quant"].value, "6")

		conceptVar = concept.conceptTable
		self.assertEqual(conceptVar["s"], concept)
		self.assertEqual(conceptVar["i"], concept.relations["ARG0"])
		self.assertEqual(conceptVar["p"], concept.relations["ARG1"])
		self.assertEqual(conceptVar["m"], concept.relations["ARG1"].relations["mod"])
		self.assertEqual(conceptVar["b2"], concept.relations["ARG1"].relations["location"])
		self.assertEqual(conceptVar["n"], concept.relations["ARG1"].relations["location"].relations["name"])
		self.assertEqual(conceptVar["f"], concept.relations["ARG1"].relations["location"].relations["topic"])
		self.assertEqual(conceptVar["p2"], concept.relations["ARG1"].relations["location"].relations["topic"].relations["mod"])
		self.assertEqual(conceptVar["o"], concept.relations["mod"])
		self.assertEqual(conceptVar["a"], concept.relations["time"])
		self.assertEqual(conceptVar["i"], concept.relations["time"].relations["ARG1"])
		self.assertEqual(conceptVar["t"], concept.relations["time"].relations["ARG2"])
		self.assertEqual(conceptVar["y"], concept.relations["time"].relations["ARG2"].relations["unit"])
		conceptVar = concept.refactorVariable()
		self.assertEqual(len(conceptVar), 12)
		self.assertEqual(conceptVar["s"], concept)
		self.assertEqual(conceptVar["i"], concept.relations["ARG0"])
		self.assertEqual(conceptVar["p"], concept.relations["ARG1"])
		self.assertEqual(conceptVar["m"], concept.relations["ARG1"].relations["mod"])
		self.assertEqual(conceptVar["b2"], concept.relations["ARG1"].relations["location"])
		self.assertEqual(conceptVar["n"], concept.relations["ARG1"].relations["location"].relations["name"])
		self.assertEqual(conceptVar["f"], concept.relations["ARG1"].relations["location"].relations["topic"])
		self.assertEqual(conceptVar["p2"], concept.relations["ARG1"].relations["location"].relations["topic"].relations["mod"])
		self.assertEqual(conceptVar["o"], concept.relations["mod"])
		self.assertEqual(conceptVar["a"], concept.relations["time"])
		self.assertEqual(conceptVar["i"], concept.relations["time"].relations["ARG1"])
		self.assertEqual(conceptVar["t"], concept.relations["time"].relations["ARG2"])
		self.assertEqual(conceptVar["y"], concept.relations["time"].relations["ARG2"].relations["unit"])

	def subTestAssert5(self, concept):
		# Test Expression "(s2 / say-01\
		#      :ARG0 (b2 / book)\
		#      :ARG1 (s / swallow-01\
		#            :ARG0 (b / boa\
		#                  :mod (c / constrictor))\
		#            :ARG1 (p / prey\
		#                  :poss b)))"
			
		self.checkBasicConcept(concept, "s2", "say-01", ["ARG0", "ARG1"], None, ["s2", "b2", "s", "b", "c", "p"], relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		arg0Concept = concept.relations["ARG0"]
		self.checkBasicConcept(arg0Concept, "b2", "book", [], concept, relationLabelIdx = [], relationLabelIsReentrance = [])
		arg1Concept = concept.relations["ARG1"]
		self.checkBasicConcept(arg1Concept, "s", "swallow-01", ["ARG0", "ARG1"], concept, relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		arg1Arg0Concept = arg1Concept.relations["ARG0"]
		self.checkBasicConcept(arg1Arg0Concept, "b", "boa", ["mod"], [arg1Concept, arg1Concept.relations["ARG1"]], relationLabelIsReentrance = [False])
		self.checkBasicConcept(arg1Arg0Concept.relations["mod"], "c", "constrictor", [], arg1Arg0Concept, relationLabelIdx = [], relationLabelIsReentrance = [])
		arg1Arg1Concept = arg1Concept.relations["ARG1"]
		self.checkBasicConcept(arg1Arg1Concept, "p", "prey", ["poss"], arg1Concept, relationLabelIdx = [0], relationLabelIsReentrance = [True])
		self.assertEqual(arg1Arg1Concept.relations["poss"], arg1Arg0Concept)

		self.assertEqual(concept.conceptTable["s2"], concept)
		self.assertEqual(concept.conceptTable["b2"], arg0Concept)
		self.assertEqual(concept.conceptTable["s"], arg1Concept)
		self.assertEqual(concept.conceptTable["b"], arg1Arg0Concept)
		self.assertEqual(concept.conceptTable["c"], arg1Arg0Concept.relations["mod"])
		self.assertEqual(concept.conceptTable["p"], arg1Arg1Concept)

	def subTestAssert6(self, concept):
		#(c / contrast-01
		#  :ARG2 (a / answer-01
		#         :mode interrogative))')
		self.checkBasicConcept(concept, "c", "contrast-01", ["ARG2"], None, ["c", "a"], relationLabelIdx = [0], relationLabelIsReentrance = [False])
		arg2Concept = concept.relations["ARG2"]
		self.checkBasicConcept(arg2Concept, "a", "answer-01", ["mode"], concept, relationLabelIdx = [0], relationLabelIsReentrance = [False])
		self.assertTrue(arg2Concept.relations["mode"], "interrogative")

		self.assertEqual(concept.conceptTable["c"], concept)
		self.assertEqual(concept.conceptTable["a"], arg2Concept)

	def subTestAssert7(self, concept):
		#(k / know-01\
		#      :ARG0 (e / everybody)\
		#      :time (d / date-entity
		#	     :time "12:00"\
		#            :location (c / country )))'
		self.checkBasicConcept(concept, "k", "know-01", ["ARG0", "time"], None, ["k", "e", "d", "c"], relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		arg0Concept = concept.relations["ARG0"]
		self.checkBasicConcept(arg0Concept, "e", "everybody", [], concept)
		timeConcept = concept.relations["time"]
		self.checkBasicConcept(timeConcept, "d", "date-entity", ["time", "location"], concept, relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		self.assertTrue(isinstance(timeConcept.relations["time"], Constant))
		self.assertEqual(timeConcept.relations["time"].value, '"12:00"')
		self.assertEqual(timeConcept.relations["time"].parent, timeConcept)
		timeLocationConcept = timeConcept.relations["location"]
		self.checkBasicConcept(timeLocationConcept, "c", "country", [], timeConcept, relationLabelIdx = [], relationLabelIsReentrance = [])

	def subTestAssert9(self, concept):
		#(c / candidate\
		#	:mod (p / president :op1 "Republican Party"))')
		self.checkBasicConcept(concept, "c", "candidate", ["mod"], None, ["c", "p"], relationLabelIdx = [0], relationLabelIsReentrance = [False])
		modConcept = concept.relations["mod"]
		self.checkBasicConcept(modConcept, "p", "president", ["op1"], concept, relationLabelIdx = [0], relationLabelIsReentrance = [False])
		self.assertTrue(isinstance(modConcept.relations["op1"], Constant))
		self.assertEqual(modConcept.relations["op1"].value, '"Republican Party"')
		
	def subTestAssert8(self, concept):
		#(k / know-01\
		#	:ARG0 (e / everybody)\
		#	:time (d / date-entity :time "12:00"))')
		self.checkBasicConcept(concept, "k", "know-01", ["ARG0", "time"], None, ["k", "e", "d"], relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		arg0Concept = concept.relations["ARG0"]
		self.checkBasicConcept(arg0Concept, "e", "everybody", [], concept, relationLabelIdx = [], relationLabelIsReentrance = [])
		timeConcept = concept.relations["time"]
		self.checkBasicConcept(timeConcept, "d", "date-entity", ["time"], concept, relationLabelIdx = [0], relationLabelIsReentrance = [False])
		self.assertTrue(isinstance(timeConcept.relations["time"], Constant))
		self.assertEqual(timeConcept.relations["time"].value, '"12:00"')

	def subTestAssert10(self, concept):
		#(d / die-01\
		#      :ARG1 (m / man :quant 28
		#	:quant (m4 / more-than)))
		self.checkBasicConcept(concept, "d", "die-01", ["ARG1"], None, ["d", "m", "m4"], relationLabelIdx = [0], relationLabelIsReentrance = [False])
		arg1Concept = concept.relations["ARG1"]
		self.checkBasicConcept(arg1Concept, "m", "man", ["quant", "quant"], concept, relationLabelIdx = [0, 1], relationLabelIsReentrance = [False, False])
		self.assertTrue(isinstance(arg1Concept.relations["quant"], list))
		self.assertEqual(len(arg1Concept.relations["quant"]), 2)
		self.assertTrue(isinstance(arg1Concept.relations["quant"][0], Constant))
		self.assertEqual(arg1Concept.relations["quant"][0].value, "28")
		quantConcept = arg1Concept.relations["quant"][1]
		self.checkBasicConcept(quantConcept, "m4", "more-than", [], arg1Concept, relationLabelIdx = [], relationLabelIsReentrance = [])

	def subTestAssert11(self, concept):
		#(c / cause-01\
                #	:mod (x / friggin')\
                #	:mod (a / all))

		self.checkBasicConcept(concept, "c", "cause-01", ["mod", "mod"], None, ["c", "x", "a"], relationLabelIdx = [0, 1], relationLabelIsReentrance = [False, False])
		mod0 = concept.relations["mod"][0]
		self.checkBasicConcept(mod0, "x", "friggin'", [], concept, relationLabelIdx = [], relationLabelIsReentrance = [])
		mod1 = concept.relations["mod"][1]
		self.checkBasicConcept(mod1, "a", "all", [], concept, relationLabelIdx = [], relationLabelIsReentrance = [])

	def subTestAssert12(self, concept):
		#(c / consult-01\
		#	:op2 "(SH)")')
		self.checkBasicConcept(concept, "c", "consult-01", ["op2"], None, ["c"], relationLabelIdx = [0], relationLabelIsReentrance = [False])
		self.assertTrue(isinstance(concept.relations["op2"], Constant))
		self.assertEqual(concept.relations["op2"].value, '"(SH)"')
	
	def subTestAssert13(self, concept):
		#(h / have-concession-91\
		#      :ARG1 (a3 / and\
		#            :op1 (d2 / do-02\
		#                  :ARG0 p5\
		#                  :ARG0 (n / nothing)\
		#                  :mod (o2 / only :polarity -))\
		#            :op2 (r / respond-01\
		#                  :ARG0 p5\
		#                  :ARG1 (t4 / thing\
		#                        :ARG2-of (q / query-01\
		#                              :ARG0 (p4 / public)))\
		#		))\
		#      :ARG2 (d / do-02\
		#            :ARG0 (p5 / political-party :name (n2 / name :op1 "CCP"))\
		#            ))
		self.checkBasicConcept(concept, "h", "have-concession-91", ["ARG1", "ARG2"], None, ["h", "a3", "d2", "p5", "n", "o2", "r", "t4", "q", "p4", "d", "n2"], relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])

		arg1Concept = concept.relations["ARG1"]
		self.checkBasicConcept(arg1Concept, "a3", "and", ["op1", "op2"], concept, relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])

		arg1Op1Concept = arg1Concept.relations["op1"]
		self.checkBasicConcept(arg1Op1Concept, "d2", "do-02", ["ARG0", "ARG0", "mod"], arg1Concept, relationLabelIdx = [0, 1, 0], relationLabelIsReentrance = [True, False, False])

		arg1Op2Concept = arg1Concept.relations["op2"]
		self.checkBasicConcept(arg1Op2Concept, "r", "respond-01", ["ARG0", "ARG1"], arg1Concept, relationLabelIdx = [0, 0], relationLabelIsReentrance = [True, False])

		arg2Concept = concept.relations["ARG2"]
		self.checkBasicConcept(arg2Concept, "d", "do-02", ["ARG0"], concept, relationLabelIdx = [0], relationLabelIsReentrance = [False])

		p5concept = concept.conceptTable["p5"]
		self.checkBasicConcept(p5concept, "p5", "political-party", ["name"], [arg1Op1Concept, arg1Op2Concept, arg2Concept], relationLabelIdx = [0], relationLabelIsReentrance = [False])

		self.assertEqual(arg1Concept.relations["op1"].relations["ARG0"][0], p5concept)
		self.assertEqual(arg1Concept.relations["op2"].relations["ARG0"], p5concept)
		self.assertEqual(arg2Concept.relations["ARG0"], p5concept)


	def subTestAssert14(self, concept):
#		(c / contrast-01\
#		  :ARG1 (f / face-01\
#		          :ARG0 (p / person\
#		                  :name (n / name\
#		                          :op1 "Karras"))\
#		          :ARG1 (a / and\
#		                  :op1 (i / imprison-01\
#		                         :ARG1 p\
#		                         :ARG2 (a2 / at-least\
#		                                 :op1 (t / temporal-quantity\
#		                                        :quant 5\
#		                                        :unit (y / year))))\
#		                  :op2 (s / strike-01\
#		                         :ARG2 (c3 / cane)\
#		                         :quant (m / minimum\
#		                                  :op1 5))\
#		                  :condition (c2 / convict-01\
#		                               :ARG1 p)))
#		  :ARG2 (e / escape-01
#		          :ARG0 p
#		          :ARG1 (p4 / penalize-01
#		                  :instrument (d / die-01)
#		                  :mod (m2 / mandatory
#		                         :prep-for (a3 / anyone
#		                                     :ARG1-of (c4 / catch-02
#		                                                :ARG2 (t2 / traffic-00
#		                                                        :ARG1 (c5 / cannabis
#		                                                                :quant (m4 / more-than
#		                                                                         :op1 (m5 / mass-quantity
#		                                                                                :quant 500
#		                                                                                :unit (g2 / gram)))))))))))
		self.checkBasicConcept(concept, "c", "contrast-01", ["ARG1", "ARG2"], None, ["c", "f", "p", "n", "a", "i", "a2", "t", "y", "s", "c3", "m", "c2", "e", "p4", "d", "m2", "a3", "c4", "t2", "c5", "m4", "m5", "g2"], relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		pConcept = concept.conceptTable["p"]
		arg1Concept = concept.conceptTable["f"]
		self.checkBasicConcept(arg1Concept, "f", "face-01", ["ARG0", "ARG1"], concept, [], relationLabelIdx = [0, 0], relationLabelIsReentrance = [False, False])
		self.assertEqual(arg1Concept.relations["ARG0"], pConcept)
		arg1Arg1Op1Concept = concept.conceptTable["i"]
		self.checkBasicConcept(arg1Arg1Op1Concept, "i", "imprison-01", ["ARG1", "ARG2"], concept.conceptTable["a"], [], relationLabelIdx = [0, 0], relationLabelIsReentrance = [True, False])
		self.assertEqual(arg1Arg1Op1Concept.relations["ARG1"], pConcept)
		arg1Arg0Concept = concept.conceptTable["p"]
		self.checkBasicConcept(arg1Arg0Concept, "p", "person", ["name"], [concept.conceptTable["f"], concept.conceptTable["i"], concept.conceptTable["c2"], concept.conceptTable["e"]], [], relationLabelIdx = [0], relationLabelIsReentrance = [False])
		arg1Arg1ConditionConcept = concept.conceptTable["c2"]
		self.checkBasicConcept(arg1Arg1ConditionConcept, "c2", "convict-01", ["ARG1"], concept.conceptTable["a"], [], relationLabelIdx = [0], relationLabelIsReentrance = [True])
		self.assertEqual(arg1Arg1ConditionConcept.relations["ARG1"], pConcept)

		arg1Arg2Concept = concept.conceptTable["e"]
		self.checkBasicConcept(arg1Arg2Concept, "e", "escape-01", ["ARG0", "ARG1"], concept, [], relationLabelIdx = [0, 0], relationLabelIsReentrance = [True, False])
		self.assertEqual(arg1Arg2Concept.relations["ARG0"], pConcept)


	def testConceptParsing(self):
		concept1 = Concept.parse("(h / he)")
		self.subTestAssert1(concept1)

		concept1 = Concept.parse("(h /he)")
		self.subTestAssert1(concept1)

		concept1 = Concept.parse("(h/ he)")
		self.subTestAssert1(concept1)

		concept1 = Concept.parse("(h/he)")
		self.subTestAssert1(concept1)

		concept2 = Concept.parse('(k / name:op1 "Kent")')
		self.subTestAssert2(concept2)

		concept2 = Concept.parse('(k /name:op1 "Kent")')
		self.subTestAssert2(concept2)

		concept3 = Concept.parse('\
(r / realize-01 \
	:polarity -\
	:ARG0 (h / he))')
		self.subTestAssert3(concept3)


		concept3 = Concept.parse('\
(r / realize-01:polarity -\
	:ARG0 (h / he))')
		self.subTestAssert3(concept3)

		concept3 = Concept.parse('\
(r / realize-01     \
	:polarity -\
	:ARG0(h / he))')
		self.subTestAssert3(concept3)

		concept3 = Concept.parse('\
(r / realize-01     \
	:polarity - :ARG0(h/ he))')
		self.subTestAssert3(concept3)

		concept4 = Concept.parse('\
(s / see-01\
  :ARG0 (i / i)\
  :ARG1 (p / picture\
          :mod (m / magnificent)\
          :location (b2 / book\
                      :name (n / name\
                              :op1 "True"\
                              :op2 "Stories"\
                              :op3 "from"\
                              :op4 "Nature")\
                      :topic (f / forest\
                               :mod (p2 / primeval))))\
  :mod (o / once)\
  :time (a / age-01\
          :ARG1 i\
          :ARG2 (t / temporal-quantity\
                  :unit (y / year)\
                  :quant 6)))')

		self.subTestAssert4(concept4)

		concept5 = Concept.parse('(s2 / say-01\
      :ARG0 (b2 / book)\
      :ARG1 (s / swallow-01\
            :ARG0 (b / boa\
                  :mod (c / constrictor))\
            :ARG1 (p / prey\
                  :poss b)))')
		self.subTestAssert5(concept5)

		concept6 = Concept.parse('(c / contrast-01\
  :ARG2 (a / answer-01\
          :mode interrogative))')
		self.subTestAssert6(concept6)

		concept7 = Concept.parse('(k / know-01\
      :ARG0 (e / everybody)\
            :time (d / date-entity :time "12:00"\
                  :location (c / country)))')
		self.subTestAssert7(concept7)

		concept8 = Concept.parse('(k / know-01\
      :ARG0 (e / everybody)\
            :time (d / date-entity :time "12:00"))')
		self.subTestAssert8(concept8)

		concept9 = Concept.parse('(c / candidate\
      :mod (p / president :op1 "Republican Party"))')
		self.subTestAssert9(concept9)

		concept10 = Concept.parse('(d / die-01\
	:ARG1 (m / man :quant 28\
		:quant (m4 / more-than)))')
		self.subTestAssert10(concept10)

		concept11 = Concept.parse("(c / cause-01\
                  :mod (x / friggin')\
                  :mod (a / all))")
		self.subTestAssert11(concept11)

		concept12 = Concept.parse('(c / consult-01\
		 :op2 "(SH)")')
		self.subTestAssert12(concept12)

		concept13 = Concept.parse('(h / have-concession-91\
      :ARG1 (a3 / and\
            :op1 (d2 / do-02\
                  :ARG0 p5\
                  :ARG0 (n / nothing)\
                  :mod (o2 / only :polarity -))\
            :op2 (r / respond-01\
                  :ARG0 p5\
                  :ARG1 (t4 / thing\
                        :ARG2-of (q / query-01\
                              :ARG0 (p4 / public)))\
		))\
      :ARG2 (d / do-02\
            :ARG0 (p5 / political-party :name (n2 / name :op1 "CCP"))\
            ))')
		self.subTestAssert13(concept13)

		concept14 = Concept.parse('(c / contrast-01\
  :ARG1 (f / face-01\
          :ARG0 (p / person\
                  :name (n / name\
                          :op1 "Karras"))\
          :ARG1 (a / and\
                  :op1 (i / imprison-01\
                         :ARG1 p\
                         :ARG2 (a2 / at-least\
                                 :op1 (t / temporal-quantity\
                                        :quant 5\
                                        :unit (y / year))))\
                  :op2 (s / strike-01\
                         :ARG2 (c3 / cane)\
                         :quant (m / minimum\
                                  :op1 5))\
                  :condition (c2 / convict-01\
                               :ARG1 p)))\
  :ARG2 (e / escape-01\
          :ARG0 p\
          :ARG1 (p4 / penalize-01\
                  :instrument (d / die-01)\
                  :mod (m2 / mandatory\
                         :prep-for (a3 / anyone\
                                     :ARG1-of (c4 / catch-02\
                                                :ARG2 (t2 / traffic-00\
                                                        :ARG1 (c5 / cannabis\
                                                                :quant (m4 / more-than\
                                                                         :op1 (m5 / mass-quantity\
                                                                                :quant 500\
                                                                                :unit (g2 / gram)))))))))))')
		self.subTestAssert14(concept14)

	def testGetConceptFromIndexList(self):
		concept = Concept.parse('(h / have-concession-91\
      :ARG1 (a3 / and\
            :op1 (d2 / do-02\
                  :ARG0 p5\
                  :ARG0 (n / nothing)\
                  :mod (o2 / only :polarity -))\
            :op2 (r / respond-01\
                  :ARG0 p5\
                  :ARG1 (t4 / thing\
                        :ARG2-of (q / query-01\
                              :ARG0 (p4 / public)))\
		))\
      :ARG2 (d / do-02\
            :ARG0 (p5 / political-party :name (n2 / name :op1 "CCP"))\
            ))')
		conceptHave = concept.getConceptFromIdxList("0")
		self.assertEqual(conceptHave, concept)

		conceptAnd = concept.getConceptFromIdxList("0.0")
		self.assertEqual(conceptAnd, concept.conceptTable["a3"])
		
		conceptP5 = concept.conceptTable["p5"]
		self.assertEqual(concept.conceptTable["n"], concept.getConceptFromIdxList("0.0.0.0"))
		self.assertEqual(concept.conceptTable["o2"], concept.getConceptFromIdxList("0.0.0.1"))
		self.assertEqual(concept.conceptTable["t4"], concept.getConceptFromIdxList("0.0.1.0"))
		self.assertEqual(conceptP5, concept.getConceptFromIdxList("0.1.0"))
		self.assertEqual(concept.conceptTable["n2"], concept.getConceptFromIdxList("0.1.0.0"))

		self.assertRaises(Exception, concept.getConceptFromIdxList, "1")
		self.assertRaises(Exception, concept.getConceptFromIdxList, "0.2")
		self.assertRaises(Exception, concept.getConceptFromIdxList, "0.1.1")
		self.assertRaises(Exception, concept.getConceptFromIdxList, "0.0.0.2")

	def testErrorConceptParsing(self):
		self.assertRaises(Exception, Concept.parse, "(h / he")
		self.assertRaises(Exception, Concept.parse, "(h / he))")
		self.assertRaises(Exception, Concept.parse, "(h he)")
		self.assertRaises(Exception, Concept.parse, "(h / he) :op \"kent\"")
		self.assertRaises(Exception, Concept.parse, "(h :ARG0( i / i ) )")
		self.assertRaises(Exception, Concept.parse, "(r / realize-01     \
	:polarity -:ARG0(1h/ he))")

		self.assertRaises(Exception, Concept.parse, "(r / realize-01     \
	:polarity -:ARG0 i)")
		self.assertRaises(Exception, Concept.parse, "(s / see-01\
  :ARG0 (i / i)\
  :ARG1 (p / picture\
          :mod (i / anoterh_i)))")
	
	def checkBasicConcept(self, concept, var, name, relationNameList, parent, conceptVarList=[], relationLabelIdx = None, relationLabelIsReentrance=None ):
		self.assertTrue(isinstance(concept, Concept))
		self.assertFalse(isinstance(concept, EmptyConcept))
		self.assertEqual(concept.var, var)
		self.assertEqual(concept.name, name)
		self.assertEqual(sum([ len(concept.relations[relName]) if isinstance(concept.relations[relName], list) else 1 for relName in concept.relations.keys()]), len(relationNameList))
		for relName in relationNameList:
			self.assertTrue(relName in concept.relations)
		self.assertListEqual(concept.relationLabel, relationNameList)
		self.assertEqual(len(concept.conceptTable), len(conceptVarList))
		self.assertListEqual(sorted(concept.conceptTable), sorted(conceptVarList))
		for var in conceptVarList:
			self.assertTrue(var in concept.conceptTable)
			self.assertFalse(isinstance(concept.conceptTable[var], EmptyConcept))

		
		if isinstance(concept.parent, list):
			self.assertListEqual(sorted(concept.parent), sorted(parent))
		else:
			self.assertEqual(concept.parent, parent)

		if relationLabelIdx != None:
			self.assertListEqual(concept.relationLabelIdx, relationLabelIdx)
		if relationLabelIsReentrance != None:
			self.assertListEqual(concept.relationLabelIsReentrance, relationLabelIsReentrance)

if __name__=="__main__":
	unittest.main()
