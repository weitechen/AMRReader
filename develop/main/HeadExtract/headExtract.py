#!/usr/bin/python

import os, sys
sys.path.append("../../main")

from Expression.expressionReader import *
from Expression.expression import *

class HeadExtract(object):
	def __init__(self, expressReader):
		self.reader = expressReader
		self.headRepository = {}
		
	def extract(self):
		
