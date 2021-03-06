
__version__ = "$Revision: 1.35 $"

"""
$Log: cNetManager.py,v $
Revision 1.35  2002/09/10 15:50:33  abiessmann
corrected URLs because of DNS change

Revision 1.34  2002/03/23 19:20:56  aharth
connect to network faster when using a dial-up connection

Revision 1.33  2002/03/10 10:12:55  Saruman
changed some debug output

Revision 1.32  2002/02/21 12:46:18  Saruman
Added routingtable to statistics page

Revision 1.31  2002/02/14 08:30:35  Saruman
Removed smart ip detection code.
Some cleanups

Revision 1.30  2002/02/13 10:46:22  Saruman
introduced counters and functions for gathering network stats.

Revision 1.29  2002/02/11 15:12:38  Saruman
Major network changes.
Network protocol now 0.3, incompatible to older versions!
Should fix all problems regarding the detection of own ip and enable use of iOwl behind a firewall.

Revision 1.28  2002/01/28 18:50:54  Saruman
changed default port 2323 for entryowl

Revision 1.27  2001/08/10 18:44:36  i10614
changed debug output.

Revision 1.26  2001/08/10 18:41:46  i10614
changed debug output.

Revision 1.25  2001/08/10 18:34:54  i10614
added debuglevel to all messages.

Revision 1.24  2001/08/07 20:13:27  i10614
introduced debuglevels for debug messages.

Revision 1.23  2001/07/19 19:46:11  i10614
fixed bug for closing sockets

Revision 1.22  2001/07/15 14:38:59  i10614
implemented config-change from GUI

Revision 1.21  2001/07/15 10:20:23  i10614
getting owls from www.iowl.net now optional

Revision 1.20  2001/06/10 15:56:51  i10614
added own thread for initialization

Revision 1.19  2001/06/05 18:21:39  i10614
added own thread for validateOwl(). Should solve startup-problems.

Revision 1.18  2001/05/30 20:27:04  i10614
Now connect to www.iowl.net instead of random owl to get own ip. Removed some debug output.

Revision 1.17  2001/05/26 14:01:19  i10614
changed default params

Revision 1.16  2001/05/26 11:41:28  i10614
less debug output

Revision 1.15  2001/05/26 10:03:12  i10614
added try-except for entry.pl

Revision 1.14  2001/05/25 18:47:09  i10614
bugfix for downloading in chunks

Revision 1.13  2001/05/20 16:15:45  i10614
small changes for .exe-building

Revision 1.12  2001/05/07 07:40:17  i10614
added iow.net/entry.pl functionality

Revision 1.11  2001/04/22 13:31:39  i10614
bugfix - entryIP was not initialized

Revision 1.10  2001/04/22 13:27:51  i10614
extended owl-caching -> now verifying old owls

Revision 1.9  2001/04/15 21:16:21  i10614
fixed for recommendations and answers

Revision 1.6  2001/04/15 19:10:59  i10614
Ping<->Pong works again.

Revision 1.5  2001/04/14 15:01:36  i10614
bugfixes

Revision 1.4  2001/04/09 13:16:30  i10614
implemented simple caching of neighbourowls

Revision 1.3  2001/04/09 12:22:16  i10614
Implemented protocol version check, more fixes for network communication

Revision 1.2  2001/04/07 17:06:24  i10614
many, many bugfixes for working network communication

Revision 1.1.1.1  2001/03/24 19:22:50  i10614
Initial import to stio1 from my cvs-tree

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
import sys
import traceback
import cNetPackage
import urllib
import thread


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

        # protocol version
        self.sProtocol = "0.3"

        # name for owlfile
        self.sOwlFilename = "data/cache.txt"

        # url for owls
        self.sOwlUrl = "http://iowl.berlios.de/entry.pl"

        # use webowls
        self.bGetWebOwls = 0

        # minimun number of owls
        self.iMinOwls = 15

        # entryowl
        self.EntryIP = ''
        self.EntryPort = 2323

        # timetolive
        self.iTTL = 5

        # interval in secs to wait for PONGS
        self.iInterval = 300


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
            try:
                self.EntryIP = socket.gethostbyname(str(sValue))
            except socket.error:
                # cant resolve hostname
                pManager.manager.DebugStr('cNetManager '+ __version__ +': Warning: Can\'t resolve entryowl %s.' %(sValue, ), 0)
                self.EntryIP = ''
        elif sOption == 'entryport':
            self.iEntryPort = int(sValue)
        elif sOption == 'numneighbours':
            self.cOwlManager.SetNumNeighbours(int(sValue))
        elif sOption == 'maxowlstokeep':
            self.cOwlManager.SetMaxOwlsToKeep(int(sValue))
        elif sOption == 'listenport':
            # XXX Need to restart listener for changes to take effect!
            self.cNetServer.SetListenPort(int(sValue))
            if pManager.manager.IsRunning():
                pManager.manager.DebugStr('cNetManager '+ __version__ +': Warnig: change of listenport currently only takes effect after restart of iOwl.', 0)
        elif sOption == 'ttl':
            self.iTTL = int(sValue)
        elif sOption == 'interval':
            self.iInterval = int(sValue)
        elif sOption == 'requestlifetime':
            self.cOwlManager.SetRequestLifeTime(int(sValue))
        elif sOption == 'getwebowls':
            self.bGetWebOwls = int(sValue)
        else:
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Warning: unknown option %s' %(sOption, ), 0)


    def GetProtocolVersion(self):
        """return version of network protocol"""
        return self.sProtocol


    def GetNumKnownOwls(self):
        """return number of known neighbourowls"""
        return self.cOwlManager.GetNumKnownOwls()


    def GetNumActiveRoutings(self):
        """return number of active routing entries"""
        return self.cOwlManager.GetNumActiveRoutings()


    def GetRoutingTable(self):
        """return routing table"""
        return self.cOwlManager.GetRoutingTable()


    def GetNumPongsReceived(self):
        """return total number of Pongs received"""
        return self.cOwlManager.GetNumPongsReceived()


    def GetNumAnswersReceived(self):
        """return total number of Answers received"""
        return self.cOwlManager.GetNumAnswersReceived()


    def StartConnection(self):
        """Start network package

        Called by cNetworkInterface.
        Start new thread to call cNetServer.StartListen(), add EntryPoint to cOlwmanager,
        generate an initial PING and pass it to cOwlManager.Distribute()

        """

        pManager.manager.DebugStr('cNetManager '+ __version__ +': Starting connection.', 1)

        # start watchdog
        self.WatchDogID = pManager.manager.RegisterWatchdog(self.TimerTick, self.iInterval)

        # Start OwlManager
        self.cOwlManager.Start()

        # start thread for network initialization
        thread.start_new_thread(self.StartNetworking, ())


    def StartNetworking(self):
        """Start connection to iOwl-Network"""

        # Read cached owls
        self.ReadCache()

        # add entrypoint to cOwlManager
        if self.EntryIP != '':
            self.cOwlManager.AddOwl((self.EntryIP, self.iEntryPort))

        # validate list of owls
        self.cOwlManager.ValidateOwls()

        # do i need to look up more owls at website?
        if ((self.cOwlManager.GetNumKnownOwls() < self.iMinOwls) and (self.bGetWebOwls == 1)):
            thread.start_new_thread(self.GetWebOwls, ())

        # start server
        self.cNetServer.StartListen()

        # generate PING
        cPing = self.GeneratePing()

        # pass PING to cOwlManager
        self.cOwlManager.Distribute(cPing)


    def Stop(self):
        """Stop the network

        Stop cNetServer (cNetServer.StopListen())
        Stop cOwlManager

        """

        self.cNetServer.StopListen()
        self.WriteCache()
        self.cOwlManager.Shutdown()


    def ReadCache(self):
        """Read cached neighbourowls from file"""

        try:
            # open file
            owlfile = open(self.sOwlFilename, "r")
        except:
            # cant open file.
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Can\'t open owlfile.', 1)
            return

        pManager.manager.DebugStr('cNetManager '+ __version__ +': Reading cached neighbourowls.', 1)
        iOwls=0
        # read line by line
        line = owlfile.readline()
        while line:
            iOwls += 1
            line = line.strip()
            ip, port = line.split(':');
            owl = self.cOwlManager.AddOwl((ip, port));
            line = owlfile.readline()

        owlfile.close()
        pManager.manager.DebugStr('cNetManager '+ __version__ +': Read %s neigbourowls from cache.' % str(iOwls), 1)


    def WriteCache(self):
        """Write neighbourowls to file"""

        try:
            owlfile = open(self.sOwlFilename, "w");
        except:
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Cant open file for caching owls.', 0)
            return

        pManager.manager.DebugStr('cNetManager '+ __version__ +': Caching neighbourowls.', 1)
        iOwls=0
        for owl in self.cOwlManager.lKnownOwls:
            iOwls += 1
            owlfile.write("%s:%s\n" % (owl.GetIP(), owl.GetPort()))
        owlfile.close()
        pManager.manager.DebugStr('cNetManager '+ __version__ +': Saved %s neighbourowls in cache.' % str(iOwls), 1)


    def HandlePing(self, sPing, sOrigin):
        """Handle incoming Ping

        Called by CRPCRequestHandler.
        Parse params-string into DOM
        Pass Ping to cOwlManager.Distribute()
        Generate Answer-Pong.
        Pass Pong to cOwlManager.Answer()

        """

        try:
            # create cDOM from ascii-Ping
            domPing = cDOM.cDOM()
            domPing.ParseString(sPing)

            # create cNetPackage from DOM-Ping
            cPing = cNetPackage.cNetPackage('ping')
            cPing.ParseDOM(domPing)

            # set originator ip
            cPing.SetOriginatorIP(sOrigin)

            # log incoming ping
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Incoming Ping from %s:%s.' %(str(cPing.GetOriginator()[0]), str(cPing.GetOriginator()[1])), 2)

            # pass ping to cOwlManager. If cOwlManager accepts ping, answer with pong
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Distributing Ping.', 3)
            if self.cOwlManager.Distribute(cPing) == 'okay':
                # generate Pong
                try:
                    cPong = self.GeneratePong(cPing)
                except:
                    # Could not generate Pong
                    pManager.manager.DebugStr('cNetManager '+ __version__ +': Could not generate Pong.', 2)
                    return
                # pass Pong to cOlwManager
                pManager.manager.DebugStr('cNetManager '+ __version__ +': Answering with Pong.', 3)
                self.cOwlManager.Answer(cPong)
            else:
                # something was wrong with that Ping...
                pass
        except:
            # unknown error. log and forget.
            # get exception
            eType, eValue, eTraceback = sys.exc_info()

            # build stacktrace string
            tb = ''
            for line in traceback.format_tb(eTraceback, 15):
                tb = tb + line

            pManager.manager.DebugStr('pNetwork '+ __version__ +': Unhandled error in thread HandlePing(): Type: '+str(eType)+', value: '+str(eValue), 2)
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Traceback:\n'+str(tb), 2)



    def HandlePong(self, sPong, sOrigin):
        """Handle incoming Pong

        Called by CRPCRequestHandler.Pong().
        Reset LastNetAction-time.
        Pass PONG to cOwlManager.Answer().

        """

        try:
            # reset WatchDog
            pManager.manager.ResetWatchdog(self.WatchDogID)

            # create cDOM from ascii-Pong
            domPong = cDOM.cDOM()
            domPong.ParseString(sPong)
            # create cNetPackage from DOM-Pong
            cPong = cNetPackage.cPong()
            cPong.ParseDOM(domPong)

            # check if i am the first hop of this pong (answerer ip set to 127.0.0.1)
            # -> set answerer ip!
            if cPong.GetAnswerer()[0]=='127.0.0.1':
                pManager.manager.DebugStr('cNetManager '+ __version__ +': First hop. Setting Answerer IP to %s' % (sOrigin), 3)
                cPong.SetAnswererIP(sOrigin)

            # set originator ip
            cPong.SetOriginatorIP(sOrigin)

            # log incoming pong
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Incoming Pong from %s:%s' % (str(cPong.GetAnswerer()[0]), str(cPong.GetAnswerer()[1])), 2)

            # extract PONG-source and add to own list of owls
            self.ExtractPongSource(cPong)

            # pass to cOwlManager
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Passing Pong to cOwlManager.Answer()', 3)
            self.cOwlManager.Answer(cPong)
        except:
            # unknown error. log and forget.
            # get exception
            eType, eValue, eTraceback = sys.exc_info()

            # build stacktrace string
            tb = ''
            for line in traceback.format_tb(eTraceback, 15):
                tb = tb + line

            pManager.manager.DebugStr('pNetwork '+ __version__ +': Unhandled error in thread HandlePong(): Type: '+str(eType)+', value: '+str(eValue), 2)
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Traceback:\n'+str(tb), 3)


    def HandleRequest(self, sRequest, sOrigin):
        """Handle incoming Request

        Called by cRPCRequestHandler.Request().
        Pass Request to cOwlManager.Distribute() for further spreading.

        """

        try:
            # create cDOM from ascii-request
            domRequest = cDOM.cDOM()
            domRequest.ParseString(sRequest)
            # create cNetPackage from DOM-request
            cRequest = cNetPackage.cRecPackage('')
            cRequest.ParseDOM(domRequest)
            # set originator ip
            cRequest.SetOriginatorIP(sOrigin)
            # log incoming Request
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Incoming Request from %s:%s.' %(str(cRequest.GetOriginator()[0]), str(cRequest.GetOriginator()[1])), 2)
            # pass to cOwlManager
            self.cOwlManager.Distribute(cRequest)
        except:
            # unknown error. log and forget.
            # get exception
            eType, eValue, eTraceback = sys.exc_info()

            # build stacktrace string
            tb = ''
            for line in traceback.format_tb(eTraceback, 15):
                tb = tb + line

            pManager.manager.DebugStr('pNetwork '+ __version__ +': Unhandled error in thread HandleRequest(): Type: '+str(eType)+', value: '+str(eValue),2)
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Traceback:\n'+str(tb), 3)



    def HandleAnswer(self, sAnswer, sOrigin):
        """Handle incoming Answer

        Called by cRPCRequestHandler.Answer().
        Pass Answer to cOwlManager.Answer().

        """

        # log incoming Answer
        pManager.manager.DebugStr('cNetManager '+ __version__ +': Incoming Answer...', 1)

        try:
            # create cDOM from ascii-Ping
            domAnswer = cDOM.cDOM()
            domAnswer.ParseString(sAnswer)
            # create cNetPackage from DOM-answer
            cAnswer = cNetPackage.cRecPackage('')
            cAnswer.ParseDOM(domAnswer)
            # set originator ip
            cAnswer.SetOriginatorIP(sOrigin)
            # pass on to cOwlManager
            self.cOwlManager.Answer(cAnswer)
        except:
            # unknown error. log and forget.
            # get exception
            eType, eValue, eTraceback = sys.exc_info()

            # build stacktrace string
            tb = ''
            for line in traceback.format_tb(eTraceback, 15):
                tb = tb + line

            pManager.manager.DebugStr('pNetwork '+ __version__ +': Unhandled error in thread HandleAnswer(): Type: '+str(eType)+', value: '+str(eValue), 2)
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Traceback:\n'+str(tb), 3)


    def SendRequest(self, elRequest):
        """process request by own pRecommendation package.

        Called by pNetworkInterface.SendRequest().
        Generate Request and pass it to cOwlManager for distribution

        elRequest   -- Request from pRecommendation

        return      -- new id generated for request


        """

        # Build network package containing request
        cRequest = self.GenerateRequest(elRequest)

        # Pass Request to cOwlManager
        pManager.manager.DebugStr('pNetwork '+ __version__ +': Passing request to network.', 2)
        if self.cOwlManager.Distribute(cRequest) == 'okay':
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Passed Request -> Okay.', 2)
        else:
            pManager.manager.DebugStr('pNetwork '+ __version__ +': Passed Request -> Error!.', 2)

        # return id for pRecommendation
        return cRequest.GetID()



    def SendAnswer(self, elAnswer, id):
        """process Answer by own pRecommendation

        Called by pNetworkInterface.SendAnswer()

        Generate Answer and pass it on to cOwlManager

        elAnswer    -- Answer from pRecommendation
        id          -- id of corresponding Request, needed to figure out the routing of answer

        """

        # Build network package containing answer
        pManager.manager.DebugStr('pNetwork '+ __version__ +': Generating Answer.', 2)
        cAnswer = self.GenerateAnswer(elAnswer, id)

        # pass Answer to cOwlManager
        pManager.manager.DebugStr('pNetwork '+ __version__ +': Passing answer to network.', 2)
        self.cOwlManager.Answer(cAnswer)



    def TimerTick(self):
        """Watchdog for network

        Called by Timer after <interval> seconds of no network activity.

        """
        # log tick
        pManager.manager.DebugStr('cNetManager '+ __version__ +': No PONG received for '+str(self.iInterval)+' seconds. Generating PING.', 2)

        # if i know no owl, try to add entryowl
        if (self.cOwlManager.GetNumKnownOwls() == 0):
            if self.EntryIP != '':
                self.cOwlManager.AddOwl((self.EntryIP, self.iEntryPort))

        # Generate Ping
        ping = self.GeneratePing()
        self.cOwlManager.Distribute(ping)


    def GeneratePing(self):
        """Generate and return a cNetPackage object"""

        # generate ping
        cPing = cNetPackage.cNetPackage('ping')
        # set unique id
        cPing.SetID(pManager.manager.GetUniqueNumber())
        # set originator
        cPing.SetOriginatorPort(self.cNetServer.GetListenPort())
        # set iOwl-Version
        cPing.SetOwlVersion(pManager.manager.GetVersion())
        # set network protocol version
        cPing.SetProtocolVersion(self.sProtocol)
        # set ttl
        cPing.SetTTL(self.iTTL)

        return cPing


    def GeneratePong(self, cPing):
        """Generate and return a cPong Object"""

        # generate pong
        cPong = cNetPackage.cPong()
        # set id from ping
        cPong.SetID(cPing.GetID())
        # set originator
        cPong.SetOriginatorPort(self.cNetServer.GetListenPort())
        # set iOwl-Version
        cPong.SetOwlVersion(pManager.manager.GetVersion())
        # set network protocol version
        cPong.SetProtocolVersion(self.sProtocol)
        # set answererPort
        cPong.SetAnswererPort(self.cNetServer.GetListenPort())

        return cPong


    def GenerateRequest(self, elRequest):
        """Generate a request

        elRequest  -- Request as generated by pRecommendation

        return     -- cNetpackage

        """

        # generate request
        cRequest = cNetPackage.cRecPackage('request')
        # set unique id
        cRequest.SetID(pManager.manager.GetUniqueNumber())
        # set originator
        cRequest.SetOriginatorPort(self.cNetServer.GetListenPort())
        # set iOwl-Version
        cRequest.SetOwlVersion(pManager.manager.GetVersion())
        # set network protocol version
        cRequest.SetProtocolVersion(self.sProtocol)
        # store elRequest
        cRequest.StorePayload(elRequest)
        # set ttl
        cRequest.SetTTL(self.iTTL)

        return cRequest


    def GenerateAnswer(self, elAnswer, id):
        """Generate complete Answer-package containing elRequest

        elAnswer    -- Answer as generated by pRecommendation
        id          -- id Answer should contain (id of request this answer belongs to. Needed to figure the
                       correct routing in cOwlManager

        return      -- cNetpackage

        """

        # generate answer
        cAnswer = cNetPackage.cRecPackage('answer')
        # set id
        cAnswer.SetID(id)
        # set originator
        cAnswer.SetOriginatorPort(self.cNetServer.GetListenPort())
        # set iOwl-Version
        cAnswer.SetOwlVersion(pManager.manager.GetVersion())
        # set network protocol version
        cAnswer.SetProtocolVersion(self.sProtocol)
        # store elRequest
        cAnswer.StorePayload(elAnswer)

        return cAnswer


    def ExtractPongSource(self, cPong):
        """Extract source of PONG

        Add new owl (Pong-source) to cOwlmanager's list of known owls.

        """
        self.cOwlManager.AddOwl(cPong.GetAnswerer())



    def GetWebOwls(self):
        """Connect to url and get a csv of owls

        List format:
            ip,ip,ip,ip...
        does not contain ports -> Use default port.

        """

        try:
            # get list from url
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Not enough owls in cache. Getting some more owls from website.', 1)
            sList = urllib.urlopen(self.sOwlUrl).read()
            lOwls = sList.split(",")
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Got '+str(len(lOwls))+' IPs from website. Now validating...', 1)
            for owl in lOwls:
                try:
                    # create socket
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # if connection to iOwl-port fails, owl is invalid
                    s.connect((owl, int(self.cNetServer.GetListenPort())))
                    s.close()
                except:
                    pManager.manager.DebugStr('cNetManager '+ __version__ +': Detected stale owl. Discarding...', 2)
                    continue

                pManager.manager.DebugStr('cNetManager '+ __version__ +': Detected active owl. Adding to neighbourlist...', 2)
                self.cOwlManager.AddOwl((owl, self.cNetServer.GetListenPort()))

        except:
            pManager.manager.DebugStr('cNetManager '+ __version__ +': Could not connect to website.', 1)
























#############################################################################
## TEST FUNCTIONS ###########################################################

def test():
    manager = cNetManager()
    manager.cNetServer.SetListenPort(2323)
    manager.iTTL = 10
    dummy = cDOM.cDOM()
    elReq = dummy.CreateElement('request', {'url':'iowl.berlios.de', 'otherurl':'www.arschlecken.de'}, 'Bitte recommendation liefern!')
    elAns = dummy.CreateElement('answer', {'url':'www.wissen.de'}, 'Check das aus!')
    re = manager.GenerateRequest(elReq)
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



