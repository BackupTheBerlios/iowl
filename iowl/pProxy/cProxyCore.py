__version__ = "$Revision: 1.2 $"

"""
$Log: cProxyCore.py,v $
Revision 1.2  2001/03/26 17:49:35  i10614
changed http://iowl to http://my.iowl.net. Improved title extraction.

Revision 1.1.1.1  2001/03/24 19:23:01  i10614
Initial import to stio1 from my cvs-tree

Revision 1.5  2001/03/18 18:51:32  mbauer
proxy now only listens on localhost, not reachable from other computers

Revision 1.4  2001/02/20 11:44:32  mbauer
cosmetic changes

Revision 1.3  2001/02/19 16:44:56  mbauer
changed shutdown-handling. Now accepts Ctrl-c for a clean shutdown.


"""
import cProxyHandler
import SocketServer

class cProxyCore:
    """Contains the core functionality of pProxy

    Tasks: Listenloop, accepting and forwarding requests.

    """

    def __init__(self):
        """Constructor"""

        # Use a parent proxy?
        self.bUseParent = 0

        # ip of parent proxy
        self.sParentProxyIP = '0.0.0.0'

        # port of ParentProxy
        self.iParentProxyPort = 0

        # my own port to listen
        self.iProxyPort = 3228

        # clicktime in seconds to seperate implicit and explicit clicks
        self.fClickTime = 2.0


    def SetPort(self, port):
        """Set port to listen on"""
        self.iProxyPort = int(port)

    def SetClickTime(self, time):
        """Set time to seperate implicit and explicit clicks"""
        self.fClickTime = float(time)

    def SetParentProxyIP(self, ip):
        """Set IP of parent proxy"""
        self.sParentProxyIP = str(ip)

    def SetParentProxyPort(self, port):
        """Set IP of parent proxy"""
        self.iParentProxyPort = int(port)

    def SetUseParent(self, bool):
        """Use parent proxy?"""
        self.bUseParent = int(bool)

    def GetParent(self):
        """Return tuple (IP, PORT) of proxy to use"""
        return self.sParentProxyIP, self.iParentProxyPort

    def GetUseParent(self):
        """Return 1 if i use a parentproxy, 0 otherwise"""
        return self.bUseParent

    def GetClickTime(self):
        """Return clicktime"""
        return self.fClickTime

    def StartListen(self):
        """Start proxy

        Focus stays here until iOwl is shutting down!

        """

        # create Server, pass cProxyHandler
        self.Server = SocketServer.ThreadingTCPServer(('127.0.0.1', self.iProxyPort), cProxyHandler.cProxyHandler)

        # start Server
        self.Server.serve_forever()

    def StopListen(self):
        """Stop the Proxy"""

        # XXX - dont know how to stop a server that started through serve_forever() ...
        pass


