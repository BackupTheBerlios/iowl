
__version__ = "$Revision: 1.1 $"

"""
$Log: cRPCRequestHandler.py,v $
Revision 1.1  2001/03/24 19:22:40  i10614
Initial revision

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

        # pManager.manager.DebugStr('cRPCReqHandler '+ __version__ +': Dispatching: ' + str(method) + str(params))
        try:
                server_method = getattr(self, method)
        except:
                raise AttributeError, 'Server does not have XML-RPC procedure "%s"' % method
        return server_method(method, params)


    def Ping(self, method, params):
        """Incoming Ping

        Create new thread for cNetManager->HandlePing()

        """

        # get cNetwork-interface
        cNetworkInterface = pManager.manager.GetNetworkInterface()

        # get cNetManager
        cNetManager = cNetworkInterface.cNetManager

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

        # start new thread
        thread.start_new_thread(cNetManager.HandleAnswer, params)
        # without new thread:
        # cNetManager.HandleAnswer(params)

        return 'okay'
