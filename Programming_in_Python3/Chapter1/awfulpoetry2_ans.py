#!/usr/bin/env python3


import sys
import random


articles = ["the", "a", "another", "her", "his"]
subjects = ["cat", "dog", "horse", "man", "woman", "boy", "girl"]
verbs = ["sang", "ran", "jumped", "said", "fought", "swam", "saw",
         "heard", "felt", "slept", "hopped", "hoped", "cried",
         "laughed", "walked"]
adverbs = ["loudly", "quietly", "quickly", "slowly", "well", "badly",
           "rudely", "politely"]
sentence=[[articles,subjects,verbs,adverbs],[articles,subjects,verbs]]


lines = 5
if len(sys.argv) > 1:
	try:
		if 1 <= int(sys.argv[1]) <= 10:
			lines = int(sys.argv[1])
	except ValueError as err:
		print(err)


while lines:
	sentense_type = sentence[random.randint(0,1)]
	line = ""
	column = 0
	while column < len(sentense_type):
		line += random.choice(sentense_type[column])
		line += " "
		column += 1
	print(line)
	lines -= 1
