
__version__ = "$Revision: 1.1 $"

"""
$Log: cNetManager.py,v $
Revision 1.1  2001/03/24 19:22:50  i10614
Initial revision

Revision 1.28  2001/03/18 22:26:52  mbauer
added try-except for all threads

Revision 1.27  2001/03/16 16:58:10  mbauer
Added try-except block for generating Pong. Catches broken Pings instead of dumping a stack-trace.

Revision 1.26  2001/02/22 15:15:30  a
typo fixed

Revision 1.25  2001/02/22 12:34:27  mbauer
resynced with cvs

Revision 1.23  2001/02/21 18:14:36  mbauer
added Garbage collector for old entries in request-table

Revision 1.22  2001/02/19 21:46:53  mbauer
Now always translate entrypoint to ip

Revision 1.18  2001/02/18 20:04:35  mbauer
Frorgot to cast int to string when generating debug output ( inside TimerTick())

Revision 1.17  2001/02/18 10:42:38  mbauer
Modified debug output

Revision 1.16  2001/02/18 10:21:06  mbauer
now only pongs reset timer for generating ping. Previously any net traffic did that.

Revision 1.15  2001/02/17 16:19:06  mbauer
added functionality to detect and delete "dead" owls from list and still retain at least the entrypoint.

Revision 1.6  2001/02/15 23:09:07  mbauer
activated cOwlManager

Revision 1.1  2001/02/14 12:31:56  mbauer
initial check-in



"""

import cDOM
import time
import pManager
import cNetServer
import cOwlManager
import socket

class cNetManager:
    """Coordinator for iowl.net. Responsible for accepting incoming
    packages and sending outgoing packages.

    XXX - functions GeneratePing, GeneratePong, GenerateRequest, GenerateAnswer
          are all very similar. Should implement one generic function instead.
    """

    def __init__(self):
        """Constructor"""

        # create cNetServer
        self.cNetServer = cNetServer.cNetServer()

        # create cOwlManager, pass myself
        self.cOwlManager = cOwlManager.cOwlManager(self)


    def SetParam(self, sOption, sValue):
        """Accept Config

        Available options:

        entryip         -- IP of Entrypoint
        entryport       -- port of Entrypoint
        numneighbours   -- Number of owls used for distribute()
        listenport      -- port cNetserver should listen on
        ttl             -- default TTL for new packages
        interval        -- maximum number of seconds for idle network operation
                            after which a PING is generated
        maxowlstokeep   -- maximum number of owls to keep in list
        maxanswers      -- maximum number of answers allowed for request

        """

        if sOption == 'entryip':
            # convert name to ip
            self.EntryIP = socket.gethostbyname(str(sValue))
        elif sOption == 'entryport':
            self.iEntryPort = int(sValue)
        elif sOption == 'numneighbours':
            self.cOwlManager.SetNumNeighbours(int(sValue))
        elif sOption == 'maxowlstokeep':
            self.cOwlManager.SetMaxOwlsToKeep(int(sValue))
        elif sOption == 'listenport':
            self.cNetServer.SetListenPort(int(sValue))
        elif sOption == 'ttl':
            self.iTTL = int(sValue)
        elif sOption == 'interval':
            self.iInterval = int(sValue)
        elif sOption == 'requestlifetime':
            self.cOwlManager.SetRequestLifeTime(int(sValue))



    def StartConnection(self):
        """Start connection with the iOwl network

        Called by cNetworkInterface. Call cNetServer.StartListen(), add EntryPoint to cOlwmanager,
        generate an initial PING and pass it to cOwlManager.Distribute()

        """

        pManager.manager.DebugStr('cNetManager '+ __version__ +': Starting connection.')

        # start watchdog
        self.WatchDogID = pManager.manager.RegisterWatchdog(self.TimerTick, self.iInterval)

        # determine own IP adress
        pManager.manager.SetOwnIP(self.GetOwnIP())

        # Start OwlManager
        self.cOwlManager.Start()

        # add entrypoint to cOwlManager
        self.cOwlManager.AddOwl(self.EntryIP, self.iEntryPort)

        # generate PING
        domPing = self.GeneratePing()

        pManager.manager.DebugStr('cNetManager '+ __version__ +': Passing initial PING to cOwlManager.')

        # pass PING to cOwlManager
        self.cOwlManager.Distribute(domPing)

        # start server
        self.cNetServer.StartListen()


    def Stop(self):
        """Stop the network

        Stop cNetServer (cNetServer.StopListen())

        """

        self.cNetServer.StopListen()


    def HandlePing(self, sPing):
        """Handle incoming Ping

        Called by CRPCRequestHandler.
        Parse params-string into DOM
        Pass Ping to cOwlManager.Distribute()
        Generate Answer-Pong.
        Pass Pong to cOwlManager.Answer()

        """

        # log incoming ping
        pManager.manager.DebugStr('cNetManager '+ __version__ +': Incoming Ping...')

        try:
            # create cDOM from ascii-Ping
            domPing = cDOM.cDOM()
            domPing.ParseString(sPing)

            # pass ping to cOwlManager. If cOwlManager accepts ping, answer with pong
            if self.cOwlManager.Distribute(domPing) == 'okay':
                # generate Pong
                try:
                    domPong = self.GeneratePong(domPing)
                except:
                    # Could not generate Pong
                    pManager.manager.DebugStr('cNetManager '+ __version__ +': Could not parse info from Ping. No Pong generated.')
                    return

                # pass Pong to cOlwManager
                self.cOwlManager.Answer(domPong)
            else:
                pManager.manager.DebugStr('cNetManager '+ __version__ +': cOwlManager did not accept ping. Probably a vicious circle or corrupt cDOM')
        except:
            # unknown error. log and forget.
            # get exception
            eType, eValue, eTraceback = sys.exc_info()

            # build stacktrace string
            tb = ''
            for line in traceback.format_tb(eTraceback, 15):
                tb = tb + line

            pManager.manager.DebugStr('pNetwork '+ __version__ +': Unhandled error in thread HandlePing(): Type: '+str(eType)+', value: '+str(eValue))
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Traceback:\n'+str(tb))



    def HandlePong(self, sPong):
        """Handle incoming Pong

        Called by CRPCRequestHandler.Pong().
        Reset LastNetAction-time.
        Pass PONG to cOwlManager.Answer().

        """
        # log incoming pong
        pManager.manager.DebugStr('cNetManager '+ __version__ +': Incoming Pong...')

        try:
            # reset WatchDog
            pManager.manager.ResetWatchdog(self.WatchDogID)

            # create cDOM from ascii-Pong
            domPong = cDOM.cDOM()
            domPong.ParseString(sPong)

            # extract PONG-source and add to own list of owls
            self.ExtractPongSource(domPong)

            # pass to cOwlManager
            self.cOwlManager.Answer(domPong)
        except:
            # unknown error. log and forget.
            # get exception
            eType, eValue, eTraceback = sys.exc_info()

            # build stacktrace string
            tb = ''
            for line in traceback.format_tb(eTraceback, 15):
                tb = tb + line

            pManager.manager.DebugStr('pNetwork '+ __version__ +': Unhandled error in thread HandlePong(): Type: '+str(eType)+', value: '+str(eValue))
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Traceback:\n'+str(tb))


    def HandleRequest(self, sRequest):
        """Handle incoming Request

        Called by cRPCRequestHandler.Request().
        Pass Request to cOwlManager.Distribute() for further spreading.

        """

        # log incoming Request
        pManager.manager.DebugStr('cNetManager '+ __version__ +': Incoming Request...')

        try:
            # create cDOM from ascii-Ping
            domRequest = cDOM.cDOM()
            domRequest.ParseString(sRequest)

            # pass to cOwlManager
            self.cOwlManager.Request(domRequest)
        except:
            # unknown error. log and forget.
            # get exception
            eType, eValue, eTraceback = sys.exc_info()

            # build stacktrace string
            tb = ''
            for line in traceback.format_tb(eTraceback, 15):
                tb = tb + line

            pManager.manager.DebugStr('pNetwork '+ __version__ +': Unhandled error in thread HandleRequest(): Type: '+str(eType)+', value: '+str(eValue))
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Traceback:\n'+str(tb))



    def HandleAnswer(self, sAnswer):
        """Handle incoming Answer

        Called by cRPCRequestHandler.Answer().
        Pass Answer to cOwlManager.Answer().

        """

        # log incoming Answer
        pManager.manager.DebugStr('cNetManager '+ __version__ +': Incoming Answer...')

        try:
            # create cDOM from ascii-Ping
            domAnswer = cDOM.cDOM()
            domAnswer.ParseString(sAnswer)

            # pass on to cOwlManager
            self.cOwlManager.Answer(domAnswer)
        except:
            # unknown error. log and forget.
            # get exception
            eType, eValue, eTraceback = sys.exc_info()

            # build stacktrace string
            tb = ''
            for line in traceback.format_tb(eTraceback, 15):
                tb = tb + line

            pManager.manager.DebugStr('pNetwork '+ __version__ +': Unhandled error in thread HandleAnswer(): Type: '+str(eType)+', value: '+str(eValue))
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Traceback:\n'+str(tb))


    def SendRequest(self, elRequest):
        """process request by own pRecommendation package.

        Called by pNetworkInterface.SendRequest().
        Generate Request and pass it to cOwlManager for distribution

        elRequest   -- Request from pRecommendation

        return      -- new id generated for request


        """

        # Build network package containing request
        domRequest, id = self.GenerateRequest(elRequest)

        # Pass Request to cOwlManager
        self.cOwlManager.Distribute(domRequest)

        # return id for pRecommendation
        return id



    def SendAnswer(self, elAnswer, id):
        """process Answer by own pRecommendation

        Called by pNetworkInterface.SendAnswer()

        Generate Answer and pass it on to cOwlManager

        elAnswer    -- Answer from pRecommendation
        id          -- id of corresponding Request, needed to figure out the routing of answer

        """

        # Build network package containing answer
        domAnswer = self.GenerateAnswer(elAnswer, id)

        # pass Answer to cOwlManager
        self.cOwlManager.Answer(domAnswer)



    def TimerTick(self):
        """Watchdog for network

        Called by Timer after <interval> seconds of no network activity.

        """
        # log tick
        pManager.manager.DebugStr('cNetManager '+ __version__ +': No PONG received for '+str(self.iInterval)+' seconds. Generating PING.')

        # Re-Add Entrypoint, just in case it got deleted because temporarily not available...
        self.cOwlManager.AddOwl(self.EntryIP, self.iEntryPort)

        # Generate Ping
        ping = self.GeneratePing()
        self.cOwlManager.Distribute(ping)



    def GeneratePing(self):
        """Generate a PING cDOM

        a Ping looks like:

        <iowl.net version="0.1" id="4711" type="Ping" ttl="12">
            <originator ip="192.168.99.2" port="2323"></originator>
        </iowl.net>

        return -- cDOM containing a PING packet

        """

        # create unique id
        id = pManager.manager.GetUniqueNumber()
        # id = 46722

        # get own IP from manager
        ownip = pManager.manager.GetOwnIP()
        # ownip = '123.456.789.101'

        # get ListenPort from cNetServer
        iListenPort = self.cNetServer.GetListenPort()

        # create the dom
        domPing = cDOM.cDOM()

        # create core element: originator, containing ip and port as attributes
        elOriginator = domPing.CreateElement('originator', {'ip':str(ownip), 'port':str(iListenPort)}, '')

        # create list containing core element
        els = []
        els.append(elOriginator)

        # get iOwl-version
        sVersion = str(pManager.manager.GetVersion())
        # sVersion = 'Testversion'

        # create container: iowl.net
        elCont = domPing.CreateElementContainer('iowl.net', {'version':sVersion, 'id':str(id), 'type':'Ping', 'ttl':str(self.iTTL)}, els)

        # save elements in dom
        domPing.SetRootElement(elCont)

        # finished!
        return domPing


    def GeneratePong(self, domPing):
        """Generate a PONG cDOM

        PONG is Answer to incoming Ping. It contains the same data as
        a Ping + info about myself.

        Note that attribute 'id' has to be the id of the corresponding PING.
        Also note that answer's TTL-counter is irrelevant since their way through the network
        is already fixed and they dont get distributed like requests.

        a Pong looks like:

        <iowl.net version="0.1" id="4711" type="Pong" ttl="10">
            <originator ip="192.168.99.2" port="2323"></originator>
            <answerer ip="192.168.99.2" port="2323"></answer>
        </iowl.net>

        return -- cDOM containing a PONG packet

        """

        # get id of PING
        # id = 123
        version, id, type, ttl, ip, port = self.cOwlManager.GetDomInfo(domPing)

        # get own IP from manager
        ownip = pManager.manager.GetOwnIP()
        # ownip = '123.456.789.101'

        # get ListenPort from cNetServer
        iListenPort = self.cNetServer.GetListenPort()

        # create the dom
        domPong = cDOM.cDOM()

        # create core element: originator, containing ip and port as attributes
        elOriginator = domPong.CreateElement('originator', {'ip':str(ownip), 'port':str(iListenPort)}, '')
        # create core element: answerer, containing ip and port as attributes
        elAnswerer = domPong.CreateElement('answerer', {'ip':str(ownip), 'port':str(iListenPort)}, '')

        # create list containing core elements
        els = []
        els.append(elOriginator)
        els.append(elAnswerer)

        # get iOwl-version
        sVersion = str(pManager.manager.GetVersion())
        # sVersion = 'Testversion'

        # create container: iowl.net
        elCont = domPong.CreateElementContainer('iowl.net', {'version':sVersion, 'id':str(id), 'type':'Pong', 'ttl':'10'}, els)

        # save elements in dom
        domPong.SetRootElement(elCont)

        # finished!
        return domPong


    def GenerateRequest(self, elRequest):
        """Generate complete Request-package containing elRequest

        elRequest  -- Request as generated by pRecommendation

        return      -- id of new package

        """
        # get new id
        # id = 123
        id = pManager.manager.GetUniqueNumber()

        # get own IP from manager
        # ownip = '123.456.789.101'
        ownip = pManager.manager.GetOwnIP()

        # get ListenPort from cNetServer
        iListenPort = self.cNetServer.GetListenPort()

        # create the dom
        domRequest = cDOM.cDOM()

        # create core element: originator, containing ip and port as attributes
        elOriginator = domRequest.CreateElement('originator', {'ip':str(ownip), 'port':str(iListenPort)}, '')

        # create list containing core elements
        els = []
        els.append(elOriginator)
        els.append(elRequest)

        # get iOwl-version
        sVersion = str(pManager.manager.GetVersion())
        # sVersion = 'Testversion'

        # create container: iowl.net
        elCont = domRequest.CreateElementContainer('iowl.net', {'version':sVersion, 'id':str(id), 'type':'Request', 'ttl':str(self.iTTL)}, els)

        # save elements in dom
        domRequest.SetRootElement(elCont)

        # finished!
        return domRequest, id


    def GenerateAnswer(self, elAnswer, id):
        """Generate complete Answer-package containing elRequest

        elAnswer    -- Answer as generated by pRecommendation
        id          -- id Answer should contain (id of request this answer belongs to. Needed to figure the
                        correct routing in cOwlManager

        return      -- domAnswer, ready for sending through network


        """

        # get own IP from manager
        ownip = pManager.manager.GetOwnIP()
        # ownip = '123.456.789.101'

        # get ListenPort from cNetServer
        iListenPort = self.cNetServer.GetListenPort()

        # create the dom
        domAnswer = cDOM.cDOM()

        # create core element: originator, containing ip and port as attributes
        elOriginator = domAnswer.CreateElement('originator', {'ip':str(ownip), 'port':str(iListenPort)}, '')

        # create list containing core elements
        els = []
        els.append(elOriginator)
        els.append(elAnswer)

        # get iOwl-version
        sVersion = str(pManager.manager.GetVersion())
        # sVersion = 'Testversion'

        # create container: iowl.net
        elCont = domAnswer.CreateElementContainer('iowl.net', {'version':sVersion, 'id':str(id), 'type':'Answer', 'ttl':str(self.iTTL)}, els)

        # save elements in dom
        domAnswer.SetRootElement(elCont)

        # finished!
        return domAnswer


    def ExtractPongSource(self, domPong):
        """Extract source of PONG

        Add new owl (Pong-source) to cOwlmanager's list of known owls.

        """

        # look for element containing 'answerer'
        lElements = domPong.MatchingElements('answerer', '')
        if len(lElements)==1:
            # found it!
            # create list of attributes
            lAttrs = ['ip','port']
            dAttrs = domPong.GetAttrs(lElements[0], lAttrs)
            # add source owl to cOwlManager
            self.cOwlManager.AddOwl(dAttrs['ip'], dAttrs['port'])
        else:
            raise 'Could not get PONG info...'


    def GetOwnIP(self):
        """Determine own IP

        Try to connect a socket to entryowl and call socket.getsockname() to
        get ip for the correct interface. Important if i have more than one network interfaces.

        If socket-connect fails, try fallback with 'gethostbyname(gethostname())'

        return  -- string containing own IP

        """

        # Own ip adress
        sOwnIP = ''

        # create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # connect to entryOwl
            s.connect((self.EntryIP, self.iEntryPort))
            # get hostname and port
            sOwnIP, iOwnPort = s.getsockname()
            # close socket
            s.close()
        except:
            # socket-connect failed :-(
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Could not connect socket to determine own IP. Reverting to "gethostbyname()"...')
            sOwnIP = socket.gethostbyname(socket.gethostname())

        return sOwnIP




#############################################################################
## TEST FUNCTIONS ###########################################################

def test():
    manager = cNetManager()
    manager.cNetServer.SetListenPort(2323)
    manager.iTTL = 10
    dummy = cDOM.cDOM()
    elReq = dummy.CreateElement('request', {'url':'www.iowl.net', 'otherurl':'www.arschlecken.de'}, 'Bitte recommendation liefern!')
    elAns = dummy.CreateElement('answer', {'url':'www.wissen.de'}, 'Check das aus!')
    re, id = manager.GenerateRequest(elReq)
    print
    print re.ToXML()
    print
    an = manager.GenerateAnswer(elAns,id)
    print an.ToXML()

    print
    print manager.cOwlManager.GetDomInfo(an)

    #manager.ExtractPongSource(p)

if __name__ == '__main__':
    test()





