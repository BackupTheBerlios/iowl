  
__version__ = "$Revision: 1.1 $"

"""
$Log: cClick.py,v $
Revision 1.1  2001/03/24 19:22:34  i10614
Initial revision

Revision 1.6  2001/02/22 21:53:17  a
bug fixes for supporting history list

Revision 1.5  2001/02/21 18:32:05  a
added has_url method

Revision 1.4  2001/02/20 20:33:19  a
added Get* methods

Revision 1.3  2001/02/20 17:36:19  a
supporting different clickstream files

Revision 1.2  2001/02/19 19:31:20  a
minor changes

Revision 1.1  2001/02/19 17:46:20  a
added cClick class


"""

import urlparse
import string
import cDOM


class cClick:

    """Click class.

    Internal representation of a click. Convert DOM to
    internal representation, convert internal representation into DOM.

    """

    def __init__(self):
        """Constructor."""
        self.sContentType = ''
        self.iStatus = 0
        self.iTimestamp = 0
        self.sTitle = 'unknown'


    def HasUrl(self, tUrl):
        """Check if url are contained in this click

        tUrl -- url
        return -- true if url in this click

        """
        if tUrl == self.tUrl:
            #self.Print()
            return 1
        else:
            return 0


    def SetClick(self, tUrl, sContentType, iStatus, iTimestamp, sTitle, \
                 tReferer):
        """Set click.

        tUrl -- url to be added in urlparse notation
        sContentType -- MIME type
        iStatus -- http status
        iTimestamp -- date of browsing seconds since 1970
        sTitle -- title of html page
        tReferer -- http referer

        """
        self.tUrl = tUrl
        self.sContentType = sContentType
        self.iStatus = iStatus
        self.iTimestamp = iTimestamp
        self.sTitle = sTitle
        self.tReferer = tReferer


    def GetTitle(self):
        """Return title as string

        return -- sTitle

        """
        return self.sTitle


    def GetTimestamp(self):
        """Return timestamp in time() notation.

        return -- iTimestamp

        """
        return self.iTimestamp


    def GetUrl(self):
        """Return url of this click

        return -- tUrl

        """
        return self.tUrl


    def GetElement(self):
        """Return Element for storing in a DOM.

        return -- contEls, container element.

        """
        foo = cDOM.cDOM()
        
        dAttrs = {}
        dAttrs['content_type'] = self.sContentType
        dAttrs['status'] = str(self.iStatus)
        dAttrs['timestamp'] = str(self.iTimestamp)
        dAttrs['title'] = self.sTitle
        dAttrs['referer'] = urlparse.urlunparse(self.tReferer)

        sUrl = urlparse.urlunparse(self.tUrl)
        el = foo.CreateElement('click', dAttrs, sUrl)

        return el


    def SetElement(self, el):
        """Read element into internal representation.

        el -- element
        
        <click content_type="text/html" referer="http://harth.org/" status="200" timestamp="11:49:34" title="das ist eine html seite">http://slashdot.org/</click></session>

        """
        foo = cDOM.cDOM()

        sName, dAttrs, sUrl = foo.GetElementContent \
                              (el, ['content_type','referer', \
                                    'status','timestamp','title'])
        # only one url
        self.tUrl = urlparse.urlparse(sUrl)
        self.sTitle = dAttrs['title']
        self.sContentType = dAttrs['content_type']        
        self.iStatus = string.atoi(dAttrs['status'])
        self.iTimestamp = string.atof(dAttrs['timestamp'])
        self.tReferer = urlparse.urlparse(dAttrs['referer'])


    def Print(self):
        """Print out content."""
        print "Click--------------"
        print self.tUrl
        print self.sContentType
        print self.iStatus
        print self.iTimestamp
        print self.tReferer
