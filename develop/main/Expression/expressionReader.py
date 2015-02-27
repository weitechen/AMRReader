from expression import *
import codecs

class AMR(object):
	def __init__(self):
		self.id = None
		self.sent = None
		self.zhSent = None
		self.expression = None
		self.conceptList = []
		self.alignments = None
		self.tokenized = None

class ISIReader(object):
	"""
	Given AMR expression string, parse to the Expression Object
	"""
	
	def __init__(self, fileName):
		self.fileName = fileName
		self.amrRepository = []

	def reading(self):
		amrIdx = 0
		lineIdx = 0
		amrString = ""
		startAMR = False
		with codecs.open(self.fileName) as fhd:
			currentAMR = AMR()
			for line in fhd.xreadlines():
				lineIdx += 1
				if line[0] == "#":
					line = line.strip()
					if line[2:4] == "::":
						terms = line[1:].split(" ::")
						for term in terms:
							separatedTerm = term.strip().split(" ")
							if len(separatedTerm) >= 2:
								if separatedTerm[0] == "id":
									currentAMR.id = separatedTerm[1]
								elif separatedTerm[0] == "snt":
									currentAMR.sent = reduce(lambda x,y: x+ " " + y, separatedTerm[1:])
								elif separatedTerm[0] == "zh":
									currentAMR.zhSent = reduce(lambda x,y: x+ " " + y, separatedTerm[1:])
								elif separatedTerm[0] == "tok":
									currentAMR.tokenized = reduce(lambda x,y: x+ " " + y, separatedTerm[1:])
								elif separatedTerm[0] == "alignments":
									currentAMR.alignments = reduce(lambda x,y: x+ " " + y, separatedTerm[1:]).strip()
					continue
				
				if startAMR and line.strip() == "":
					startAMR = False

					try:
						currentAMR.expression = Expression.parse(amrString.strip())
						# process the conceptList
						conceptIdx = 0
						for (relationName, concept, isReentrance, propatation) in currentAMR.expression.traverse():
							if isinstance(concept, Constant) or (not isReentrance):
								conceptIdx += 1
								concept.setConceptIdx(conceptIdx)
								currentAMR.conceptList.append(concept)

						self.amrRepository.append(currentAMR)

						currentAMR = AMR()
					except:
						print amrString
						print "%d: Ln:%d" % (lineIdx, amrIdx)
						raise
					amrString = ""
				else:
					startAMR = True
					amrString += line

		print "done"


if __name__=="__main__":
	#reader = ISIReader("/data/home/verbs/student/wech5560/data/amr/Little_Prince/amr-release-proxy.train.aligned")
	reader = ISIReader("/data/home/verbs/student/wech5560/data/LDC2014E41_DEFT_Phase_1_AMR_Annotation_R4/data/unsplit/deft-p1-amr-r4-bolt.txt")

	#reader = ISIReader("/home/verbs/student/wech5560/data/amr/amr-bank.txt")
	reader.reading()

	#print [c for c in reader.amrRepository[0].conceptList]
	for AMR in reader.amrRepository:
		#print AMR.alignments
		#print AMR.tokenized
		#print ""
		print isinstance(AMR.expression, Expression)
		print AMR.expression.__class__
		AMR.expression.inverseConcept()
		break

	print "done"
