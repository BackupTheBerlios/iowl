__version__ = "$Revision: 1.2 $"

"""
$Log: pProxyInterface.py,v $
Revision 1.2  2001/03/27 14:09:11  i10614
added functionality to specify address proxy listens at in configfile

Revision 1.1.1.1  2001/03/24 19:23:02  i10614
Initial import to stio1 from my cvs-tree

Revision 1.3  2001/02/20 17:37:13  mbauer
added SetRecording() and GetStatus()

Revision 1.2  2001/02/19 13:10:29  mbauer
Added explicit click detection

Revision 1.1  2001/02/18 19:55:17  mbauer
initial release


"""

import pManager
import cProxyManager

class pProxyInterface:
    """Interface class for package pProxy

    Contains all public available functions of package pProxy.

    """

    def __init__(self):
        """Constructor"""

        # create ProxyManager
        self.cProxyManager = cProxyManager.cProxyManager()


    def SetParam(self, sOption, sValue):
        """Accept settings

        Pass setparam-call to cProxyManager

        """

        self.cProxyManager.SetParam(sOption, sValue)


    def Start(self):
        """Start proxy operation"""

        self.cProxyManager.Start()


    def ShutDown(self):
        """Stop proxy Operation"""

        pManager.manager.DebugStr('pProxy '+ __version__ +': Shutting down.')
        self.cProxyManager.Stop()


    def GetClickTime(self):
        """Return clicktime"""
        return self.cProxyManager.GetClickTime()


    def GetUseParent(self):
        """Return 1 if i use a parentproxy, 0 otherwise"""
        return self.cProxyManager.GetUseParent()


    def GetParent(self):
        """Return tuple (IP, PORT) of proxy to use"""
        return self.cProxyManager.GetParent()


    def GetLastExplicit(self):
        """Return timestamp of last explicit click"""
        return self.cProxyManager.GetLastExplicit()


    def SetLastExplicit(self, iTimestamp):
        """Set timestamp of last explicit click"""
        self.cProxyManager.SetLastExplicit(iTimestamp)


    def SetRecording(self, bValue):
        """Set status of proxy

        bValue -- new status. 0 -> not recording clickstream
                              1 -> recordiung clickstream

        """

        # pass call to cProxyManager
        self.cProxyManager.SetRecording(bValue)


    def GetStatus(self):
        """Return status of proxy

        returns -- 0 or 1
                0 -> not recording clickstream
                1 -> recording clickstream

        """

        return self.cProxyManager.GetStatus()

