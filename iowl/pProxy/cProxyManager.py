__version__ = "$Revision: 1.4 $"

"""
$Log: cProxyManager.py,v $
Revision 1.4  2001/07/19 19:46:52  i10614
removed warning at initial setting of options

Revision 1.3  2001/07/15 14:39:18  i10614
implemented config-change from GUI

Revision 1.2  2001/03/27 14:09:11  i10614
added functionality to specify address proxy listens at in configfile

Revision 1.1.1.1  2001/03/24 19:23:01  i10614
Initial import to stio1 from my cvs-tree

Revision 1.5  2001/02/21 14:52:10  mbauer
minor changes

Revision 1.4  2001/02/20 17:37:13  mbauer
added SetRecording() and GetStatus()

Revision 1.3  2001/02/20 11:44:58  mbauer
cosmetic changes

Revision 1.2  2001/02/19 13:10:29  mbauer
Added explicit click detection


"""

import pManager
import cProxyCore

class cProxyManager:
    """Main class of proxy

    Handles configuration and commands from pProxyInterface, stores
    data necessary for detection of explicit clicks

    """

    def __init__(self):
        """Constructor"""

        # create cCoreProxy
        self.cProxyCore = cProxyCore.cProxyCore()

        # init time of last explicit click
        self.iLastExplicit = 0

        # start recording clickstream
        self.bRecording = 1


    def SetParam(self, sOption, sValue):
        """Accept Config

        Available options:

        proxyport       -- port cProxyCore should listen on
        clicktime       -- time to seperate implicit from explicit clicks
        parentproxyip   -- ip of parent proxy i should use
        parentproxyport -- port of parent proxy
        recording       -- status of proxy (recording/not recording clickstream)
        listento        -- adress the proxy listens to

        """

        if sOption == 'proxyport':
            self.cProxyCore.SetPort(str(sValue))
            # XXX - Need to restart proxy for changes to take effect!
            if pManager.manager.IsRunning():
                pManager.manager.DebugStr('pProxyManager '+ __version__ +': Warning: Change of proxyport needs a restart!')
        elif sOption == 'clicktime':
            self.cProxyCore.SetClickTime(str(sValue))
        elif sOption == 'parentproxyip':
            self.cProxyCore.SetParentProxyIP(str(sValue))
        elif sOption == 'parentproxyport':
            self.cProxyCore.SetParentProxyPort(str(sValue))
        elif sOption == 'useparent':
            self.cProxyCore.SetUseParent(int(sValue))
        elif sOption == 'recording':
            self.bRecording = int(sValue)
            # update trayicon
            pManager.manager.SetIcon(int(sValue))
        elif sOption == 'listenat':
            # XXX Need to restart proxy for changes to take effect!
            self.cProxyCore.SetListenAt(str(sValue))
            if pManager.manager.IsRunning():
                pManager.manager.DebugStr('pProxyManager '+ __version__ +': Warning: Change of listen-adress needs a restart!')
        else:
            # unknown option!
            pManager.manager.DebugStr('pProxyManager '+ __version__ +': Warning: Trying to set unknown parameter "'+sOption+'".')


    def GetParent(self):
        """Return tuple (IP, PORT) of proxy to use"""
        return self.cProxyCore.GetParent()


    def GetUseParent(self):
        """Return 1 if i use a parentproxy, 0 otherwise"""
        return self.cProxyCore.GetUseParent()


    def Start(self):
        """Activate Listenloop in cProxyCore"""
        self.cProxyCore.StartListen()


    def Stop(self):
        """Stop ListenLoop in cProxyCore

        Since the main()-focus stays in cProxyCore.StartListen(), calling of
        this function leads to the complete exit of iOwl.net.
        So pProxy should be the last package to stop in case of a shutdown.

        """

        self.cProxyCore.StopListen()


    def GetLastExplicit(self):
        """Return timestamp of last explicit click"""
        return self.iLastExplicit


    def SetLastExplicit(self, iTimestamp):
        """Set timestamp of last explicit click"""
        self.iLastExplicit = iTimestamp


    def GetClickTime(self):
        """Return clicktime"""
        return self.cProxyCore.GetClickTime()


    def GetStatus(self):
        """Return status of proxy

        returns -- 0 or 1
                0 -> not recording clickstream
                1 -> recording clickstream

        """

        return self.bRecording


