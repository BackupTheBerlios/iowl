
__version__ = "$Revision: 1.5 $"

"""
$Log: cOwlManager.py,v $
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

class cOwlManager:
    """Coordinator class for neighbour owls

    Responsible for routing of all network packages

    Organisiation of requests dictionary:
    key = global unique identifier of request
    value = list containing:    - origination Owl (cNeighbourOwl Object)
                                - List of Olws request is sent to (cNeighbourOwl objects)
                                - Number of allowed Answers
                                - Number of received Answers

    XXX Need some mechanism to clean old entrys in request table!!

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

        # name for owlfile
        self.sOwlFilename="owls.txt"

        # init dictionary of requests
        self.dRequests = {}

        # maximum number of known owls
        self.iMaxOwlsToKeep = 50

        # number of neighbour owls (number of owls requests are sent to)
        self.iNumNeighbours = 5

        # time requests are valid - default 5 minutes
        self.iRequestLifeTime = 300


    def SetNumNeighbours(self, neighbours):
        """Set number of neighbour owls"""
        self.iNumNeighbourOwls = neighbours


    def SetMaxOwlsToKeep(self, maxOwls):
        """Set max number of owls in list of known owls"""
        self.iMaxOwlsToKeep = maxOwls


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

        # look if owl is kown already
        for owl in self.lKnownOwls:
            if (str(owl.IP) == str(tOrig[0])) and (str(owl.iPort) == str(tOrig[1])):
                # already there -> return old owl
                return owl

        # okay, this is a new owl.
        newOwl = cNeighbourOwl.cNeighbourOwl(tOrig[0], tOrig[1], self)

        # Add to list and return new owl
        self.lKnownOwls.append(newOwl)
        return newOwl


    def DeleteOwl(self, lOwlList, tOwl):
        """Delete an owl from lOwlList"""

        # look for owl
        for owl in lOwlList:
            if (owl.IP == tOwl[0]) and (owl.iPort == tOwl[1]):
                # found! Now delete it
                lOwlList.remove(owl)
                return

        # Uh-oh. Trying to delete non-existing owl?
        return


    def IsValidPackage(self, cNetPackage):
        """Check if a network package is valid

        return 0 if broken,
               1 if okay.

        """

        # check protocol version
        if cNetPackage.GetProtocolVersion() != self.cNetManager.sProtocol:
            # wrong protocol version. Log error, throw domObj away and continue operation
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Warning: Received NetPackage with different network version for distribution. Skipping...')
            return 0

        # check type of domObj
        if cNetPackage.GetType() not in ('ping', 'request'):
            # unknown type. Log error, throw domObj away and continue operation
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Warning: Received unknown Dom type "'+cNetPackage.GetType()+'" for distribution. Skipping...')
            return 0

        # check for circular structures. If id of request is already in
        # request-list -> Throw away!
        if cNetPackage.GetID() in self.dRequests.keys():
            # Log error, throw domObj away and continue operation
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Warning: Detected vicious circle.')
            # To prevent sending more requests to the owl causing the circle, delete originating owl from
            # KnownOwls (if it is there)
            try:
                # i need to get reference to neighbourowl object representing the originating owl.
                # get value list from request dictionary (== get attributes of request)
                reqAttributes = self.dRequests[cNetPackage.GetID()]
                # try to delete first element of list (should be a reference to a neighbourOwl) from KnownOwls.
                # might not exist in list if i dont know that owl
                self.lKnownOwls.remove(reqAttributes[self.SourceOwl])
            except:
                pass

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

        # check package
        if not self.IsValidPackage(cNetPackage):
            return 'error'

        # Get cNeighbourOwl Object that sent me this request
        OrigOwl = self.AddOwl(cNetPackage.GetOriginator())

        # Create list of request attributes
        lReqAttributes = range(4)
        lReqAttributes[self.SourceOwl] = OrigOwl    # owl that i received this request from
        lReqAttributes[self.iMaxAnswers] = 2*cNetPackage.GetTTL()   # number of allowed answers. Dependant on TTL
        lReqAttributes[self.iRecvdAnswers] = 0      # not yet received any answer
        lReqAttributes[self.iTimeCreated] = time.time() # timestamp when request was created
        # Add request to request-dictionary.
        self.dRequests[cNetPackage.GetID()] = lReqAttributes


        # if TTL reached zero -> dont distribute request any further
        if cNetPackage.GetTTL() <= 0:
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Request "'+str(cNetPackage.GetID())+'" reached TTL 0. No more distributing.')
            # return okay cause cNetPackage is accepted regardless of ttl.
            # it just does not get distributed further.
            return 'okay'

        # decrement TTL
        cNetPackage.DecrementTTL()


        #############################
        # Now pass dom to neighbours#
        #############################

        # first replace originator of dom with myself
        cNetPackage.SetOriginator(pManager.manager.GetOwnIP(), self.cNetManager.cNetServer.GetListenPort())

        # now get list of Owls to pass to.
        # XXX - pretty braindead, just take a slice of lKnownOwls with size self.iNumNeighbours. Should
        #       include more intelligence in selecting target owls.
        if len(self.lKnownOwls) > self.iNumNeighbours:
            # i know more owls than i need -> just take a slice with desired size, beginning with first owl.
            lNeighbours = self.lKnownOwls[:self.iNumNeighbours]
        else:
            # i dont know enough owls -> Use whole list for distribution!
            # need a deep copy of list, not just reference...
            lNeighbours = self.lKnownOwls[:]

        # remove originating owl from neighbours - dont want to send to creator of packet!
        self.DeleteOwl(lNeighbours, cNetPackage.GetOriginator())
        # remove myself from neighbours - dont want to send to myself!
        self.DeleteOwl(lNeighbours, (pManager.manager.GetOwnIP(), self.cNetManager.cNetServer.GetListenPort()))

        distri = []
        for i in lNeighbours:
            distri.append(str(i.IP) +':'+ str(i.iPort))

        pManager.manager.DebugStr('cOwlManager '+ __version__ +': Distributing to: '+str(distri)+'.')

        if len(lNeighbours) == 0:
            # empty list!
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Cant Distribute. NeighbourList is empty.')


        # Get cDom-representation of cNetPackage
        domObj = cNetPackage.GetDOM()

        # convert dom to ascii-string for network transport
        # XXX - This may be unneccessary with new release of xmlrpclib!
        sObj = str(domObj.ToXML())

        # Finally start sending
        if cNetPackage.GetType()=='ping':
            # call ping()
            for owl in lNeighbours:
                # pManager.manager.DebugStr('cOwlManager '+ __version__ +': Sending Ping to '+str(owl.IP)+':'+str(owl.iPort)+'.')
                # start new thread for each RPC
                thread.start_new_thread(owl.Ping, (sObj,))
            return 'okay'


        elif cNetPackage.GetType()=='request':
            # call remote owl's Request()
            for owl in lNeighbours:
                # start new thread for each RPC
                thread.start_new_thread(owl.Request, (sObj,))

            # Pass request to own pRecommendation Interface except if it was generated by own owl
            if cNetPackage.GetOriginator()[0] != pManager.manager.GetOwnIP():
                # ok, request was not generated by myself.
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': Passing new request to own pRecommendation.')
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

        if not self.IsValidPackage(cNetPackage):
            return

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
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Received answer for non-existant request. Throwing away..')
            return

        # check type of domObj
        if cNetPackage.GetType() not in ('pong', 'answer'):
            # unknown type. Log error, throw domObj away and continue operation
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Warning: Received unknown Dom type "'+cNetPackage.GetType()+'" as Answer. Skipping...')
            return

        # look if request was created by myself
        if (str(reqAttributes[self.SourceOwl].IP)    == str(pManager.manager.GetOwnIP())) and \
           (str(reqAttributes[self.SourceOwl].iPort) == str(self.cNetManager.cNetServer.GetListenPort())):
            # answer for myself!
            if type == 'pong':
                # Pong info already extracted inside cNetManager.HandlePong().
                # just throw away and continue
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': Received Pong for myself.')
                return
            elif type == 'answer':
                # Pass it to pRecommendationInterface
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': Received Answer for myself. Passing on to pRecommendation.')
                # Get Answer element from cNetPackage
                elAnswer = cNetPackage.GetPayload()
                # Get recommendation interface from pManager.
                pRecIntf = pManager.manager.GetRecommendationInterface()
                pRecIntf.SetAnswer(elAnswer, cNetPackage.GetID())
                return
            else:
                pManager.manager.DebugStr('cOwlManager '+ __version__ +': domType Error! Should never get here!')
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
            # start new thread for RPC
            thread.start_new_thread(origOwl.Pong, (sObj,))
            return
        elif cNetPackage.GetType() == 'answer':
            # Pass answer to originating Owl and continue
            # start new thread for RPC
            thread.start_new_thread(origOwl.Answer, (sObj,))
            return
        else:
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': domType Error! Should never get here!')
            return

        # increment answer counter for request
        tmp = reqAttributes[self.iRecvdAnswers]
        reqAttributes[self.iRecvdAnswers] = tmp+1

        # if answercounter > maxanswers -> delete request from requests dictionary!
        if reqAttributes[self.iRecvdAnswers] > reqAttributes[self.iMaxAnswers]:
            # request reached max answer count.
            # delete it from request dictionary.
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': MaxAnswers reached for request "'+cNetPackage.GetID()+'". Deleting it from dictionary.')
            del self.dRequests[cNetPackage.GetID()]


    def Start(self):
        """Start operation of cOwlManager.

        purpose: register CleanOldRequest-Function with pManager.
                 read list of known owls from file
        """

        pManager.manager.RegisterWatchdog(self.CleanOldRequests, 600)

        try:
            # open file
            owlfile = open(self.sOwlFilename, "r")
        except:
            # cant open file.
            return

        pManager.manager.DebugStr('cOwlManager '+ __version__ +': Reading cached neighbourowls.')
        iOwls=0
        # read line by line
        line = owlfile.readline()
        while line:
            iOwls += 1
            line = line.strip()
            ip, port = line.split(':');
            owl = self.AddOwl((ip, port));
            line = owlfile.readline()

        owlfile.close()
        pManager.manager.DebugStr('cOwlManager '+ __version__ +': Read %s neigbourowls from cache.' % str(iOwls))


    def Shutdown(self):
        """Stop working.

        Save all known neighbourowls to file.
        """

        try:
            owlfile = open(self.sOwlFilename, "w");
        except:
            pManager.manager.DebugStr('cOwlManager '+ __version__ +': Cant open owlfile for writing.')
            return

        pManager.manager.DebugStr('cOwlManager '+ __version__ +': Caching neighbourowls.')
        iOwls=0
        for owl in self.lKnownOwls:
            iOwls += 1
            owlfile.write("%s:%s\n" % (owl.GetIP(), owl.GetPort()))
        owlfile.close()
        pManager.manager.DebugStr('cOwlManager '+ __version__ +': Saved %s neighbourowls in cache.' % str(iOwls))


    def CleanOldRequests(self):
        """Clean requests from expired entrys

        Get called by external timer-thread.

        XXX - Check for possible multithread-problems -> do i need mutex?

        """

        # get current time
        fTime = time.time()

        iNumDeleted = 0
        for id in self.dRequests.keys():
            if (fTime - self.dRequests[id][self.iTimeCreated]) > self.iRequestLifeTime:
                # this request is expired! Delete it
                del self.dRequests[id]
                iNumDeleted = iNumDeleted + 1

        pManager.manager.DebugStr('cOwlManager '+ __version__ +': Cleaned Requeststable from expired entries. Deleted: '+str(iNumDeleted)+', remaining: '+str(len(self.dRequests.keys())))
        return


























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


