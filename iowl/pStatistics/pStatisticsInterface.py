
__version__ = "$Revision: 1.4 $"

"""
$Log: pStatisticsInterface.py,v $
Revision 1.4  2002/02/10 21:39:56  aharth
added showrules feature

Revision 1.3  2002/01/24 09:41:53  Saruman
adapted to new directory-structure

Revision 1.2  2001/04/15 20:14:07  i10614
minor changes

Revision 1.1.1.1  2001/03/24 19:23:05  i10614
Initial import to stio1 from my cvs-tree

Revision 1.10  2001/02/22 12:30:32  a
minor changes

Revision 1.8  2001/02/21 18:29:14  a
itemsets and rules are now generated dynamically

Revision 1.7  2001/02/21 16:03:16  a
minor changes

Revision 1.6  2001/02/21 14:29:53  a
added methods needed by pAssocRules

Revision 1.5  2001/02/20 17:37:54  a
itemset modifications for AssocRules

Revision 1.4  2001/02/15 21:14:40  a
minor improvements

Revision 1.3  2001/02/14 17:22:13  a
minor changes

Revision 1.2  2001/02/14 10:25:37  a
creates file if doesn't exist

Revision 1.1  2001/02/13 19:01:38  a
changed pStatistics in pStatisticsInterface

Revision 1.1  2001/02/13 18:43:51  a
should work now

Revision 1.1  2001/02/13 15:45:48  a
included cFile into cItemsets and cAssoRules, added cStatistics


"""

import cRules
import cItemsets
import urlparse

class pStatisticsInterface:

    """Core statistics class.
    
    Storing itemsets as well as association rules. The computation of
    association rules are conducted in pAssocRules. This class manages the
    itemsets and rules in memory and on disk as xml files.

    """

    def __init__(self):
        """Constructor."""
        self.sItemsetsFileName = 'data/itemsets.xml'
        self.sRulesFileName = 'data/assorules.xml'
        # store only candidate one itemsets in a file
        self.Itemsets = cItemsets.cItemsets(1)
        self.Rules = cRules.cRules()


    def Start(self):
        """Kind of constructor."""
        # we don't save Itemsets and Rules any more
        #self.Itemsets.OpenFile(self.sItemsetsFileName)
        #self.Rules.OpenFile(self.sRulesFileName)
        pass


    def SetParam(self, sParameter, sValue):
        """Get config from pManagement.

        sParameter -- key
        sValue -- value

        """
        if (sParameter == 'itemsetsfilename'):
            self.sItemsetsFileName = sValue
        elif (sParameter == 'assorulesfilename'):
            self.sRulesFileName = sValue


    def Shutdown(self):
        """Kind of destructor."""
        #self.Rules.CloseFile()
        #self.Itemsets.CloseFile()
        pass


    def DeleteURL(self, sUrl):
        """Delete URL in itemsets and in assorules.

        sUrl -- url
        
        """
        tUrl = urlparse.urlparse(sUrl)
        self.Itemsets.DeleteURL(tURL)
        self.Rules.DeleteURL(tURL)


    def GetMatches(self, lUrls):
        """Get rules that match sUrl.

        lUrls -- list of urls to get recommendations for

        """
        return self.Rules.GetMatches(lUrls)


    def GetRules(self):
        """Get all rules.

        return -- lRules, list with rules
        """
        return self.Rules
    

    def GetTopNList(self, n):
        """Return top n list.

        return -- lUrls, top list of browsed urls

        """
        

    def AddRule(self, rule):
        """Add rule.

        rule -- rule to add.

        """
        self.Rules.AddRule(rule)


def test():
    """Built-in test method for this class."""
    
    stat = pStatisticsInterface()
    stat.SetParam('itemsetsfilename', '/tmp/itemsets.xml')
    stat.SetParam('assorulesfilename', '/tmp/assorules.xml')
    stat.Start()
    stat.Shutdown()


if __name__ == '__main__':
    test()
