import re
import sys

# check parameters
if len(sys.argv) != 2:
    print 'USAGE: links.py filename'
    sys.exit()

# open file
filename = sys.argv[1]
print 'Opening file ' + filename
file = open(filename, "r")

# read file to string
str = file.read()

# close file
file.close()

# remove newlines
str = str.replace('\n', '')

# regular expression magic
# ? is not greedy, matching the shortest possible string
# fixme iowl html code uses also ' as "
# I means match lowercase
proghref = re.compile('<a.*?href=[\",\'](.*?)[\",\'].*?>(.*?)</a>', re.IGNORECASE|re.DOTALL)

list = proghref.findall(str)

for m in list:
    url = m[0]
    text = m[1]

    # maybe in text there's a img tag so extract the alt= value
    progalt = re.compile('<img.*?alt=[\",\'](.*?)[\",\'].*?>', re.IGNORECASE|re.DOTALL)
    alt = progalt.findall(text)
    # found image with alt string?
    if len(alt) > 0:
        text = alt[0]

    print text + ': ' + url
