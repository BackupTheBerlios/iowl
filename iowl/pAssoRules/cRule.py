  
__version__ = "$Revision: 1.1 $"

"""
$Log: cRule.py,v $
Revision 1.1  2001/03/24 19:22:53  i10614
Initial revision

Revision 1.3  2001/03/17 15:19:35  mbauer
removed lots of debug output

Revision 1.2  2001/02/21 16:02:37  a
test rules generation

Revision 1.1  2001/02/19 17:47:53  a
added cRule class


"""

import urlparse
import string
import cDOM


class cRule:

    """Rule class.

    Internal representation of an association rule. Convert DOM to
    internal representation, convert internal representation into DOM.
    There are one consequent and 1..n antecedents. Confidence and support
    for this rule are also stored.

    """

    def __init__(self):
        """Constructor."""
        self.iSupport = 0
        self.iConfidence = 0
        self.antecedents = []


    def GetElement(self):
        """Return element for storing in a DOM."""
        lEls = []

        foo = cDOM.cDOM()

        sUrl = urlparse.urlunparse(self.consequent)
        el = foo.CreateElement('consequent', {}, sUrl)
        lEls.append(el)

        for url in self.antecedents:
            sUrl = urlparse.urlunparse(url)
            el = foo.CreateElement('antecedent', {}, sUrl)
            lEls.append(el)

            sConf = str(self.iConfidence)
            sSupp = str(self.iSupport)

        contEl = foo.CreateElementContainer ('rule', \
                                             {'confidence': sConf,\
                                              'support': sSupp}, lEls)

        return contEl


    def SetElement(self, el):
        """Read element into internal representation.

        el -- element containing rule
        
        """
        foo = cDOM.cDOM()
        
        # get ... in <itemset count="45>...</itemset>
        dAttrs, lContents = foo.GetElementContainerContent \
                            (el, 'rule', ['confidence', 'support'])
        self.iConfidence = string.atoi(dAttrs['confidence'])
        self.iSupport = string.atoi(dAttrs['support'])

        # list with text and attributes
        dNone, lAntecedents = foo.GetElementsContent \
                              (lContents, 'antecedent', None)
        dNone, lConsequent = foo.GetElementsContent \
                             (lContents, 'consequent', None)

        # only one consequent
        #
        # Mike - removed debug output
        #
        # print "************"
        # print lConsequent[0]
        self.consequent = urlparse.urlparse(lConsequent[0])
        for antecedent in lAntecedents:
            # urlparse before converting
            self.antecedents.append(urlparse.urlparse(antecedent))


    def GetRule(self):
        """Return rule."""
        l = []
        l.append(consequent)
        for url in self.antecedents:
            l.append(url)

        return tuple(l), iSupport, iConfidence


    def SetAntecedents(self, lUrls):
        """Set antecedents for rule.

        lUrls -- list of antecedents

        """
        for url in lUrls:
            self.antecedents.append(url)


    def SetConsequent(self, tUrl):
        """Set consequent for rule.

        tUrl -- consquent in urlparse notation

        """
        self.consequent = tUrl


    def GetConsequent(self):
        """Return consequent.

        tUrl -- consquent in urlparse notation

        """
        return self.consequent


    def SetConfidence(self, iConfidence):
        """Set confidence for rule.

        iConfidence -- confidence

        """
        self.iConfidence = iConfidence


    def SetSupport(self, iSupport):
        """Set support for rule.

        iSupport -- support

        """
        self.iSupport = iSupport


    def HasUrls(self, lUrls):
        """Check if lUrls are contained in antecedents

        lUrls -- list of urls
        return -- true if lUrls are subset of antecedents

        """
        list = lUrls[:]

        for url in lUrls:
            if url in self.antecedents:
                i = list.index(url)
                del list[i]

        if len(list) == 0:
            #self.Print()
            return 1
        else:
            return 0


    def Print(self):
        """Print out content."""
        print "Rule--------------"
        print self.consequent
        print self.iSupport
        print self.iConfidence
        for url in self.antecedents:
            print url
