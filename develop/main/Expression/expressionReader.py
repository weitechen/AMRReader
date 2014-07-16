from expression import *
import codecs

class AMR(object):
	def __init__(self):
		self.id = None
		self.sent = None
		self.zhSent = None
		self.expression = None
		self.alignment = None

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
							separatedTerm = term.split(" ")
							if len(separatedTerm) >= 2:
								if separatedTerm[0] == "id":
									currentAMR.id = separatedTerm[1]
								elif separatedTerm[0] == "snt":
									currentAMR.sent = reduce(lambda x,y: x+ " " + y, separatedTerm[1:])
								elif separatedTerm[0] == "zh":
									currentAMR.zhSent = reduce(lambda x,y: x+ " " + y, separatedTerm[1:])
					continue
				
				if startAMR and line.strip() == "":
					startAMR = False

					try:
						currentAMR.expression = Expression.parse(amrString.strip())
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

	@staticmethod
	def parse(amrSentence):
		expression = Expression()

		return expression

if __name__=="__main__":
	fhd = open("../../../data/amr-bank.txt", "r")
	#fhd = open("/net/data/LDC/AMR_Annotation_Release_1.0_LDC2014T12/amr_anno_1.0/data/unsplit/amr-release-1.0-consensus.txt", "r")
	startAMR = False
	amrString = ""
	idx = 0
	amrIdx = 0
	for line in fhd.xreadlines():
		amrIdx += 1
		if line[0] == "#":
			continue
		if not startAMR and line[0] == "(":
			startAMR = True
			idx += 1

		if startAMR:
			if line.strip() == "":
				startAMR = False
				try:
					expression = Expression.parse(amrString.strip())
				except:
					print amrString
					print "%d: Ln:%d" % (idx, amrIdx)
					raise
				
				amrString = ""
			else:
				amrString += line

	print "done"
