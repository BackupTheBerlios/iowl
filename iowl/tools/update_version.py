import re
import time

file = open("iowl/pManagement/pManager.py", "r")

str = file.read()
file.close()

newver = "$DATE " + time.asctime() + "$"

prog = re.compile("\$DATE.*\$")
newstr = prog.sub(newver, str)

file2 = open("iowl/pManagement/pManager.py", "w")
file2.write(newstr)
file2.flush()
file2.close()
