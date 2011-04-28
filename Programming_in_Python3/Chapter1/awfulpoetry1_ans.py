#!/usr/bin/env python3


import random


articles = ["the", "a", "another", "her", "his"]
subjects = ["cat", "dog", "horse", "man", "woman", "boy", "girl"]
verbs = ["sang", "ran", "jumped", "said", "fought", "swam", "saw",
         "heard", "felt", "slept", "hopped", "hoped", "cried",
         "laughed", "walked"]
adverbs = ["loudly", "quietly", "quickly", "slowly", "well", "badly",
           "rudely", "politely"]
sentence=[[articles,subjects,verbs,adverbs],[articles,subjects,verbs]]


for _ in [1,2,3,4,5]:
	sentense_type = sentence[random.randint(0,1)]
	line = ""
	column = 0
	while column < len(sentense_type):
		line += random.choice(sentense_type[column])
		line += " "
		column += 1
	print(line)
