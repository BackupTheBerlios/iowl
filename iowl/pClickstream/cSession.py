
__version__ = "$Revision: 1.3 $"

"""
$Log: cSession.py,v $
Revision 1.3  2001/03/26 17:48:01  i10614
activated filtering of invalid urls

Revision 1.2  2001/03/24 19:27:41  i10614
cvs does not like empty dirs while importing. Trying to add manually.

Revision 1.1.1.1  2001/03/24 19:22:32  i10614
Initial import to stio1 from my cvs-tree

Revision 1.11  2001/02/22 21:53:18  a
bug fixes for supporting history list

Revision 1.10  2001/02/22 15:12:27  a
added RemoveUrl method

Revision 1.9  2001/02/21 14:28:25  a
embedded sessions handling into pClickstreamInterface

Revision 1.8  2001/02/20 17:36:20  a
supporting different clickstream files

Revision 1.7  2001/02/19 17:46:20  a
added cClick class

Revision 1.6  2001/02/19 11:23:26  a
added AddClick with arguments

Revision 1.5  2001/02/15 20:42:37  a
bugfixes

Revision 1.4  2001/02/14 20:29:23  a
don't know really what changed ;-)

Revision 1.3  2001/02/14 17:22:10  a
minor changes

Revision 1.2  2001/02/14 16:44:41  a
pClickstreamInterface works

Revision 1.1  2001/02/14 16:02:33  a
initial release of pClickstream


"""

import urlparse
import string
import cFile
import cData
import cClick


class cSession(cData.cData):

    """Store one session.

    Storing a session here. This class is responsible for keeping
    the session in memory as well as read/write from/to disk through
    cFile class. cFile returns dom Element classes that are parsed with
    help of the method SetElements. GetElements returns Element classes
    for using with cFile.

    Clicks are stored in a dictionary. Key is an url in tuple
    (urlparse)-notation
    
    Data is also a tuple of a tuple:
    (content_type, status, timestamp, title, referer)
    if one url is browsed twice during a session a new tuple is
    generated

    """

    def __init__(self):
        """Constructor."""
        # constructor from super class
        cData.cData.__init__(self, 'session', '0.1')


    def AddClick(self, click):
        """Add click to list."""

        self.lData.append(click)


    def GetClicks(self):
        """Return list of clicks.

        return -- lData, list of clicks

        """
        return self.lData


    def GetClicksCount(self):
        """Return number of clicks.

        return -- number of clicks

        """
        return len(self.lData)


    def GetUrls(self):
        """Return a list of urls.

        return -- lUrls, list of urls of this session

        """
        lUrls = []
        for click in self.lData:
            tUrl = click.GetUrl()
            lUrls.append(tUrl)

        return lUrls


    def RemoveUrl(self, tUrl):
        """Delete URL from dict.
        
        tUrl -- url to be deleted in urlparse notation

        XXX referer is not deleted! url can survive in referer!

        """
        # for deleting
        foo = self.lData[:]
        for click in foo:
            if click.GetUrl() == tUrl:
                iIndex = self.lData.index(click)
                del self.lData[iIndex]


    def GetElements(self):
        """Return Elements for storing in a DOM.

        return -- lContEls, elements in a list.

        """
        lEls = []

        for click in self.lData:
            el = click.GetElement()
            lEls.append(el)

        return lEls


    def SetElements(self, lEls):
        """Read elements into internal representation.

        lEls -- elements
        
        <click content_type="text/html" referer="http://harth.org/" status="200" timestamp="11:49:34" title="das ist eine html seite">http://slashdot.org/</click></session>

        """
        for el in lEls:
            click = cClick.cClick()
            click.SetElement(el)
            self.lData.append(click)


    def HasItemset(self, itemset):
        """Check whether itemset is in session or not.

        itemset -- itemset to be checked if in session

        """
        lUrls = itemset.GetUrls()

        for click in self.lData:
            tUrl = click.GetUrl()
            if tUrl in lUrls:
                i = lUrls.index(tUrl)
                del lUrls[i]

        if len(lUrls) == 0:
            return 1
        else:
            return 0


####################################################################
## TEST FUNCTIONS ##################################################

def test():
    """Built-in test method for this class."""

    sess = cSession()

    sess.OpenFile('/tmp/foo.xml')

    urltuple = urlparse.urlparse("http://slashdot.org")
    urltuple2 = urlparse.urlparse("http://harth.org")

    click = cClick.cClick()

    click.SetClick(urltuple, 'text/html', '200', '134352234', 'das ist eine html seite', urltuple2)

    click2 = cClick.cClick()

    click2.SetClick(urltuple2, 'text/html', '200', '21312321', 'das ist noch eine html seite', urltuple2)

    sess.AddClick(click)
    sess.AddClick(click2)

    sess.Print()
    #sess.DeleteURL(urltuple2)

    sess.CloseFile()

    sess2 = cSession()

    sess2.OpenFile('/tmp/foo.xml')
    sess2.AddClick(click2)
    sess2.Print()
    sess2.file.Print()
    sess2.CloseFile()


if __name__ == '__main__':
    #try:
    test()
    #except:
    #import sys
    #print "debug:", sys.exc_type, sys.exc_value
