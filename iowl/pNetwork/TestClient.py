import xmlrpclib
import time
import cDOM

def GeneratePing():
    """Generate a PING cDOM

    a Ping looks like:

    <iowl.net version="0.1" id="4711" type="Ping" ttl="12">
        <originator ip="192.168.99.2" port="2323"></originator>
    </iowl.net>

    return -- cDOM containing a PING packet

    """

    # create unique id
    # id = pManager.manager.GetUniqueNumber()
    id = 222222

    # get own IP from manager
    # ownip = pManager.manager.GetOwnIP()
    ownip = '1.2.3.4'

    # get ListenPort from cNetServer
    # iListenPort = self.cNetServer.GetListenPort()
    iListenPort = 2323

    # create the dom
    domPing = cDOM.cDOM()

    # create core element: originator, containing ip and port as attributes
    elOriginator = domPing.CreateElement('originator', {'ip':str(ownip), 'port':str(iListenPort)}, 'dummy')

    # create list containing core element
    els = []
    els.append(elOriginator)

    # get iOwl-version
    # sVersion = str(pManager.manager.GetVersion())
    # sVersion = 'Testversion'
    sVersion = "0.2"

    # create container: iowl.net
    elCont = domPing.CreateElementContainer('iowl.net', {'version':sVersion, 'id':str(id), 'type':'Ping', 'ttl':str(4)}, els)

    # save elements in dom
    domPing.SetRootElement(elCont)

    # finished!
    return domPing


testsvr = xmlrpclib.Server("http://localhost:2323")

ping = GeneratePing()

asciiPing = ping.ToXML()

testsvr.Ping(asciiPing)


