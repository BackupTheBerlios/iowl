
__version__ = "$Revision: 1.2 $"

"""
$Log: cNetServer.py,v $
Revision 1.2  2001/05/26 14:01:19  i10614
changed default params

Revision 1.1.1.1  2001/03/24 19:22:39  i10614
Initial import to stio1 from my cvs-tree

Revision 1.5  2001/03/18 23:02:33  mbauer
added missing import socket

Revision 1.4  2001/02/18 20:22:19  mbauer
activeted proxy, so now have to start a real thread for netServer

Revision 1.3  2001/02/17 00:40:40  mbauer
Loads of enhancements and bugfixes...

Revision 1.2  2001/02/15 19:51:31  mbauer
cosmetic changes


"""
import cRPCRequestHandler
import SocketServer
import thread
import pManager
import socket

class cNetServer:
    """Listen for incoming connections from other owls"""

    def __init__(self):
        """Constructor"""
        self.iListenPort = 2323


    def SetListenPort(self, iPort):
        """Set Listen Port"""

        self.iListenPort = iPort


    def StartListen(self):
        """Start TCPserver"""

        pManager.manager.DebugStr('cNetServer '+ __version__ +': Starting thread for NetServer')
        self.server = SocketServer.TCPServer(('', self.iListenPort), cRPCRequestHandler.cRPCRequestHandler)

        # for testing only - start listen without new thread:
        # self.server.serve_forever()
        # with new thread:
        thread.start_new(self.server.serve_forever, ())


    def StopListen(self):
        """Stop listening and close server

        XXX Dunno how to do this. ??

        """

        pass

    def GetListenPort(self):
        """Return port i am listening on"""
        return self.iListenPort





################################################################
### TEST FUNCTIONS #############################################

def test():
    s = cNetServer(x)
    s.StartListen
    print('finished!')


if __name__=='__main__':
    test()







