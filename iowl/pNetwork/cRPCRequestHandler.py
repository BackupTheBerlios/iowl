
__version__ = "$Revision: 1.5 $"

"""
$Log: cRPCRequestHandler.py,v $
Revision 1.5  2002/03/10 10:12:55  Saruman
changed some debug output

Revision 1.4  2002/02/21 12:46:18  Saruman
Added routingtable to statistics page

Revision 1.3  2002/02/11 15:12:38  Saruman
Major network changes.
Network protocol now 0.3, incompatible to older versions!
Should fix all problems regarding the detection of own ip and enable use of iOwl behind a firewall.

Revision 1.2  2001/08/10 18:36:21  i10614
added debug output.

Revision 1.1.1.1  2001/03/24 19:22:40  i10614
Initial import to stio1 from my cvs-tree

Revision 1.6  2001/02/17 13:48:43  mbauer
removed some debug output

Revision 1.5  2001/02/15 23:07:38  mbauer
more documentation

Revision 1.1  2001/02/14 18:02:48  mbauer
initial checkin


"""


import xmlrpcserver
import xmlrpclib
import pManager
import cNetManager
import thread

class cRPCRequestHandler(xmlrpcserver.RequestHandler):
    """Handle RPCs from other owls"""

    def call(self, method, params):
        """Handler for incoming requests

        Dispatches incoming method-call to responsible function.

        method -- remotely requested local method
        params -- parameter for method-call

        """

        pManager.manager.DebugStr('cRPCReqHandler '+ __version__ +': Dispatching: ' + str(method) + ', Parameter: ' +str(params), 4)
        try:
                # Look if requested method exists
                server_method = getattr(self, method)
        except:
                raise AttributeError, 'Server does not have XML-RPC procedure "%s"' % method
        # execute requested method
        return server_method(method, params)


    def Ping(self, method, params):
        """Incoming Ping

        Create new thread for cNetManager->HandlePing()

        """

        # get cNetwork-interface
        cNetworkInterface = pManager.manager.GetNetworkInterface()

        # get cNetManager
        cNetManager = cNetworkInterface.cNetManager

        # get originating owl
        host, port = self.client_address;

        # add host to params
        params = params + (host,)

        pManager.manager.DebugStr('cRPCReqHandler '+ __version__ +': ping from ' + str(host) + ':' + str(port), 4)

        # start new thread
        thread.start_new_thread(cNetManager.HandlePing, params)
        # without new thread:
        # cNetManager.HandlePing(params)

        return 'okay'


    def Pong(self, method, params):
        """Incoming Pong

        Create new thread for cNetManager->HandlePong()

        """

        # get cNetwork-interface
        cNetworkInterface = pManager.manager.GetNetworkInterface()

        # get cNetManager
        cNetManager = cNetworkInterface.cNetManager

        # get originating owl
        host, port = self.client_address;

        # add host to params
        params = params + (host,)

        pManager.manager.DebugStr('cRPCReqHandler '+ __version__ +': pong from ' + str(host) + ':' + str(port), 4)

        # start new thread
        thread.start_new_thread(cNetManager.HandlePong, params)
        # without new thread:
        # cNetManager.HandlePong(params)

        return 'okay'


    def Request(self, method, params):
        """Incoming Request

        Create new thread for cNetManager->HandleRequest()

        """

        # get cNetwork-interface
        cNetworkInterface = pManager.manager.GetNetworkInterface()

        # get cNetManager
        cNetManager = cNetworkInterface.cNetManager

        # get originating owl
        host, port = self.client_address;

        # add host to params
        params = params + (host,)

        pManager.manager.DebugStr('cRPCReqHandler '+ __version__ +': request from ' + str(host) + ':' + str(port), 4)

        # start new thread
        thread.start_new_thread(cNetManager.HandleRequest, params)
        # without new thread:
        # cNetManager.HandleRequest(params)

        return 'okay'


    def Answer(self, method, params):
        """Incoming Answer

        Create new thread for cNetManager->HandleAnswer()

        """

        # get cNetwork-interface
        cNetworkInterface = pManager.manager.GetNetworkInterface()

        # get cNetManager
        cNetManager = cNetworkInterface.cNetManager

        # get originating owl
        host, port = self.client_address;

        # add host to params
        params = params + (host,)

        pManager.manager.DebugStr('cRPCReqHandler '+ __version__ +': answer from ' + str(host) + ':' + str(port), 4)

        # start new thread
        thread.start_new_thread(cNetManager.HandleAnswer, params)
        # without new thread:
        # cNetManager.HandleAnswer(params)

        return 'okay'
