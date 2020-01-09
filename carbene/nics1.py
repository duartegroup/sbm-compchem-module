from __future__ import print_function
import platform

x = []
y = []
z = []

print("\nInput coordinates of heavy atoms in ring:\n")
line = "test"
lc = 0
while not (line == "" and lc > 3):
    if platform.python_version().startswith("2"):
        line = raw_input() # Python 2
    else:
        line = input()     # Python 3
    if line != "":
        x.append(float(line.split()[1]))
        y.append(float(line.split()[2]))
        z.append(float(line.split()[3]))
        lc = lc + 1

print("Add the following line to the coordinate block: ")
print("\n========================================================")
print("  DA    %.10f    %.10f    %.10f" % (sum(x)/lc, sum(y)/lc, sum(z)/lc))
print("========================================================\n")

