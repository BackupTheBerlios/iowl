__version__ = "$Revision: 1.7 $"

"""
$Log: cSingleRecommendationDataGrabber.py,v $
Revision 1.7  2002/03/01 14:39:14  aharth
minor bugfix for activate/deactivate

Revision 1.6  2002/02/18 13:39:42  Saruman
Made waittime for recommendations configurable.
Setting default waittime to 15 seconds instead of 5.

Revision 1.5  2002/02/11 16:22:46  aharth
changed jscript stuff for singlerecommendation

Revision 1.4  2001/05/26 14:44:03  i10614
only display a maximum of 15 recommendations

Revision 1.3  2001/04/07 17:06:23  i10614
many, many bugfixes for working network communication

Revision 1.2  2001/03/28 19:53:07  i10614
replaced http://iowl with http://my.iowl.net

Revision 1.1.1.1  2001/03/24 19:22:58  i10614
Initial import to stio1 from my cvs-tree

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
import time

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

        # get pRecommendationInterface
        cRecommendationInterface = pManager.manager.GetRecommendationInterface()

        # start request for Recommendations
        iReqID = cRecommendationInterface.GenerateSingleRequest(str(dParams['sUrl']))

        # wait for recommendations to come in
        time.sleep(cRecommendationInterface.GetWaitTime())

        # get list of clicks
        lClicks = cRecommendationInterface.GetRecommendations(iReqID)

        # get header
        sHeader = self.cGuiRequestHandler.GetHeader('Recommendation')

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

        # get dynamic content
        sContent = '<h2>Recommendations</h2>'
        if lClicks == None:
            sContent = sContent + '<p class="message">Sorry, i did not find any ressources i could recommend. :-(</p>'
        else:
            sContent = sContent + '<p class="message">Success :-). I would recommend you have a look at the following ressource(s):</p>'
            iCounter = 0
            for click in lClicks:
                iCounter+=1
                sContent = sContent +'<p><a href="%s" target="_new">%s</a></p>' % (str(urlparse.urlunparse(click.GetUrl())), str(click.GetTitle()))
                if (iCounter > 15):
                    break

        # Get second part of page
        sPart2 = self.cGuiRequestHandler.GetEndPage()

        # glue together
        sPage = sHeader + sPart1 + sContent + sPart2

        # return page and content-type
        return sPage, 'text/html'
