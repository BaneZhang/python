#!/usr/bin/env python3



numbers=[]
lowest = None 
highest = None
total=0


while True:
	number = input("enter a number or Enter to finish:")
	if number:
		try:
			numbers.append(number)
			number = int(number)
			if lowest is None or number < lowest:
				lowest = number
			if highest is None or number > highest:
				highest = number
			total += number
		except ValueError as err:
			print(err)
	else:
		break


print("numbers:",numbers)
print("count = ",len(numbers),"sum = ",total,"lowest = ",lowest,"highest = ",highest,"mean = ",total/len(numbers))
