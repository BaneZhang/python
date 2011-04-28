#!/usr/bin/env python3

import io
import sys

sys.stdout = io.StringIO()

print("An error message", file=sys.stdout)
sys.stdout.write("Another error message\n")
print("Nothing has been printed on the console", file=sys.stdout)

error_strings = sys.stdout.getvalue()
sys.stdout = sys.__stdout__
print(error_strings)
