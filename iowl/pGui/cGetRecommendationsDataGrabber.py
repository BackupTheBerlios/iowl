__version__ = "$Revision: 1.4 $"

"""
$Log: cGetRecommendationsDataGrabber.py,v $
Revision 1.4  2002/02/10 21:40:54  aharth
added showrules feature, cleaned up ui

Revision 1.3  2001/05/26 14:44:03  i10614
only display a maximum of 15 recommendations

Revision 1.2  2001/04/23 13:03:26  i10614
added target _new

Revision 1.1.1.1  2001/03/24 19:22:58  i10614
Initial import to stio1 from my cvs-tree

Revision 1.6  2001/02/22 23:13:05  mbauer
cosmetic changes

Revision 1.5  2001/02/22 21:19:17  mbauer
bugfix

Revision 1.3  2001/02/22 15:15:02  a
if no recommendation is possible return message in html

Revision 1.2  2001/02/22 14:47:43  mbauer
new Gui-look implemented

Revision 1.1  2001/02/21 14:50:13  mbauer
initial release



"""
import pManager
import urlparse

class cGetRecommendationsDataGrabber:
    """Get results for a previously started recommendation request"""

    def __init__(self, cGuiRequestHandler):
        """Constructor"""
        self.cGuiRequestHandler = cGuiRequestHandler


    def GetHtml(self, dParams):
        """Return complete HTML-page

        dParams - dict containing
                    'id':'47611'
                    'sUrl':'url these recommendations are for'

        return  -- string (<html>.....</html)

        """

        # get pRecommendationInterface
        cRecommendationInterface = pManager.manager.GetRecommendationInterface()

        # get list of clicks
        lClicks = cRecommendationInterface.GetRecommendations(dParams['id'])

        # get header
        sHeader = self.cGuiRequestHandler.GetHeader('Recommendations for %s' % str(dParams['sUrl']))

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



















