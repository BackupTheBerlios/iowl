
__version__ = "$Revision: 1.3 $"

"""
$Log: pNetworkInterface.py,v $
Revision 1.3  2001/04/14 15:01:36  i10614
bugfixes

Revision 1.2  2001/03/27 18:25:17  i10614
added shutdown notification

Revision 1.1.1.1  2001/03/24 19:22:39  i10614
Initial import to stio1 from my cvs-tree

Revision 1.5  2001/02/19 17:42:21  mbauer
added SendAnswer, SendRequest for pRecommendation

Revision 1.4  2001/02/14 18:00:15  mbauer
initial checkin

Revision 1.1  2001/02/14 10:47:29  mbauer
initial version


"""

import cNetManager
import pManager

class pNetworkInterface:
    """Interface class for package pNetwork

    Contains all public available functions of package pNetwork.

    """

    def __init__(self):
        """Constructor"""

        # create NetManager
        self.cNetManager = cNetManager.cNetManager()


    def SendRequest(self, elRequest):
        """Send request through iOwl network

        Pass document to cNetManager.SendRequest().

        elRequest   -- request of type cDom.element (correct type ??).
        return      -- id of generated net package
        """

        # pass dom to cNetManager
        return self.cNetManager.SendRequest(elRequest)


    def SendAnswer(self, elAnswer, id):
        """Send answer through iOwl network

        Pass answer to cNetManager.SendRequest().

        elAnswer    -- request of type cDOM.element (correct type ??).
        id          -- id of according request package

        """

        # pass dom to cNetManager
        return self.cNetManager.SendAnswer(elAnswer, id)


    def SetParam(self, sOption, sValue):
        """Accept settings

        Pass setparam-call to cNetManager

        """
        self.cNetManager.SetParam(sOption, sValue)


    def TimerTick(self, interval):
        """Timer function, called after interval seconds

        Necessary to generate PINGs after interval time

        """
        self.cNetManager.TimerTick(interval)


    def Shutdown(self):
        """Initiate shutdown of Network"""
        pManager.manager.DebugStr('pNetwork '+ __version__ +': Shutting down.')
        self.cNetManager.Stop()


    def Start(self):
        """Start operation of iOwl network"""
        self.cNetManager.StartConnection()


    def GetListenPort(self):
        """return port i am listening on"""
        return self.cNetManager.GetListenPort()


    def GetProtocolVersion(self):
        """return version of network protocol"""
        return self.cNetManager.GetProtocolVersion()


