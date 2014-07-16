import codecs

if __name__ == "__main__":
	amrBankFile = "/home/wtchen/Research/AMR/data/amr-bank-struct-v1.3-training.txt"
	zhSegFile = "alignedSentZHSeg.txt"
		
	fhd = codecs.open(amrBankFile)
	fhd_zh = codecs.open(zhSegFile)
	sourceSent = ""
	targetSent = ""
	fhd_write = codecs.open("alignedSentZH.txt", "w")
	chiSentGener = fhd_zh.xreadlines()

	for line in fhd.xreadlines():
		line = line.strip()
		if line != "" and line[0] == "#":
			#if len(line) > 7 and line[:7] == "# ::zh ":
			#	target = line[7:]
			#	print target
				#fhd_write.write(source + " ||| " + target + "\n")
			#	fhd_write.write(target + "\n")
				
			if len(line) > 8 and line[:8] == "# ::snt ":
				source = line[8:].lower()
				target = chiSentGener.next().strip()
				fhd_write.write(source + " ||| " + target + "\n")

				

	fhd.close()
	fhd_write.close()
