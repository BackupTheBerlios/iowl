
__version__ = "$Revision: 1.2 $"

"""
$Log: cRules.py,v $
Revision 1.2  2001/04/15 21:16:22  i10614
fixed for recommendations and answers

Revision 1.1.1.1  2001/03/24 19:23:06  i10614
Initial import to stio1 from my cvs-tree

Revision 1.3  2001/02/21 16:03:16  a
minor changes

Revision 1.2  2001/02/21 14:29:53  a
added methods needed by pAssocRules

Revision 1.1  2001/02/20 18:01:27  a
added cRules.py

Revision 1.11  2001/02/19 17:47:14  a
added cItemset class

Revision 1.10  2001/02/15 20:42:55  a
bugfixes

Revision 1.9  2001/02/14 17:22:13  a
minor changes

Revision 1.8  2001/02/14 16:42:41  a
move cDOM to pMisc

Revision 1.7  2001/02/14 10:25:36  a
creates file if doesn't exist

Revision 1.6  2001/02/13 18:43:50  a
should work now

Revision 1.5  2001/02/13 15:45:47  a
included cFile into cItemsets and cAssoRules, added cStatistics

Revision 1.4  2001/02/12 23:11:45  a
changed to new naming scheme

Revision 1.3  2001/02/12 21:50:22  a
AssoRules now works

Revision 1.2  2001/02/12 21:13:42  a
changed AssoRules

Revision 1.1  2001/02/12 18:44:09  a
added cAssoRules.py

"""

import urlparse
import string
import cFile
import cData
import cRule
import pManager


class cRules(cData.cData):

    """Store association rules.

    Storing association rules here. This class is responsible for keeping
    the association rules in memory as well as read/write from/to disk through
    cFile class. cFile returns dom Element classes that are parsed with
    help of the method SetElements. GetElements returns Element classes
    for using with cFile.

    """

    def __init__(self):
        """Constructor."""
        # constructor from super class
        cData.cData.__init__(self, 'rules', '0.1')


    def AddRule(self, rule):
        """Add rule to dict.

        rule -- cRule object
        
        """
        self.lData.append(rule)


    def DeleteURL(self, tUrl):
        """Delete URL from dict.
        
        tUrl -- url to be deleted in tuple notation

        """
        for key in self.dData.keys():
            for url in key:
                if (url == tUrl):
                    del self.dData[key]


    def GetMatches(self, lUrls):
        """Get rules that match to urls.

        lUrls -- url to get match for
        return -- lRules, list of rules that apply to this lUrls
        
        """
        lRules = []

        # get pClickstreamInterface
        pAssocRulesInterface = pManager.manager.GetAssocRulesInterface()

        if not pAssocRulesInterface.GotRules():
            # there are no rules...
            return None

        for rule in self.lData:
            if rule.HasUrls(lUrls):
                lRules.append(rule)

        if len(lRules) > 0:
            return lRules
        else:
            return None


    def GetElements(self):
        """Return Elements for storing in a DOM.

        return -- lEls, elements in a list.

        """
        lEls = []

        for rule in self.lData:
            el = rule.GetElement()
            lEls.append(el)

        return lEls


    def SetElements(self, lEls):
        """Read elements into internal representation.

        lEls -- elements
        <rule confidenceCount="74" supportCount="45">
        <antecedent>http://slashdot.org</antecedent>
        ...
        </rule>

        """
        for el in lEls:
            rule = cRule.cRule()
            rule.SetElement(el)
            self.lData.append(rule)


####################################################################
## TEST FUNCTIONS ##################################################

def test():
    """Built-in test method for this class."""

    assos = cRules()

    assos.OpenFile('/tmp/foo.xml')

    urltuple = urlparse.urlparse("http://slashdot.org")
    urltuple2 = urlparse.urlparse("http://harth.org")

    # add urls in tuple notation
    rule = cRule.cRule()
    rule.SetSupport(1)
    rule.SetConfidence(2)
    rule.SetAntecedents([urltuple,urltuple2])
    rule.SetConsequent(urltuple)
    assos.AddRule(rule)

    # add urls in tuple notation
    rule = cRule.cRule()
    rule.SetSupport(1)
    rule.SetConfidence(200)
    rule.SetAntecedents([urltuple2,urltuple2])
    rule.SetConsequent(urltuple2)
    assos.AddRule(rule)

    assos.Print()

    assos.CloseFile()

    assos2 = cRules()

    assos2.OpenFile('/tmp/foo.xml')
    assos2.Print()
    assos2.file.Print()
    assos2.CloseFile()


if __name__ == '__main__':
    #try:
    test()
    #except:
    #import sys
    #print "debug:", sys.exc_type, sys.exc_value
