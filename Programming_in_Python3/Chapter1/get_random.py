#!/usr/bin/env python3



#导入random模块默认不行，需要将路径"/usr/lib/python3.1"加shell的PATH变量
import random


print(random.randint(1,6))
print(random.choice(["apple","banana","cherry","durian"]))
