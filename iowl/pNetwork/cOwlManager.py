
__version__ = "$Revision: 1.27 $"

"""
$Log: cOwlManager.py,v $
Revision 1.27  2002/02/22 15:48:59  Saruman
recommendations should work again *sigh*

Revision 1.26  2002/02/22 12:06:15  Saruman
added comments.
added sanity check to detect broken routing table.
Now answering requests even when ttl is expired and request does not get forwarded.

Revision 1.25  2002/02/21 15:48:59  Saruman
Bugfix for routing-mutex.
Temporary disabled ValidateOwl().

Revision 1.24  2002/02/21 13:57:14  Saruman
Of course, never executed code never gets tested.
Fixed.

Revision 1.23  2002/02/21 13:49:45  Saruman
Fixed totally dumb bug for counting answers. Code was never executed.
C0-Ueberdeckungstests anyone? ;-)

Introduced mutex for modifying entries in Routing Table.
PONGS circulating forever should be fixed now.

Revision 1.22  2002/02/21 12:46:18  Saruman
Added routingtable to statistics page

Revision 1.21  2002/02/14 08:31:49  Saruman
cleanups, comments etc.

Revision 1.20  2002/02/13 10:46:22  Saruman
introduced counters and functions for gathering network stats.

Revision 1.19  2002/02/11 16:16:22  Saruman
Fixed bug when validating cached owls.
Now should be able to validate all cached owls, not just the first.

Revision 1.18  2002/02/11 15:12:38  Saruman
Major network changes.
Network protocol now 0.3, incompatible to older versions!
Should fix all problems regarding the detection of own ip and enable use of iOwl behind a firewall.

Revision 1.17  2001/08/10 18:35:59  i10614
more debug output.
added debuglevel to all messages.
minor cleanups.

Revision 1.16  2001/07/15 10:21:33  i10614
added verbose debug output for different network version conflicts

Revision 1.15  2001/06/10 15:56:08  i10614
debug output fixes

Revision 1.14  2001/06/05 18:22:42  i10614
removed irritating debug output.

Revision 1.13  2001/05/30 20:30:02  i10614
shortened debug output

Revision 1.12  2001/05/07 07:39:36  i10614
added mutex for neighbour-handling

Revision 1.11  2001/04/22 18:55:40  i10614
bugfix for validating neighbourowls

Revision 1.10  2001/04/22 13:27:51  i10614
extended owl-caching -> now verifying old owls

Revision 1.9  2001/04/15 21:28:58  i10614
Test: Not deleting owls involved in vicious circles

Revision 1.8  2001/04/15 21:16:22  i10614
fixed for recommendations and answers

Revision 1.7  2001/04/15 19:58:48  i10614
fixes for recomendations

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

Revision 1.1.1.1  2001/03/24 19:22:47  i10614
Initial import to stio1 from my cvs-tree

Revision 1.29  2001/03/18 15:49:51  mbauer
added try-except in cOwlManager.Answer()

Revision 1.28  2001/03/17 14:59:24  mbauer
added user-defined exceptions for parsing network packets

Revision 1.27  2001/02/25 14:12:59  mpopp
fixed spelling

Revision 1.26  2001/02/22 12:48:30  mbauer
fixed bug for sending requests

Revision 1.25  2001/02/22 12:32:40  mbauer
fixed bugs in SendRequest/SendAnswer

Revision 1.24  2001/02/21 18:14:36  mbauer
added Garbage collector for old entries in request-table

Revision 1.23  2001/02/19 19:19:52  mbauer
Added algorithm to detect the correct IP adress when having more than one interface

Revision 1.21  2001/02/18 20:23:26  mbauer
added new XXX... :-/

Revision 1.20  2001/02/17 16:57:41  mbauer
cosmetic changes

Revision 1.6  2001/02/17 01:24:42  mbauer
bugfixes...

Revision 1.3  2001/02/16 12:02:49  mbauer
added DeleteOwl()

Revision 1.1  2001/02/15 23:02:46  mbauer
inital check-in


"""

import pManager
import cNetManager
import cNetException
import cNeighbourOwl
import cDOM
import thread
import time
import sys
import socket

class cOwlManager:
    """Coordinator class for neighbour owls

    Responsible for routing of all network packages

    Organisiation of requests dictionary:
    key = global unique identifier of request
    value = list containing:    - origination Owl (cNeighbourOwl Object)
                                - Number of allowed Answers
                                - Number of received Answers
                                - Creation time of entry


    """

    def __init__(self, cNetManager):
        """Constructor"""

        # some magic numbers for request dictionary values for easy list index access
        self.SourceOwl = 0
        self.iMaxAnswers = 1
        self.iRecvdAnswers = 2
        self.iTimeCreated = 3

        # store my cNetManager
        self.cNetManager = cNetManager

        # init list of owls
        self.lKnownOwls = []

        # init dictionary of requests
        self.dRequests = {}

        # maximum number of known owls
        self.iMaxOwlsToKeep = 50

        # number of neighbour owls (number of owls requests are sent to)
        self.iNumNeighbours = 5

        # time requests are valid - default 5 minutes
        self.iRequestLifeTime = 300

        # mutex for adding/removing owls
        self.OwlLock = thread.allocate_lock()

        # mutex for adding/removing routing entries
        self.RouteLock = thread.allocate_lock()

        # total number of pongs received for myself
        self.iNumPongsReceived = 0

        # total number of answers received for myself
        self.iNumAnswersReceived = 0


    def SetNumNeighbours(self, neighbours):
        """Set number of neighbour owls"""
        self.iNumNeighbourOwls = neighbours


    def SetMaxOwlsToKeep(self, maxOwls):
        """Set max number of owls in list of known owls"""
        self.iMaxOwlsToKeep = maxOwls


    def GetNumPongsReceived(self):
        """return total number of Pongs received"""
        return self.iNumPongsReceived


    def GetNumAnswersReceived(self):
        """return total number of Answers received"""
        return self.iNumAnswersReceived


    def SetRequestLifeTime(self, iTime):
        """Set lifetime for requests

        XXX - This needs to be dependant on TTL of request!

        """
        self.iRequestLifeTime = iTime


    def AddOwl(self, tOrig):
        """Add new owl to list of known owls and return it

        If owl is already in list, just return that owl.

        XXX -- Todo: take care of MaxOwlsToKeep! Cause if list gets
               too large, operations may take too long since its
               a dumb "look-in-every-single-object-and-compare" - operation...

        ip     -- ip adress of owl
        port   -- port of owl

        return -- cNeighbourOwl Object with new or already existing owl

        """

        # dont add localhost - return owl object without adding to list
        if (str(tOrig[0])=='127.0.0.1') or (str(tOrig[0])=='localhost'):
            return cNeighbourOwl.cNeighbourOwl(tOrig[0], tOrig[1], self)

        # Acquire Lock
        self.OwlLock.acquire()

        # look if owl is kown already
        for owl in self.lKnownOwls:
            if (str(owl.IP) == str(tOrig[0])) and (str(owl.iPort) == str(tOrig[1])):
                # already there -> return old owl
                # release Lock
                self.OwlLock.release()
                return owl

        # okay, this is a new owl.
        newOwl = cNeighbourOwl.cNeighbourOwl(tOrig[0], tOrig[1], self)

        # log
        pManager.manager.DebugStr('cOwlManager '+ __version__ +': Adding owl at '+ str(tOrig[0]) + ':' + str(tOrig[1]) +'.', 4)

        # Add to list
        self.lKnownOwls.append(newOwl)

        # release Lock
        self.OwlLock.release()

        # return owl
        return newOwl


    def DeleteOwl(self, lOwlList, tOwl):
        """Delete an owl from lOwlList"""

        # Acquire Lock
        self.OwlLock.acquire()

        # look for owl
        for owl in lOwlList:
            if str(owl.IP) == str(tOwl[0]) and str(owl.iPort) == str(tOwl[1]):
                # found! Now delete it
                lOwlList.remove(owl)
                # release Lock
                self.OwlLock.release()
                return

        # Uh-oh. Trying to delete non-existing owl?
        # release Lock
        self.OwlLock.release()
        return


    def IsValidPackage(self, cNetPackage):
        """Check if a network package is valid

        return 0 if broken,
               1 if okay.

        """

        # check protocol version
        if cNetPackage.GetProtocolVersion() != self.cNetManager.sProtocol:
            # wrong protocol version. Log error, throw domObj away and continue operation
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Warning: Received NetPackage with different network version. Mine: '+str(self.cNetManager.sProtocol)+', other: '+str(cNetPackage.GetProtocolVersion()), 2)
            return 0

        # check type of domObj
        if cNetPackage.GetType() not in ('ping', 'request'):
            # unknown type. Log error, throw domObj away and continue operation
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Warning: Received unknown Dom type "'+cNetPackage.GetType()+'".', 2)
            return 0

        # check for circular structures. If id of request is already in request-list -> Throw away!
        if cNetPackage.GetID() in self.dRequests.keys():
            # Log error, throw domObj away and continue operation
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Warning: Detected vicious circle.', 3)
            return 0

        # ok, request is valid and can be sent out.
        return 1


    def Distribute(self, cNetPackage):
        """Pass cNetPackage to all Neighbourowls.

        cNetPackage is either a PING or a REQUEST. Called by cNetManager.HandlePing(),
        cNetManager.HandleRequest() or cNetManager.SendRequest().
        Pass Request to pRecommendationInterface (except it is from own owl).
        Decrement TTL of cNetPackage.
        Pass cNetPackage on through the network

        cNetPackage -- NetPackage to pass around (PING or REQUEST)

        returns:    'okay' if cNetPackage is accepted
                    'error' else

        """

        # lock routing table
        self.RouteLock.acquire()

        # check package
        if not self.IsValidPackage(cNetPackage):
            self.RouteLock.release()
            return 'error'

        # Get cNeighbourOwl Object that sent me this request
        OrigOwl = self.AddOwl(cNetPackage.GetOriginator())

        # Create list of request attributes
        lReqAttributes = range(4)
        lReqAttributes[self.SourceOwl] = OrigOwl                    # owl that i received this request from
        lReqAttributes[self.iMaxAnswers] = 2*cNetPackage.GetTTL()   # number of allowed answers. Dependant on TTL
        lReqAttributes[self.iRecvdAnswers] = 0                      # not yet received any answer
        lReqAttributes[self.iTimeCreated] = time.time()             # timestamp when request was created

        # Add request to request-dictionary.
        self.dRequests[cNetPackage.GetID()] = lReqAttributes

        # release routing table
        self.RouteLock.release()

        # if TTL reached zero -> dont distribute request any further
        if cNetPackage.GetTTL() <= 0:
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Request "'+str(cNetPackage.GetID())+'" reached TTL 0. No more distributing.', 3)
            # although ttl is expired, we still want to answer, if it is a request
            if cNetPackage.GetType() == 'request':
                # Although it should not happen that a request with ttl 0 was created by myself, check it for sanity reasons
                if (OrigOwl.GetIP()!=pManager.manager.GetOwnIP()) or (str(OrigOwl.GetPort())!=str(self.cNetManager.cNetServer.GetListenPort())):
                    # ok, request was not generated by myself.
                    pManager.manager.DebugStr('cOwlManager '+ __version__ +': Passing new request to own pRecommendation.', 3)
                    # Get Request element from domObj
                    elRequest = cNetPackage.GetPayload()
                    # get pRecommandationInterface from manager
                    pRecIntf = pManager.manager.GetRecommendationInterface()
                    # pass request and it's id to pRecommendation
                    pRecIntf.SetRequest(elRequest, cNetPackage.GetID())

            # return okay cause cNetPackage is accepted regardless of ttl.
            # it just does not get distributed further.
            return 'okay'

        # decrement TTL
        cNetPackage.DecrementTTL()


        #############################
        # Now pass dom to neighbours#
        #############################

        # get list of Owls to pass to.
        # XXX - pretty braindead, just take a slice of lKnownOwls with size self.iNumNeighbours. Should
        #       include more intelligence in selecting target owls.
        if len(self.lKnownOwls) > self.iNumNeighbours:
            # i know more owls than i need -> just take a slice with desired size, beginning with first owl.
            lNeighbours = self.lKnownOwls[:self.iNumNeighbours]
        else:
            # i dont know enough owls -> Use whole list for distribution!
            # need a deep copy of list, not just reference...
            lNeighbours = self.lKnownOwls[:]

        # remove originating owl from list of target owls - dont want to send package back to where it came from!
        self.DeleteOwl(lNeighbours, cNetPackage.GetOriginator())

        # remove myself from neighbours - dont want to send to myself!
        # XXX This should be unnecessary, localhost never gets added to list!
        self.DeleteOwl(lNeighbours, (pManager.manager.GetOwnIP(), self.cNetManager.cNetServer.GetListenPort()))

        # now replace originator port of netpackage with my own port
        # NOTE: Dont set my ip here, it will get set by the owl receiving the package!
        cNetPackage.SetOriginatorPort(self.cNetManager.cNetServer.GetListenPort())

        # Generate debug info
        distri = []
        for i in lNeighbours:
            distri.append(str(i.IP) +':'+ str(i.iPort))
        pManager.manager.DebugStr('cOwlManager '+ __version__ +': Distributing to '+str(len(distri))+' owls.', 3)

        # Get cDom-representation of cNetPackage
        domObj = cNetPackage.GetDOM()

        # convert dom to ascii-string for network transport
        # XXX - This may be unneccessary with new release of xmlrpclib!
        sObj = str(domObj.ToXML())

        # Finally start sending
        if cNetPackage.GetType()=='ping':
            # call ping()
            for owl in lNeighbours:
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': Sending Ping to '+str(owl.IP)+':'+str(owl.iPort)+'.', 4)
                # start new thread for each RPC
                thread.start_new_thread(owl.Ping, (sObj,))
            return 'okay'

        elif cNetPackage.GetType()=='request':
            # call remote owl's Request()
            for owl in lNeighbours:
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': Sending Request to '+str(owl.IP)+':'+str(owl.iPort)+'.', 4)
                # start new thread for each RPC
                thread.start_new_thread(owl.Request, (sObj,))

            # pass request to own pRecommendation unless it was issued by myself
            if (OrigOwl.GetIP()!=pManager.manager.GetOwnIP()) or (str(OrigOwl.GetPort())!=str(self.cNetManager.cNetServer.GetListenPort())):
                # ok, request was not generated by myself.
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': Passing new request to own pRecommendation.', 3)
                # Get Request element from domObj
                elRequest = cNetPackage.GetPayload()
                # get pRecommandationInterface from manager
                pRecIntf = pManager.manager.GetRecommendationInterface()
                # pass request and it's id to pRecommendation
                pRecIntf.SetRequest(elRequest, cNetPackage.GetID())

            return 'okay'

        # should never happen!
        return 'error'


    def Answer(self, cNetPackage):
        """Send an Answer to it's destination owl

        Answer is either a PONG or an ANSWER. Called by cNetManager.HandleAnswer().

        cNetPackage -- network package to send back

        """

        # look in requests dictionary for originating owl of request
        try:
            reqAttributes = self.dRequests[cNetPackage.GetID()]
            origOwl = reqAttributes[self.SourceOwl]
            # validate origOwl
            test = origOwl.iPort
        except:
            # id no longer exists in requests table. Probably request expired or max
            # number of answers reached.
            # Throw away answer and continue operation
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Received answer for non-existant request. Throwing away..', 2)
            return


        # check type of domObj
        if cNetPackage.GetType() not in ('pong', 'answer'):
            # unknown type. Log error, throw domObj away and continue operation
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Warning: Received unknown Dom type "'+cNetPackage.GetType()+'" as Answer. Skipping...', 2)
            return


        # sanity check: never forward PONG to original creator of PONG (Answerer)
        if cNetPackage.GetType() == 'pong':
            # print "Checking PONG source..."
            # print "Answerer: "+str(cNetPackage.GetAnswerer())
            # print "Routing to: "+str(origOwl.GetIP())+":"+str(origOwl.GetPort())
            if ((origOwl.GetIP()==str(cNetPackage.GetAnswerer()[0])) and (origOwl.GetPort()==str(cNetPackage.GetAnswerer()[1]))):
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': Warning: Inconsistent routing table! Routing Id: "'+cNetPackage.GetID() + "IP: "+origOwl.GetIP(), 2)
                return


        # look if request was created by myself
        if (str(reqAttributes[self.SourceOwl].IP)    == str(pManager.manager.GetOwnIP())) and \
           (str(reqAttributes[self.SourceOwl].iPort) == str(self.cNetManager.cNetServer.GetListenPort())):
            # answer for myself!
            if cNetPackage.GetType() == 'pong':
                # Pong info already extracted inside cNetManager.HandlePong().
                # just throw away and continue
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': Received Pong for myself.', 3)
                # count Pong
                self.iNumPongsReceived += 1
                # finish answer
                self.FinishAnswer(reqAttributes, cNetPackage)
                return
            elif cNetPackage.GetType() == 'answer':
                # Pass it to pRecommendationInterface
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': Received Answer for myself. Passing on to pRecommendation.', 3)
                # Get Answer element from cNetPackage
                elAnswer = cNetPackage.GetPayload()
                # Get recommendation interface from pManager.
                pRecIntf = pManager.manager.GetRecommendationInterface()
                pRecIntf.SetAnswer(elAnswer, cNetPackage.GetID())
                # count Answer
                self.iNumAnswersReceived += 1
                # finish answer
                self.FinishAnswer(reqAttributes, cNetPackage)
                return
            else:
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': domType Error! Should never get here!', 1)
                return


        # must be answer for another owl

        # Get cDom-representation of cNetPackage
        domObj = cNetPackage.GetDOM()

        # convert dom to ascii-string for network transport
        # XXX - This may be unneccessary with new release of xmlrpclib!
        sObj = str(domObj.ToXML())

        if cNetPackage.GetType() == 'pong':
            # Pong info already extracted inside cNetManager.HandlePong().
            # just pass Pong on to originating Owl and continue
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Sending Pong to '+str(origOwl.GetIP())+':'+str(origOwl.GetPort())+'.', 4)
            # start new thread for RPC
            thread.start_new_thread(origOwl.Pong, (sObj,))
            # finish answer
            self.FinishAnswer(reqAttributes, cNetPackage)
            return
        elif cNetPackage.GetType() == 'answer':
            # Pass answer to originating Owl and continue
            # start new thread for RPC
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Sending Answer to '+str(origOwl.GetIP())+':'+str(origOwl.GetPort())+'.', 4)
            thread.start_new_thread(origOwl.Answer, (sObj,))
            # finish answer
            self.FinishAnswer(reqAttributes, cNetPackage)
            return
        else:
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': domType Error! Should never get here!', 1)
            return


    def FinishAnswer(self, reqAttributes, cNetPackage):
        """Finish handling of incoming answer

        Main purpose: increment and check answercounters
        """

        # increment answer counter for request
        tmp = reqAttributes[self.iRecvdAnswers]
        reqAttributes[self.iRecvdAnswers] = tmp+1

        # if answercounter > maxanswers -> delete request from requests dictionary!
        if reqAttributes[self.iRecvdAnswers] > reqAttributes[self.iMaxAnswers]:
            # request reached max answer count.
            # delete it from request dictionary.
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': MaxAnswers reached for request "'+cNetPackage.GetID()+'". Deleting it from dictionary.', 3)

            # lock Routing Table
            self.RouteLock.acquire()
            # request might be deleted while waiting for lock -> ignore failing deletion
            try:
                del self.dRequests[cNetPackage.GetID()]
            except:
                # release Routing Table
                self.RouteLock.release()
                pass

            # release Routing Table
            self.RouteLock.release()


    def Start(self):
        """Start operation of cOwlManager.

        purpose: register CleanOldRequest-Function with pManager.
        """

        # Check every 10 minutes for expired entries in requesttable
        pManager.manager.RegisterWatchdog(self.CleanOldRequests, 600)



    def Shutdown(self):
        """Stop working."""
        pass


    def CleanOldRequests(self):
        """Clean requests from expired entrys

        Get called by external timer-thread.

        """

        # get current time
        fTime = time.time()

        iNumDeleted = 0

        # lock routing table
        self.RouteLock.acquire()

        for id in self.dRequests.keys():
            if (fTime - self.dRequests[id][self.iTimeCreated]) > self.iRequestLifeTime:
                # this request is expired! Delete it
                del self.dRequests[id]
                iNumDeleted = iNumDeleted + 1

        # release routing table
        self.RouteLock.release()

        if iNumDeleted > 1:
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Cleaned Requeststable from expired entries. Deleted: '+str(iNumDeleted)+', remaining: '+str(len(self.dRequests.keys())), 3)

        return


    def ValidateOwls(self):
        """Validate list of neighbour owls

        Called after start to validate cached owls.

        """

        # XXX Does not work that way. Deleting list while iterating it??
        # Fix later...
        return

        #for owl in self.lKnownOwls:
        #    try:
        #        # create socket
        #        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #        s.connect((owl.GetIP(), int(owl.GetPort())))
        #        pManager.manager.DebugStr('cOwlManager '+ __version__ +': validated owl %s:%s.' %(str(owl.GetIP()), str(owl.GetPort())), 3)
        #        s.close()
        #    except:
        #        pManager.manager.DebugStr('cOwlManager '+ __version__ +': Removing unreachable owl %s:%s.' %(str(owl.GetIP()), str(owl.GetPort())), 3)
        #        self.DeleteOwl(self.lKnownOwls, (owl.GetIP(), owl.GetPort()))



    def GetNumKnownOwls(self):
        """return number of known neighbourowls"""
        return len(self.lKnownOwls)


    def GetNumActiveRoutings(self):
        """return number of active routing entries"""
        return len(self.dRequests)


    def GetRoutingTable(self):
        """return routing table"""
        return self.dRequests















#########################################################################
### Test Functions

def test():
    x="x"
    om = cOwlManager(x)
    # Add three owls
    o1 = om.AddOwl(('1.2.3.4', 4096));
    o2 = om.AddOwl(('1.2.3.5', 4096));
    o3 = om.AddOwl(('1.2.3.6', 4096));
    om.Start()

    om.Shutdown()


if __name__=="__main__":
    test()


def GetDomInfo(self, domObj):
    """Extract information from dom

    if name of root-object does not match raise exception "DOM-Error".
    if version or protocol-version of dom does not match raise exception "Version-Error".

    domObj -- dom to examine

    returns list containing:

        version -- version of originating owl
        protocol-- network protocol version
        id      -- dom id
        type    -- dom type (Ping, Pong, Request, Answer)
        ttl     -- TimeToLive for dom
        orgIP   -- originating owl's IP
        orgPort -- originating owl's port

    """

    # Get Root Element
    root = domObj.GetRootElement()
    # Get Name of RootElement
    rootname = domObj.GetName(root)
    # check name
    if rootname != 'iowl.net':
        # This is not a valid iOwl.net Network package!
        raise cNetException.domError('invalid DOM')

    # get Attributes of root elem
    # list of attributes
    lAttrs = ['version', 'protocol', 'id', 'type', 'ttl']
    dAttrs = domObj.GetAttrs(root, lAttrs)
    version = dAttrs['version']
    protocol = dAttrs['protocol']
    id = dAttrs['id']
    type = dAttrs['type']
    ttl = dAttrs['ttl']

    # check for same version
    if version != pManager.manager.GetVersion():
        # dom was generated by an owl with another Version.
        raise cNetException.versionError('DOM has wrong version '+str(version))

    # check for same network version
    if protocol != self.cNetManager.sProtocol:
        # dom was generated by an owl with another network version.
        raise cNetException.versionError('DOM has wrong network version '+str(protocol))

    # get childelements
    childs = []
    dAttrs, childs = domObj.GetElementContainerContent(root, rootname, lAttrs)

    # search for element named 'originator' in childs
    originator = None
    for child in childs:
        childname = domObj.GetName(child)
        if childname == 'originator':
            originator = child

    if originator == None:
        # could not parse!
        raise cNetException.domError('invalid DOM - no originator found.')


    # get attributes of originator
    lOriginAttrs = ['ip','port']
    dOriginAttrs = domObj.GetAttrs(originator, lOriginAttrs)
    ip = dOriginAttrs['ip']
    port = dOriginAttrs['port']

    return version, protocol, id, type, ttl, ip, port


def ReplaceOrigin(self, domObj):
    """Replace origin of DOM with myself

    returns new DOM

    """

    # Get RootElement
    root = domObj.GetRootElement()

    # Get Name of RootElement
    rootname = domObj.GetName(root)

    # get childelements
    childs = []
    lAttrs = ['version', 'protocol', 'id', 'type', 'ttl']
    dAttrs, childs = domObj.GetElementContainerContent(root, rootname, lAttrs)

    # search for element named 'originator' in childs
    for child in childs:
        childname = domObj.GetName(child)
        if childname == 'originator':
            originator = child

    # get attributes of originator
    lOriginAttrs = ['ip','port']
    dOriginAttrs = domObj.GetAttrs(originator, lOriginAttrs)
    ip = dOriginAttrs['ip']
    port = dOriginAttrs['port']

    # get own IP from manager
    ownip = pManager.manager.GetOwnIP()
    # ownip = '1.2.3.4'

    # get ListenPort from cNetServer
    iListenPort = self.cNetManager.cNetServer.GetListenPort()

    # create new originator element
    newOrig = domObj.CreateElement('originator', {'ip':str(ownip), 'port':str(iListenPort)}, '')

    # store all childs of rootnode
    dAttr, lChilds = domObj.GetElementContainerContent(root, 'iowl.net', lAttrs)

    # search and delete originator in lChilds
    for child in lChilds:
        if domObj.GetName(child) == 'originator':
            lChilds.remove(child)

    # add new originator to list
    lChilds.append(newOrig)

    # generate new dom
    newDomObj = cDOM.cDOM()

    # generate new rootelement (==Elementcontainer)
    newroot = newDomObj.CreateElementContainer('iowl.net',
                                            {'version':dAttrs['version'],
                                                'protocol':dAttrs['protocol'],
                                                'id':dAttrs['id'],
                                                'type':dAttrs['type'],
                                                'ttl':dAttrs['ttl']
                                            },
                                            lChilds)

    # set as rootnode
    newDomObj.SetRootElement(newroot)

    # return new dom
    return newDomObj


def DecrementDomTTL(self, domObj):
    """Decrement TTL of given domObj

    XXX This is really ugly, there is no function available to change an
        attribute of a DOM 'on-the-fly', i have to build a new DOM just to
        decrement a counter.
        oh well...

    """

    # get element containing attribute 'ttl' -> root element
    root = domObj.GetRootElement()

    # get attributes of root element
    lAttrs = ['version', 'protocol',  'id', 'type', 'ttl']
    dAttrs = domObj.GetAttrs(root, lAttrs)

    # get current ttl
    iCurTTL = int(dAttrs['ttl'])

    if iCurTTL <= 0:
        # PANIC!
        raise 'TTL zero or below zero prior to decrementing!'

    # store all childs of rootnode
    dAttr, lChilds = domObj.GetElementContainerContent(root, 'iowl.net', lAttrs)

    # generate new dom
    newDomObj = cDOM.cDOM()

    # generate new rootelement (==Elementcontainer)
    newroot = newDomObj.CreateElementContainer('iowl.net',
                                            {'version':dAttrs['version'],
                                                'protocol':dAttrs['protocol'],
                                                'id':dAttrs['id'],
                                                'type':dAttrs['type'],
                                                'ttl':str(iCurTTL -1)
                                            },
                                            lChilds)

    # set as rootnode
    newDomObj.SetRootElement(newroot)

    # return new dom
    return newDomObj


def GetElementFromDOM(self, domObj, sElementName):
    """Extract element from domObj

    domObj is a network package. I need to return the element named sElementName.

    return  -- cDOM.element

    """

    # Get list of child-elements
    lElements = domObj.GetElements()

    # Get element named "answer"
    element = None
    for el in lElements:
        if domObj.GetName(el) == sElementName:
            element = el
            break

    if element == None:
        # print domObj.ToXML()
        raise 'Could not extract element from DOM!'

    # okay, return element
    return element


