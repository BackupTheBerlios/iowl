
__version__ = "$Revision: 1.11 $"

"""
$Log: pAssocRulesInterface.py,v $
Revision 1.11  2002/01/30 17:52:50  aharth
fixed bug #105

Revision 1.10  2002/01/25 15:19:35  aharth
fixed typo in cDOM that caused error message in pAssocRulesInterface

Revision 1.9  2002/01/25 13:19:31  aharth
added itemsets stuff

Revision 1.8  2002/01/24 14:32:59  aharth
Computation of rules should be much faster

Revision 1.7  2001/08/10 18:30:11  i10614
added debuglevel to all messages.

Revision 1.6  2001/04/15 21:16:21  i10614
fixed for recommendations and answers

Revision 1.5  2001/04/15 20:14:06  i10614
minor changes

Revision 1.4  2001/04/14 15:02:29  i10614
minor change

Revision 1.3  2001/04/07 17:06:23  i10614
many, many bugfixes for working network communication

Revision 1.2  2001/03/27 18:19:34  i10614
added notification when shutting down

Revision 1.1.1.1  2001/03/24 19:22:53  i10614
Initial import to stio1 from my cvs-tree

Revision 1.5  2001/03/18 18:32:45  mbauer
Added try-except for ComputeRules-Thread. Errors now get logged, too.

Revision 1.4  2001/02/21 16:02:37  a
test rules generation

Revision 1.3  2001/02/21 14:33:09  a
major improvements

Revision 1.2  2001/02/20 20:55:03  a
added Start, Shutdown methods

Revision 1.1  2001/02/20 20:42:30  a
added pAssocRulesInterface


"""

import cAssociationRules
import pManager
import thread
import sys
import traceback

class pAssocRulesInterface:

    def __init__(self):
        """Constructor."""
        self.AssocRules = cAssociationRules.cAssociationRules()
        self.bGotRules = 0
        self.sItemsetPathName='data/itemsets/'

    def Start(self):
        """Kind of constructor."""
        csi = pManager.manager.GetClickstreamInterface()
        lSessions = csi.GetSessions()
        iCount = csi.GetItemCount()

        pManager.manager.DebugStr('pAssocRulesInterface '+ __version__ +': Starting new thread to compute rules.', 3)
        thread.start_new(self.ComputeRules, (lSessions, iCount))


    def SetParam(self, sParameter, sValue):
        """Get config from pManagement.

        sParameter -- key
        sValue -- value

        """
        if (sParameter == 'itemsetpathname'):
            self.sItemsetPathName = sValue


    def Shutdown(self):
        """Kind of destructor."""
        pManager.manager.DebugStr('pAssocRulesInterface '+ __version__ +': Shutting down.', 1)


    def ComputeRules(self, lSessions, iCount):
        """Compute association rules.

        lSessions -- list of sessions
        iCount -- overall count of urls in clickstream

        """
        self.AssocRules.ComputeRules(lSessions, iCount, self.sItemsetPathName)
        pManager.manager.DebugStr('pAssocRulesInterface '+ __version__ +': Finished Computing Rules.', 3)
        self.bGotRules = 1


    def GotRules(self):
        """true if we finished computing rules"""
        return self.bGotRules



####################################################################
## TEST FUNCTIONS ##################################################

def test():
    pass

if __name__ == '__main__':
    test()

