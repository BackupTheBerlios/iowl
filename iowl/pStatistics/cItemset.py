  
__version__ = "$Revision: 1.1 $"

"""
$Log: cItemset.py,v $
Revision 1.1  2001/03/24 19:23:06  i10614
Initial revision

Revision 1.12  2001/02/21 14:29:53  a
added methods needed by pAssocRules

Revision 1.11  2001/02/20 17:37:54  a
itemset modifications for AssocRules

Revision 1.10  2001/02/19 17:47:14  a
added cItemset class


"""

import urlparse
import string
import cDOM


class cItemset:

    """Itemset class.

    Internal representation of an itemset. Convert DOM to
    internal representation, convert internal representation into DOM.
    Stored are one or more urls and count for that urls.

    <itemset count="2">
    <url>http://harth.org/</url>
    <url>http://slashdot.org/</url>
    </itemset>

    """

    def __init__(self):
        """Constructor."""
        self.iCount = 0
        self.lUrls = []


    def SetElement(self, el):
        """Read element into internal representation.

        el -- element

        <itemset count="74">
        <url>http://slashdot.org</url>
        ...
        </itemset>

        """
        foo = cDOM.cDOM()
        
        # get ... in <itemset count="45">...</itemset>
        dAttrs, lContents = foo.GetElementContainerContent \
                            (el, 'itemset', ['count'])
        iCount = string.atoi(dAttrs['count'])

        # list with text and attributes
        dAttrs, lUrls = foo.GetElementsContent(lContents, 'url', None)

        # Convert list of urls into tuple notation.
        for url in lUrls:
            tUrl = urlparse.urlparse(url)
            self.lUrls.append(tUrl)

        self.SetCount(iCount)


    def GetElement(self):
        """Return Element for storing in a DOM.

        return -- contEl, an element covering all urls

        """
        lEls = []

        foo = cDOM.cDOM()
        
        sCount = str(self.iCount)

        for url in self.lUrls:
            sUrl = urlparse.urlunparse(url)
            el = foo.CreateElement('url', {}, sUrl)
            lEls.append(el)

        contEl = foo.CreateElementContainer \
                 ('itemset', {'count': sCount}, lEls)

        return contEl


    def IsItemset(self, itemset):
        """Check whether itemset is equal this object.

        itemset -- itemset to check

        """
        self.lUrls.sort()
        itemset.lUrls.sort()

        if self.lUrls == itemset.lUrls:
            return 1
        else:
            return 0


    def IsSubset(self, lUrls):
        """Check if urls in itemset are subset of lUrls

        lUrls -- list of urls
        return -- true if urls in itemset are subset of lUrls, false otherwise

        """
        list = self.lUrls[:]

        #print '-----------------'
        #print list
        #print '---'
        #print lUrls
        #print '-----------------------'

        for url in lUrls:
            if url in list:
                i = list.index(url)
                del list[i]

        if len(list) == 0:
            #self.Print()
            return 1
        else:
            return 0


    def Increment(self):
        """Increment count."""
        self.iCount = self.iCount+1


    def SetCount(self, iCount):
        """Set count for itemset.

        iCount -- count of itemset

        """
        self.iCount = iCount


    def GetCount(self):
        """Return occurrence of this itemset.

        return -- iCount, occurence of this itemset

        """
        return self.iCount


    def SetUrls(self, lUrls):
        """Set urls for this itemset.

        lUrls -- list of urls

        """
        self.lUrls = lUrls


    def AddUrl(self, url):
        """Add url to this itemset.

        url -- url in urlparse notation

        """
        self.lUrls.append(url)


    def GetUrls(self):
        """Get urls stored in this itemset.

        return -- list of urls

        """
        return self.lUrls


    def Print(self):
        """Print out content."""
        print "Itemset--------------"
        print self.iCount
        for url in self.lUrls:
            print url
