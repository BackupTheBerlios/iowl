
__version__ = "$Revision: 1.1 $"

"""
$Log: cRequestHandler.py,v $
Revision 1.1  2001/03/24 19:22:51  i10614
Initial revision

Revision 1.1  2001/02/19 19:20:04  a
added *Handler classes


"""

import cRequest
import cAnswer


class pRequestHandler:

    """Handles requests.
    
    This class is responsible for handling requests.
    
    """"
    
    def __init__(self):
        """Constructor."""
        self.Request = cRequest.cRequest()


    def SetRequest(self, request):
        """Parse request into internal representation.

        lEls -- list of request elements

        """
        self.Request.SetElements(lEls)


    def PreperateAnswer(self):
        """Preperate answer for request."""
        answer = cAnswer.cAnswer()
        # lItemsets = self.Request.GetItemsets()
        # lRules = pStatisticsInterface.GetMatches(lItemsets)
        # if lRules != None:
        # answer.SetRules(lRules)
        # pNetworkInterface.SendAnswer(answer)
