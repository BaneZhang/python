#!/usr/bin/env python3
s = input("Enter an integer:")
try:
	i = int(s)
	print("valid integer entered:",i)
except ValueError as err:
	print(err)
