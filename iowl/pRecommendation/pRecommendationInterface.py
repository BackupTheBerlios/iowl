
__version__ = "$Revision: 1.11 $"

"""
$Log: pRecommendationInterface.py,v $
Revision 1.11  2002/03/04 21:59:57  aharth
added recommendations count

Revision 1.10  2002/02/18 13:39:42  Saruman
Made waittime for recommendations configurable.
Setting default waittime to 15 seconds instead of 5.

Revision 1.9  2001/08/10 18:38:11  i10614
added debuglevel to all messages.

Revision 1.8  2001/04/15 21:16:22  i10614
fixed for recommendations and answers

Revision 1.7  2001/04/15 20:14:07  i10614
minor changes

Revision 1.6  2001/04/15 19:14:01  i10614
minor changes

Revision 1.5  2001/04/07 17:06:24  i10614
many, many bugfixes for working network communication

Revision 1.4  2001/03/27 18:27:04  i10614
added shutdown notification

Revision 1.3  2001/03/24 23:40:35  i10614
various bugfixes

Revision 1.1.1.1  2001/03/24 19:22:50  i10614
Initial import to stio1 from my cvs-tree

Revision 1.14  2001/02/22 23:20:43  a
fixed minor bug

Revision 1.13  2001/02/22 22:02:28  a
minor changes

Revision 1.12  2001/02/22 21:53:19  a
bug fixes for supporting history list

Revision 1.11  2001/02/22 15:18:32  a
giving recommendations to own owl from own clickstream

Revision 1.10  2001/02/22 15:13:52  a
owls gives recommendation to itself

Revision 1.9  2001/02/22 12:17:07  a
basic network functionality

Revision 1.8  2001/02/21 18:30:05  a
basic functions work

Revision 1.7  2001/02/21 16:03:50  a
minor changes

Revision 1.6  2001/02/21 13:57:16  mbauer
added import statement for urlparse

Revision 1.5  2001/02/21 13:21:24  a
cosmetic changes

Revision 1.4  2001/02/21 13:00:13  a
added methods for Gui

Revision 1.3  2001/02/19 19:20:05  a
added *Handler classes

Revision 1.2  2001/02/19 18:20:29  a
initial version

Revision 1.1  2001/02/18 22:32:48  a
initial version


"""
import urlparse
import pManager
import cRecommendationBuilder
import cRequestBuilder
import cRequest
import cAnswer
import sys

class pRecommendationInterface:

    """Recommendation class.
    
    This class is responsible for creating and answering request as well
    as compute recommendations from answers of other owls. A request
    can consist of 1..n URLs. If the user wants recommendations, request
    to other owls must be issued first. That is done in this class.

    """

    def __init__(self):
        """Constructor."""
        self.iTopList = 23
        self.RecBuilder = cRecommendationBuilder.cRecommendationBuilder()
        self.ReqBuilder = cRequestBuilder.cRequestBuilder()
        # returned rules from network, key is id
        self.dRules = {}
        # time in seconds to wait for incoming recommendations
        self.iWaitTime = 10
        # number of answered recommendations
        self.iNumAnsweredRecommendations = 0
        # number of received recommendations
        self.iNumReceivedRecommendations = 0


    def Start(self):
        """Kind of constructor."""
        pass


    def SetParam(self, sParameter, sValue):
        """Get config from pManagement.

        sParameter -- key
        sValue -- value

        """
        if (sParameter == 'toplist'):
            self.iTopList = sValue
        elif (sParameter == 'waittime'):
            self.iWaitTime = int(sValue)


    def GetWaitTime(self):
        """return time to wait for incoming recommendations"""
        return self.iWaitTime


    def Shutdown(self):
        """Kind of destructor."""
        pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Shutting down.', 1)


    def GenerateSingleRequest(self, sUrl):
        """Generate a request and send it to network.

        sUrl -- Url to get recommendations for

        """
        tUrl = urlparse.urlparse(sUrl)
        el = self.ReqBuilder.DoRequest([tUrl,])

        # Get NetworkInterface
        pNetIntf = pManager.manager.GetNetworkInterface()

        # Send request to iOwl-net
        pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Now sending single request to network.', 4)
        sId = pNetIntf.SendRequest(el)
        pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Finished sending single request to network. Id: '+str(sId), 4)

        # Generate empty list for answers
        self.dRules[sId] = []

        # return id to gui
        return sId


    def GenerateSessionRequest(self):
        """Generate a request and send it to network.

        return -- id


        XXX - What to do when history is empty?

        """

        # collect clicks for current session
        csi = pManager.manager.GetClickstreamInterface()
        lUrls = []
        lClicks = csi.GetHistory()
        for click in lClicks:
            lUrls.append(click.GetUrl())

        # generate request from list of clicks
        el = self.ReqBuilder.DoRequest(lUrls)

        # Get NetworkInterface
        pNetIntf = pManager.manager.GetNetworkInterface()

        # Send request to iOwl-net
        pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Now sending session request to network.', 4)
        sId = pNetIntf.SendRequest(el)
        pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Finished sending session request to network. Id: '+str(sId), 4)

        # Generate empty list for answers
        self.dRules[sId] = []

        # return id to gui
        return sId


    def GetRecommendations(self, sId):
        """Return a list with recommendations.

        This method is called from gui to collect all answers that came in for request with id sId.

        id -- id of request
        return -- list of clicks

        """

        # prepare list to answer
        lClicks = None

        # Look if request exists in my list
        if self.dRules.has_key(sId):
            # Look if i received answers from other owls
            if len(self.dRules[sId]) > 0:
                lClicks = self.RecBuilder.BuildRecommendation(self.dRules[sId])
                self.iNumReceivedRecommendations = self.iNumReceivedRecommendations + 1
            else:
                # request is there but got no answers
                pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Dont have any answers for request id: '+str(sId), 4)

            # delete id from list to disable new answers coming in.
            del self.dRules[sId]

        else:
            pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Serious Error! Id '+str(sId)+' does not exist!', 3)

        # return recommendation
        return lClicks


    def SetRequest(self, reqEl, sId):
        """Incoming request from network layer.

        After receiving a request an answer must be issued to network with
        method SendRequest from pNetworkInterface.

        reqEl - element with request from other owl
        id -- unique id generated by network

        """

        pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Got single request from network. Id: '+str(sId), 4)
        request = cRequest.cRequest()
        request.SetElement(reqEl)

        psi = pManager.manager.GetStatisticsInterface()
        lMatchingRules = psi.GetMatches(request.GetUrls())

        if lMatchingRules:
            answer = cAnswer.cAnswer()
            answer.SetRules(lMatchingRules)
            answerEl = answer.GetElement()
            # Get NetworkInterface
            pNetIntf = pManager.manager.GetNetworkInterface()
            # send answer
            pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Now sending answer to network. Id: '+str(sId), 4)
            pNetIntf.SendAnswer(answerEl, sId)
            pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Finished sending answer to network. Id: '+str(sId), 4)
            self.iNumAnsweredRecommendations = self.iNumAnsweredRecommendations + 1
        else:
            pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Dont have answers for request. Id: '+str(sId), 4)


    def GetNumAnsweredRecommendations(self):
        """ Return number of recommendations. """
        return self.iNumAnsweredRecommendations


    def GetNumReceivedRecommendations(self):
        """ Return number of recommendations. """
        return self.iNumReceivedRecommendations


    def SetAnswer(self, answerEl, sId):
        """Incoming answer for a sent request from network layer.

        answer -- elements with answer from other owls
        id -- unique id of my request

        """

        pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Got answer from network for my request. Id: '+str(sId), 3)
        answer = cAnswer.cAnswer()
        answer.SetElement(answerEl)

        # extract rules from answer
        lAnswerRules = answer.GetRules()

        # look if request is still active
        if self.dRules.has_key(sId):
            # okay, append to answerlist
            self.dRules[sId].append(lAnswerRules)
        else:
            pManager.manager.DebugStr('pRecommendationInterface '+ __version__ +': Throwing away answer. Request is already gone! Id: '+str(sId), 3)



#    def GenerateLongtermRequest(self):
#        """Generate a request and send it to network.
#
#        return -- id
#
#        """
#        id = 0
#        # print "id = send request to network"
#        return id


####################################################################
## TEST FUNCTIONS ##################################################

def test():
    """Built-in test method for this class."""

    print "none"


if __name__ == '__main__':
    test()
