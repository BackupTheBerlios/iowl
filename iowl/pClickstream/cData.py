
__version__ = "$Revision: 1.3 $"

"""
$Log: cData.py,v $
Revision 1.3  2001/03/27 18:22:12  i10614
Changed Session handling. A new session is created inside AddClick(). Whith
each new Session a new watchdog is registered.
The Watchdog now calls CloseSession() and gets discarded.

Revision 1.2  2001/03/24 19:27:41  i10614
cvs does not like empty dirs while importing. Trying to add manually.

Revision 1.1.1.1  2001/03/24 19:22:32  i10614
Initial import to stio1 from my cvs-tree

Revision 1.5  2001/02/21 14:28:25  a
embedded sessions handling into pClickstreamInterface

Revision 1.4  2001/02/20 17:36:19  a
supporting different clickstream files

Revision 1.3  2001/02/19 17:46:20  a
added cClick class

Revision 1.2  2001/02/15 20:42:36  a
bugfixes

Revision 1.1  2001/02/14 17:31:15  a
added cData


"""

import urlparse
import string
import cDOM
import cFile


class cData:

    """Superclass for storing data in xml on disk.

    Storing data here. This class is responsible for keeping
    the data in memory as well as read/write from/to disk through
    cFile class. cFile returns dom Element classes that are parsed with
    help of the method SetElements. GetElements returns Element classes
    for using with cFile.

    Data is stored in a list.

    """

    def __init__(self, sRootElementName, sVersion):
        """Constructor."""
        self.lData = []
        self.sFileName = ''
        self.file = cFile.cFile(sRootElementName, sVersion)


    def GetFileName(self):
        return self.file.GetFileName()

    def OpenFile(self, sFileName):
        """Open file.

        This opens a file. If an IOError occurs (probably the file doesn't
        exist), then create an empty dom.

        sFileName -- file to open

        """
        # could open document
        if self.file.Open(sFileName) == 1:
            # get elements from file...
            newels = self.file.GetElements()
            # ...and store in internal representation
            self.SetElements(newels)
            # and clean root element
            self.file.CleanElements()
        # else: created new dom


    def CloseFile(self):
        """Save content and close file."""
        # get elements from internal representation...
        els = self.GetElements()
        # ...and save to disk
        for el in els:
            self.file.AddElement(el)

        # don't create empty files
        if len(self.lData) != 0:
            self.file.Save()


    def Print(self):
        """Print content of this class."""
        print 'Now printing content...'
        for date in self.lData:
            date.Print()

        print '...done.'
