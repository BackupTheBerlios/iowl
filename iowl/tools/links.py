import re
import sys
import htmllib
import formatter

class seekUrl(htmllib.HTMLParser):
    def __init__(self):
        self.start = 0
        self.c_data = ''
        self.alist = []
        htmllib.HTMLParser.__init__(self, formatter.NullFormatter())

    def anchor_bgn(self,href,name,type):
        #print "start_a href:", href, "\nname:", name, "\ntype:", type
        self.href = href
        self.c_data = ""

    def anchor_end(self):
        # check wheter anchor has href attribute
        if len(self.href) != 0:
            self.alist.append([self.href, self.c_data])

    def start_title(self, attrs):
        self.c_data = ""

    def end_title(self):
        self.title = self.c_data

    def handle_data(self, data):
        self.c_data = self.c_data+data

    def getTitle(self):
        return self.title
    
    def getLinkList(self):
        return self.alist


# check parameters
if len(sys.argv) != 2:
    print 'USAGE: links.py filename'
    sys.exit()

# open file
filename = sys.argv[1]
print 'Opening file ' + filename
file = open(filename, "r")

parser = seekUrl()

str = file.read()

# strip out newlines and MSDOS chars
str = str.replace('\n', '')
str = str.replace('^M', '')

# feed to parser
parser.feed(str)

linklist = parser.getLinkList()

print parser.getTitle()

for l in linklist:
    url = l[1]
    text = l[0]
    print text + ": " + url
