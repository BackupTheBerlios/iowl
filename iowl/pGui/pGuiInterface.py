__version__ = "$Revision: 1.3 $"

"""
$Log: pGuiInterface.py,v $
Revision 1.3  2001/08/10 18:42:50  i10614
added debuglevel to all messages.

Revision 1.2  2001/03/27 18:23:11  i10614
added session creation date to history

Revision 1.1.1.1  2001/03/24 19:22:54  i10614
Initial import to stio1 from my cvs-tree

Revision 1.2  2001/02/22 14:47:44  mbauer
new Gui-look implemented

Revision 1.1  2001/02/20 17:34:59  mbauer
initital release



"""

import cGuiRequestHandler
import pManager

class pGuiInterface:
    """Interface for package pGui"""


    def __init__(self):
        """Constructor"""

        # create requesthandler
        self.cGuiRequestHandler = cGuiRequestHandler.cGuiRequestHandler()
        pass


    def SetParam(self, sOption, sValue):
        """Accept settings

        Pass setparam-call to cGuiRequestHandler

        """

        self.cGuiRequestHandler.SetParam(sOption, sValue)


    def Start(self):
        """Start working

        pGui does not need any initialization...

        """
        return


    def Shutdown(self):
        """Stop working

        pGui does not need any shutdown activity...

        """

        pManager.manager.DebugStr('pGui '+ __version__ +': Shutting down.', 1)
        return


    def AcceptCommand(self, sUrl):
        """take command from pProxy

        sUrl    -- complete url containing command

        return  -- html code with answer
                   String containing content-type of answer

        """

        # pass on to cGuiRequestHandler
        return self.cGuiRequestHandler.AcceptCommand(sUrl)



