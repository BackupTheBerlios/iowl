
__version__ = "$Revision: 1.2 $"

"""
$Log: cRequestBuilder.py,v $
Revision 1.2  2001/04/07 17:06:24  i10614
many, many bugfixes for working network communication

Revision 1.1.1.1  2001/03/24 19:22:51  i10614
Initial import to stio1 from my cvs-tree

Revision 1.2  2001/02/22 21:53:18  a
bug fixes for supporting history list

Revision 1.1  2001/02/22 12:41:03  a
added RequestBuilder


"""

import cRequest
import pManager


class cRequestBuilder:

    """Request builder class.
    
    In this class requests are built.

    """

    def DoRequest(self, lUrls):
        """Generate a request and send it to network.

        lUrls -- Urls to get recommendations for
        return -- el, element for request in network
        
        """

        ni = pManager.manager.GetNetworkInterface()

        request = self.BuildRequest(lUrls)

        el = request.ReturnRootElement()

        return el


    def BuildRequest(self, lUrls):
        """Build requests from list of urls.

        lUrls -- list of urls to build request with
        return -- request, a cRequest object

        """
        request = cRequest.cRequest()

        request.SetUrls(lUrls)

        # request.Print()

        return request




