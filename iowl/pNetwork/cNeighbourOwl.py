
__version__ = "$Revision: 1.5 $"

"""
$Log: cNeighbourOwl.py,v $
Revision 1.5  2001/05/30 20:25:37  i10614
changed debug output

Revision 1.4  2001/04/15 19:10:59  i10614
Ping<->Pong works again.

Revision 1.3  2001/04/14 15:01:36  i10614
bugfixes

Revision 1.2  2001/04/09 13:16:30  i10614
implemented simple caching of neighbourowls

Revision 1.1.1.1  2001/03/24 19:22:44  i10614
Initial import to stio1 from my cvs-tree

Revision 1.10  2001/03/18 22:25:56  mbauer
removed debug output

Revision 1.9  2001/03/17 14:58:16  mbauer
changed comments

Revision 1.8  2001/02/21 18:18:20  mbauer
fixed bug when deleting owl

Revision 1.6  2001/02/17 16:19:06  mbauer
added functionality to detect and delete "dead" owls from list and still retain at least the entrypoint.

Revision 1.1  2001/02/15 19:52:17  mbauer
initial checkin


"""

import xmlrpclib
import pManager
# import cOwlManager


class cNeighbourOwl:
    """Representation of other iOwl

    Offers all remote owl functions via Remote Procedure Call

    """

    def __init__(self, ip, port, cOwlManager):
        """Contructor"""

        # store ip and port of owl
        self.IP = ip
        self.iPort = port
        self.cOwlManager = cOwlManager


    def GetServer(self):
        """return xmlrpc Server-object representing this owl"""

        return xmlrpclib.Server('http://'+str(self.IP)+':'+str(self.iPort))


    def GetIP(self):
        """return string containing my IP"""
        return self.IP


    def GetPort(self):
        """return integer containing my port"""
        return self.iPort


    def Ping(self, sPing):
        """Ping owl"""

        try:
            # get remote owlserver ("myself")
            myself = self.GetServer()
            # call remote Ping-function
            myself.Ping(sPing)
        except TypeError:
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': PING for '+str(self.IP)+':'+str(self.iPort)+' could not be sent (TypeError).')
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': Content of PING: '+sPing)
        except:
            # Can't call remote function - delete owl from list
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': Cant do RPC for '+str(self.IP)+':'+str(self.iPort)+'. Discarding owl.')
            # Delete owl
            self.cOwlManager.DeleteOwl(self.cOwlManager.lKnownOwls, (self.IP, self.iPort))


    def Pong(self, sPong):
        """Pong owl"""

        try:
            # get remote owlserver ("myself")
            myself = self.GetServer()
            # call remote Pong-function
            myself.Pong(sPong)
        except TypeError:
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': PONG for '+str(self.IP)+':'+str(self.iPort)+' could not be sent (TypeError).')
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': Content of PONG: '+sPong)
        except:
            # Can't call remote function - delete owl from list
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': Cant do RPC for '+str(self.IP)+':'+str(self.iPort)+'. Discarding owl.')
            # Delete owl
            self.cOwlManager.DeleteOwl(self.cOwlManager.lKnownOwls, (self.IP, self.iPort))



    def Request(self, sRequest):
        """send Request"""

        try:
            # get remote owlserver ("myself")
            myself = self.GetServer()
            # call remote Request-function
            myself.Request(sRequest)
        except TypeError:
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': REQUEST for '+str(self.IP)+':'+str(self.iPort)+' could not be sent (TypeError).')
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': Content of REQUEST: '+sRequest)
        except:
            # Can't call remote function - delete owl from list
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': Cant do RPC for '+str(self.IP)+':'+str(self.iPort)+'. Discarding owl.')
            # Delete owl
            self.cOwlManager.DeleteOwl(self.cOwlManager.lKnownOwls, (self.IP, self.iPort))


    def Answer(self, sAnswer):
        """send Answer"""

        try:
            # get remote owlserver ("myself")
            myself = self.GetServer()

            # call remote Answer-function
            myself.Answer(sAnswer)
        except TypeError:
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': ANSWER for '+str(self.IP)+':'+str(self.iPort)+' could not be sent (TypeError).')
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': Content of ANSWER: '+sANSWER)
        except:
            # Can't call remote function - delete owl from list
            pManager.manager.DebugStr('cNeighbourOwl '+ __version__ +': Cant do RPC for '+str(self.IP)+':'+str(self.iPort)+'. Discarding owl.')
            # Delete owl
            self.cOwlManager.DeleteOwl(self.cOwlManager.lKnownOwls, (self.IP, self.iPort))




###############################################
### TEST FUNCTIONS ############################

def test():
    owl = cNeighbourOwl('127.0.0.1', 2323)

    ping = 'ping...ping'
    pong = 'pong...pong'
    req = 'request...'
    answ = 'answ'

    print 'pinging'
    owl.Ping(ping)

    print 'ponging'
    owl.Pong(pong)

    print 'requesting'
    owl.Request(req)

    print 'answering'
    owl.Answer(answ)



if __name__ == '__main__':
    test()
