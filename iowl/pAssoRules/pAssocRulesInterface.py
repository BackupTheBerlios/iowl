
__version__ = "$Revision: 1.2 $"

"""
$Log: pAssocRulesInterface.py,v $
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


    def Start(self):
        """Kind of constructor."""
        #pManager.manager.SetDebugLevel(1)
        csi = pManager.manager.GetClickstreamInterface()
        lSessions = csi.GetSessions()
        iCount = csi.GetItemCount()

        print 'Now Computing Rules...may take a few minutes.'
        thread.start_new(self.ComputeRules, (lSessions, iCount))


    def SetParam(self, sParameter, sValue):
        """Get config from pManagement.

        sParameter -- key
        sValue -- value

        """
        pass


    def Shutdown(self):
        """Kind of destructor."""

        pManager.manager.DebugStr('pAssocRules '+ __version__ +': Shutting down.')
        pass


    def ComputeRules(self, lSessions, iCount):
        """Compute association rules.

        lSessions -- list of sessions
        iCount -- overall count of urls in clickstream

        """
        try:
            self.AssocRules.ComputeRules(lSessions, iCount)
        except:
            # unknown error. log and forget.
            # get exception
            eType, eValue, eTraceback = sys.exc_info()

            # build stacktrace string
            tb = ''
            for line in traceback.format_tb(eTraceback, 15):
                tb = tb + line

            pManager.manager.DebugStr('pAssocRules '+ __version__ +': Unhandled error in thread ComputeRules: Type: '+str(eType)+', value: '+str(eValue))
            pManager.manager.DebugStr('pAssocRules '+ __version__ +': Traceback:\n'+str(tb))
            pManager.manager.DebugStr('pAssocRules '+ __version__ +': Trying to continue...')


####################################################################
## TEST FUNCTIONS ##################################################

def test():
    pass

if __name__ == '__main__':
    test()
        
