
__version__ = "$Revision: 1.5 $"

"""
$Log: cFile.py,v $
Revision 1.5  2001/08/07 18:52:22  i10614
bugfix by Andi: delete empty sessions from disk

Revision 1.4  2001/07/15 10:22:32  i10614
added bugfix for removing of urls (andi)

Revision 1.3  2001/04/14 15:04:45  i10614
minor fixes

Revision 1.2  2001/03/27 18:26:34  i10614
added GetFileName()

Revision 1.1.1.1  2001/03/24 19:23:04  i10614
Initial import to stio1 from my cvs-tree

Revision 1.20  2001/03/17 15:19:36  mbauer
removed lots of debug output

Revision 1.19  2001/02/19 21:44:18  a
small bugfix in CleanElement

Revision 1.18  2001/02/19 17:47:14  a
added cItemset class

Revision 1.17  2001/02/15 20:42:55  a
bugfixes

Revision 1.16  2001/02/14 20:35:27  a
uncommented pManager

Revision 1.15  2001/02/14 20:29:24  a
don't know really what changed ;-)

Revision 1.14  2001/02/14 17:22:13  a
minor changes

Revision 1.13  2001/02/14 16:42:41  a
move cDOM to pMisc

Revision 1.12  2001/02/14 10:25:36  a
creates file if doesn't exist

Revision 1.11  2001/02/14 09:48:14  a
now creates file if doesn't exist

Revision 1.10  2001/02/13 18:43:50  a
should work now

Revision 1.9  2001/02/13 15:45:48  a
included cFile into cItemsets and cAssoRules, added cStatistics

Revision 1.8  2001/02/12 23:11:45  a
changed to new naming scheme

Revision 1.7  2001/02/12 21:13:42  a
changed AssoRules

Revision 1.6  2001/02/12 17:49:14  a
mostly documentation changes

Revision 1.5  2001/02/11 17:40:25  a
multiple attributes support

Revision 1.4  2001/02/11 15:19:37  a
now supporting multiple urls

Revision 1.3  2001/02/11 10:48:41  a
added cItemset and cDOM

"""

import sys
import string
import xml.dom.minidom
import cDOM
import time
import pManager
import os


class cFile(cDOM.cDOM):

    """Kind of database in this class.

    This class contains the functions for handling xml files on disk
    and in memory. It manages the document object model (dom). You can
    load/save the dom from/to disk, append and delete elements and
    search through the dom.

    """

    def __init__(self, sRootElementName, sVersion):
        """Constructor.

        sRootElementName -- name of root element
        sVersion -- version string

        """
        cDOM.cDOM.__init__(self)
        self.sRootElementName = sRootElementName
        self.sVersion = sVersion

        self.sFileName = ''
        #self.pm = pm


    def GetFileName(self):
        """return string containing filename"""
        return self.sFileName


    def Open(self, sFileName):
        """Load xml file into dom.

        sFileName -- file name of xml file

        """
        self.sFileName = sFileName

        # XXX check version and rootElementFileName
        try:
            file = open(self.sFileName, 'r')
            # now read file and parse into dom
            self.Parse(file)
            return 1
        # if can't open then create file
        except IOError:
            self.CleanElements()
            return 0


    def Save(self):
        """Save dom document to xml file on disk."""
        self.SaveAs(self.sFileName)


    def SaveAs(self, sFileName):
        """Save dom document to xml file on disk.

        sFileName -- new filename

        """
        file = open(sFileName, 'w')
        file.write(self.ToXML())
        file.close()


    def Print(self):
        """Output elements of dom in xml."""
        print('Now printing xml...')
        print(self.ToXML())


    def CleanElements(self):
        """Remove all elements despite root element."""
        # create root element
        el = self.CreateElement(self.sRootElementName, {'version' : self.sVersion}, '')

        if (self.Document.documentElement):
            self.Document.removeChild(self.Document.documentElement)
            # bug in python 2.0
            # self.Document.documentElement = None

        self.SetRootElement(el)


    def DeleteFile(self):
        try:
            os.remove(self.sFileName)
        # XXX should work without OSError catch
        except OSError:
            pass


####################################################################
## TEST FUNCTIONS ##################################################

def test():
    """Built-in test method for this class."""

    import time
    # build small xml file, save to disk, read from disk...
    file = cFile('demo', '0.1')

    file.Print()

    file.Open('/tmp/foo.xml')

    el = file.CreateElement('foo', {'bla': '0.1'}, 'dat is ein text')
    #ellist = []
    #ellist.append(el)
    #elcont = file.CreateElementContainer('fasel', {}, ellist)

    file.AddElement(el) #(elcont)

    file.Print()

    file.Save()


if __name__ == '__main__':
    #try:
    #pManager.manager = pManager.cManager('/tmp/foo')
    test()
    #except:
    #import sys
    #print 'debug:', sys.exc_type, sys.exc_value
