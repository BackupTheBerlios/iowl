__version__ = "$Revision: 1.1 $"

"""
$Log: cSingleRecommendationDataGrabber.py,v $
Revision 1.1  2001/03/24 19:22:58  i10614
Initial revision

Revision 1.5  2001/02/25 12:32:42  mpopp
*** empty log message ***

Revision 1.4  2001/02/22 20:41:50  mbauer
revamped gui :-)

Revision 1.2  2001/02/21 18:34:20  a
changed seconds from 20 to 4

Revision 1.1  2001/02/21 14:50:12  mbauer
initial release



"""

import cClick
import cDOM
import urlparse
import pManager
import pRecommendationInterface
import cJavaScriptTimer

class cSingleRecommendationDataGrabber:
    """Get recommendations for a single url"""

    def __init__(self, cGuiRequestHandler):
        """Constructor"""
        self.cGuiRequestHandler = cGuiRequestHandler


    def GetHtml(self, dParams):
        """Return complete HTML-page

        To allow the package pRecommendation to gather answers,
        start Query and return a page containing a java-script countdown.
        After countdown is finished, start a new request that
        forces pRecommendation to display its results.

        http headers etc are generated by proxy.

        dParams - dict containing one key 'sUrl':'http://www.irgendwo.de'

        return  -- string (<html>.....</html)

        """


        # time to wait till reload
        iSeconds = 4

        # get pRecommendationInterface
        cRecommendationInterface = pManager.manager.GetRecommendationInterface()

        # start request for Recommendations
        iReqID = cRecommendationInterface.GenerateSingleRequest(str(dParams['sUrl']))

        # build url to load after timer finished
        sNewUrl = 'http://iowl/command?action=getrecommendations&id=%s&sUrl=%s' % (str(iReqID), str(dParams['sUrl']))

        # get javascript timer
        sScript, sFunction, sForm = cJavaScriptTimer.cJavaScriptTimer().GetTimer(iSeconds, sNewUrl)

        # get Header including timerscript
        sHeader = self.cGuiRequestHandler.GetHeader('iOwl.net - Gathering Recommendations', sScript, sFunction)

        # Get recording Status of proxy
        bState = pManager.manager.GetProxyInterface().GetStatus()

        # Get first part of page
        sPart1 = ''
        if bState == 0:
            # Owl not logging
            # Get inactive page
            sPart1 = self.cGuiRequestHandler.GetInactivePage()
        else:
            # owl is logging
            # get active page
            sPart1 = self.cGuiRequestHandler.GetActivePage()

        # get content
        sContent = """
                   <h1><font face="Arial, Helvetica, sans-serif" size="5" color="#666666">Gathering recommendations</font></h1>
                   <p>
                   Please wait while iOwl.net gathers information for your request.
                   Time left: %s
                   seconds.
                   """ %sForm

        # Get second part of page
        sPart2 = self.cGuiRequestHandler.GetEndPage()

        # glue together
        sPage = sPart1 + sHeader + sContent + sPart2

        # return page and content-type
        return sPage, 'text/html'
