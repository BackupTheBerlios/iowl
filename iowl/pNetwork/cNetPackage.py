
__version__ = "$Revision: 1.5 $"

"""
$Log: cNetPackage.py,v $
Revision 1.5  2002/02/22 12:04:46  Saruman
initiate answerer IP of pong to localhost.

Revision 1.4  2002/02/11 15:12:38  Saruman
Major network changes.
Network protocol now 0.3, incompatible to older versions!
Should fix all problems regarding the detection of own ip and enable use of iOwl behind a firewall.

Revision 1.3  2001/04/15 21:16:21  i10614
fixed for recommendations and answers

Revision 1.2  2001/04/15 19:10:59  i10614
Ping<->Pong works again.

Revision 1.1  2001/04/14 14:55:27  i10614
initial release


"""

import cDOM

class cNetPackage:
    """This is the base class for all data structures
    going through the network

    A cNetPackage (Ping) looks like this:

    <iowl.net id="45856275162370631278" protocol="0.2" ttl="4" type="ping" version="0.4">
        <originator ip="192.168.99.2" port="2323"></originator>
    </iowl.net>

    """

    def __init__(self, sType = 'undefined'):
        """constructor"""

        # ip of creator
        self.sOrigIP = '127.0.0.1'
        # port of creator
        self.iOrigPort = 0
        # iOwl-version
        self.sVersion = ''
        # network-version
        self.sProtocol = ''
        # type
        self.sType = sType
        # id
        self.sID = 0
        # ttl
        self.iTTL = 0


    def SetOriginatorIP(self, sIP):
        """Set originator IP"""
        self.sOrigIP = sIP


    def SetOriginatorPort(self, iPort):
        """Set originator port"""
        self.iOrigPort = iPort


    def GetOriginator(self):
        """return originator"""
        return self.sOrigIP, self.iOrigPort


    def SetOwlVersion(self, sVersion):
        """Set iOwl-Version"""
        self.sVersion = sVersion


    def GetOwlVersion(self):
        """return string containing version of iOwl"""
        return self.sVersion


    def SetProtocolVersion(self, sVersion):
        """Set version of network protocol"""
        self.sProtocol=sVersion


    def GetProtocolVersion(self):
        """return string containing version of network-protocol"""
        return self.sProtocol


    def SetID(self, sID):
        """Set id of package"""
        self.sID = sID


    def GetID(self):
        """Return string containing ID of package"""
        return self.sID


    def SetType(self, sType):
        """Set type of package
        must be on of:
        - "request"
        - "answer"
        - "ping"
        - "pong"

        """
        self.sType = sType


    def GetType(self):
        """Return string containing type of package"""
        return self.sType


    def SetTTL(self, iTTL):
        """Set TTL-Counter"""
        self.iTTL = iTTL


    def GetTTL(self):
        """return int containing TTL"""
        return self.iTTL


    def DecrementTTL(self):
        """Decrement TTL by one

        returns new TTL value.
        Raise exception if TTL is < 1
        """
        if self.iTTL < 1:
            raise

        self.iTTL-=1
        return self.iTTL


    def GetDOM(self):
        """Generate cDOM from internal representation"""

        # create the dom
        dom = cDOM.cDOM()
        # create core element: originator, containing ip and port as attributes
        elOriginator = dom.CreateElement('originator',
                                         {'ip':str(self.sOrigIP),
                                          'port':str(self.iOrigPort)
                                         },
                                         ''
                                        )
        # create list containing core element
        els = []
        els.append(elOriginator)
        # create container: iowl.net
        elCont = dom.CreateElementContainer('iowl.net',
                                            {'version':self.sVersion,
                                             'protocol':self.sProtocol,
                                             'id':self.sID,
                                             'type':self.sType,
                                             'ttl':str(self.iTTL)
                                            },
                                            els
                                           )
        # save elements in dom
        dom.SetRootElement(elCont)
        return dom



    def ParseDOM(self, cDom):
        """Parse a DOM to internal representation

        A cNetPackage (Ping) looks like this:

        <iowl.net id="45856275162370631278" protocol="0.2" ttl="4" type="ping" version="0.4">
            <originator ip="192.168.99.2" port="2323"></originator>
        </iowl.net>

        """

        # get root element
        elRoot = cDom.GetRootElement()
        # extract general info
        dAttrs, lContents = cDom.GetElementContainerContent(elRoot, 'iowl.net', ['id',
                                                                               'protocol',
                                                                               'version',
                                                                               'ttl',
                                                                               'type'])
        # store info
        self.SetID(dAttrs['id'])
        self.SetProtocolVersion(dAttrs['protocol'])
        self.SetOwlVersion(dAttrs['version'])
        self.SetTTL(int(dAttrs['ttl']))
        self.SetType(dAttrs['type'])

        # get originator element
        lElements = cDom.MatchingElementsByName('originator')
        elOriginator=lElements[0]
        # list with text and attributes
        sName, dAttrs, sContent = cDom.GetElementContent(elOriginator, ['ip','port'])
        # store originator info
        self.SetOriginatorIP(dAttrs['ip'])
        self.SetOriginatorPort(int(dAttrs['port']))


    def Print(self):
        """print all my data"""
        print self.sType
        print self.sID
        print self.sVersion
        print self.sProtocol
        print str(self.iTTL)
        print self.sOrigIP+':'+str(self.iOrigPort)






class cPong(cNetPackage):
    """This is a Pong

    Only extension to cNetPackage is the storing of
    the answerer's adress.

    """

    def __init__(self, sType='pong'):
        """Constructor"""

        # call base-class constructor
        cNetPackage.__init__(self, sType)

        # Answerer IP
        self.sAnswIP = '127.0.0.1'

        # Answerer Port
        self.iAnswPort = 0


    def SetAnswererIP(self, sIP):
        """Set Answerer IP"""
        self.sAnswIP = sIP


    def SetAnswererPort(self, iPort):
        """Set Answerer port"""
        self.iAnswPort = iPort


    def GetAnswerer(self):
        """return originator"""
        return self.sAnswIP, self.iAnswPort


    def GetDOM(self):
        """Generate cDOM from internal representation

        return - cDOM

        """

        # create the dom
        dom = cDOM.cDOM()
        # create core element: originator, containing ip and port as attributes
        elOriginator = dom.CreateElement('originator',
                                         {'ip':self.sOrigIP,
                                          'port':str(self.iOrigPort)
                                         },''
                                        )
        # create core element: answerer, containing ip and port as attributes
        elAnswerer = dom.CreateElement('answerer',
                                       {'ip':self.sOrigIP,
                                        'port':str(self.iOrigPort)
                                       },''
                                      )

        # create list containing core element
        els = []
        els.append(elOriginator)
        els.append(elAnswerer)

        # create container: iowl.net
        elCont = dom.CreateElementContainer('iowl.net',
                                            {'version':self.sVersion,
                                             'protocol':self.sProtocol,
                                             'id':self.sID,
                                             'type':self.sType,
                                             'ttl':str(self.iTTL)
                                            },
                                            els
                                           )
        # save elements in dom
        dom.SetRootElement(elCont)
        return dom


    def ParseDOM(self, cDom):
        """Parse a DOM to internal representation

        A cNetPackage (Pong) looks like this:

        <iowl.net id="45856275162370631278" protocol="0.2" ttl="4" type="pong" version="0.4">
            <originator ip="192.168.99.2" port="2323"></originator>
            <answerer ip="192.168.99.3" port="2323"></answerer>
        </iowl.net>

        """

        # call superclasses parseDom
        cNetPackage.ParseDOM(self, cDom)

        # Look for my additional stuff

        # get answerer element
        lElements = cDom.MatchingElementsByName('answerer')
        elAnswerer=lElements[0]
        # list with text and attributes
        sName, dAttrs, sContent = cDom.GetElementContent(elAnswerer, ['ip','port'])
        # store originator info
        self.SetAnswererIP(dAttrs['ip'])
        self.SetAnswererPort(int(dAttrs['port']))


    def Print(self):
        """print all my data"""
        cNetPackage.Print(self)
        print self.sAnswererIP+':'+str(self.iAnswererPort)



class cRecPackage(cNetPackage):
    """a request or answer for recommendations

    Only extension to cNetPackage is the storing of payload

    """

    def __init__(self, sType='undefined'):
        """Constructor"""

        # call base-class constructor
        cNetPackage.__init__(self, sType)

        # my payload
        self.payload = None


    def StorePayload(self, payload):
        """Store payload dom-element"""
        self.payload = payload


    def GetPayload(self):
        """get Payload dom-element"""
        return self.payload


    def GetDOM(self):
        """Generate cDOM from internal representation

        return - cDOM

        """

        # create the dom
        dom = cDOM.cDOM()
        # create core element: originator, containing ip and port as attributes
        elOriginator = dom.CreateElement('originator',
                                         {'ip':str(self.sOrigIP),
                                          'port':str(self.iOrigPort)
                                         },
                                         ''
                                        )
        # create list containing core element and payload
        els = []
        els.append(elOriginator)
        # create container for payload
        elPayload = dom.CreateElementContainer('payload', {}, (self.payload, ))
        els.append(elPayload)
        # create container: iowl.net
        elCont = dom.CreateElementContainer('iowl.net',
                                            {'version':self.sVersion,
                                             'protocol':self.sProtocol,
                                             'id':self.sID,
                                             'type':self.sType,
                                             'ttl':str(self.iTTL)
                                            },
                                            els
                                           )
        # save elements in dom
        dom.SetRootElement(elCont)
        return dom


    def ParseDOM(self, cDom):
        """Parse a DOM to internal representation

        A cNetPackage (request/Answer) looks like this:

        <iowl.net id="45856275162370631278" protocol="0.2" ttl="4" type="request" version="0.4">
            <originator ip="192.168.99.2" port="2323"></originator>
            <payload>
                something....
            </payload>
        </iowl.net>

        """

        # call superclass's parseDom
        cNetPackage.ParseDOM(self, cDom)

        # Look for my additional stuff

        # get payload element
        lElements = cDom.MatchingElementsByName('payload')

        # store Payload
        self.payload = lElements[0].childNodes[0]


    def Print(self):
        """print all my data"""

        cNetPackage.Print(self)
        print self.payload


