
__version__ = "$Revision: 1.1 $"

"""
$Log: cItemsets.py,v $
Revision 1.1  2001/03/24 19:23:05  i10614
Initial revision

Revision 1.13  2001/02/22 12:30:32  a
minor changes

Revision 1.11  2001/02/21 14:29:53  a
added methods needed by pAssocRules

Revision 1.10  2001/02/20 17:37:54  a
itemset modifications for AssocRules

Revision 1.9  2001/02/20 11:10:40  a
changed cAssoRules to cRules

Revision 1.8  2001/02/19 17:47:14  a
added cItemset class

Revision 1.7  2001/02/15 20:42:56  a
bugfixes

Revision 1.6  2001/02/14 17:22:13  a
minor changes

Revision 1.5  2001/02/14 16:42:41  a
move cDOM to pMisc

Revision 1.4  2001/02/14 10:25:37  a
creates file if doesn't exist

Revision 1.3  2001/02/13 18:43:50  a
should work now

Revision 1.2  2001/02/13 15:45:48  a
included cFile into cItemsets and cAssoRules, added cStatistics

Revision 1.1  2001/02/13 14:01:41  a
changed cItemset.py in cItemsets.py

Revision 1.8  2001/02/12 23:11:45  a
changed to new naming scheme

Revision 1.7  2001/02/12 21:50:23  a
AssoRules now works

Revision 1.6  2001/02/12 21:13:42  a
changed AssoRules

Revision 1.5  2001/02/12 17:49:14  a
mostly documentation changes

Revision 1.4  2001/02/11 17:40:25  a
multiple attributes support

Revision 1.3  2001/02/11 15:19:37  a
now supporting multiple urls

Revision 1.2  2001/02/11 13:19:16  a
handling one url per itemset possible

Revision 1.1  2001/02/11 10:48:41  a
added cItemset and cDOM

"""

import urlparse
import string
import cDOM
import cFile
import cData
import cItemset


class cItemsets(cData.cData):

    """Here are the itemsets stored.

    Storing candidate-itemsets here. This class is responsible for keeping
    the Itemsets in memory as well as read/write from/to disk through
    cFile class. cFile returns dom Element classes that are parsed with
    help of the method SetElements. GetElements returns Element classes
    for using with cFile.

    XXX Problems with tab and other whitespaces during parsing

    """

    def __init__(self, iSize):
        """Constructor."""
        # constructor from super class
        cData.cData.__init__(self, 'itemsets', '0.1')
        
        self.isCandidate = 0
        self.iSize = iSize


    def AddItemset(self, itemset):
        """Add itemset to list.

        itemset -- cItemset to be added to list

        """
        if not self.HasItemset(itemset):
            #print "append " + str(itemset.lUrls)
            self.lData.append(itemset)


    def HasItemset(self, itemset):
        """Check wheter itemset already in itemsets.

        lUrls -- list of urls to check

        """
        for i in self.lData:
            if i.IsItemset(itemset):
                return 1

        return 0


    def DeleteURL(self, tUrl):
        """Delete URL from dict.

        tUrl -- url to be deleted in tuple notation

        """
        for key in self.dData.keys():
            for url in key:
                if (url == tUrl):
                    del self.dData[key]


    def Prune(self, iThreshold):
        """Prune URLs.

        iThreshold -- if # of urls < threshold the remove it from dict

        """
        print '*******Before pruning: ' + str(len(self.lData))
        foo = self.lData[:]
        for itemset in foo:
            if itemset.GetCount() < iThreshold:
                index = self.lData.index(itemset)
                del self.lData[index]

        for itemset in self.lData:
            if itemset.GetCount() == 0:
                print "SCHEIIIIIIIIIIIISSSSSSSSSEEEEEE" + str(iThreshold)

        print '*******After pruning: ' + str(len(self.lData))

        self.isCandidate = 1


    def GetElements(self):
        """Return Elements for storing in a DOM.

        return -- lContEls, all elements covering all itemsets

        """
        lEls = []
        
        for itemset in self.lData:
            el = itemset.GetElement()
            lEls.append(el)

        return lEls


    def SetElements(self, lEls):
        """Read elements into internal representation.

        lEls -- elements

        <itemset count="74">
        <url>http://slashdot.org</url>
        ...
        </itemset>

        """
        for el in lEls:
            itemset = cItemset.cItemset()
            itemset.SetElement(el)
            self.lData.append(itemset)


    def GetSize(self):
        """Return size of this itemsets.

        return -- size

        """
        return self.iSize


    def GetList(self):
        """Return list with n itemset for iteration.

        return -- list with itemset

        """
        return self.lData


    def CountUrl(self, lUrls):
        """Count url to this itemset.

        lUrls -- list of url to check

        """
        for itemset in self.lData:
            # if urls in itemset are subset of urls in lUrls
            if itemset.IsSubset(lUrls):
                itemset.Increment()


####################################################################
## TEST FUNCTIONS ##################################################

def test():
    """Built-in test method for this class."""

    items = cItemsets(2)

    items.OpenFile('/tmp/foo.xml')

    urltuple = urlparse.urlparse('http://slashdot.org')
    urltuple2 = urlparse.urlparse('http://harth.org')

    itemset1 = cItemset.cItemset()
    itemset2 = cItemset.cItemset()

    itemset1.SetUrls([urltuple, urltuple])
    itemset1.SetCount(4711)

    itemset1.SetUrls([urltuple2, urltuple2])
    itemset1.SetCount(4712)

    items.AddItemset(itemset1)
    items.AddItemset(itemset2)

    items.CloseFile()

    items2 = cItemsets(2)

    items2.OpenFile('/tmp/foo.xml')
    items2.Print()
    #XXXprint 'now prune...'
    #items2.Prune(2)
    items2.Print()
    items2.CloseFile()


if __name__ == '__main__':
    #try:
    test()
    #except:
    #import sys
    #print 'debug:', sys.exc_type, sys.exc_value
