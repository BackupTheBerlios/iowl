__version__ = "$Revision: 1.1 $"

"""
$Log: pGuiInterface.py,v $
Revision 1.1  2001/03/24 19:22:54  i10614
Initial revision

Revision 1.2  2001/02/22 14:47:44  mbauer
new Gui-look implemented

Revision 1.1  2001/02/20 17:34:59  mbauer
initital release



"""

import cGuiRequestHandler

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
        return


    def AcceptCommand(self, sUrl):
        """take command from pProxy

        sUrl    -- complete url containing command

        return  -- html code with answer
                   String containing content-type of answer

        """

        # pass on to cGuiRequestHandler
        return self.cGuiRequestHandler.AcceptCommand(sUrl)



