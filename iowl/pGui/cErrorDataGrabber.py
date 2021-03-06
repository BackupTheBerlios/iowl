__version__ = "$Revision: 1.2 $"

"""
$Log: cErrorDataGrabber.py,v $
Revision 1.2  2002/02/10 21:40:54  aharth
added showrules feature, cleaned up ui

Revision 1.1.1.1  2001/03/24 19:22:54  i10614
Initial import to stio1 from my cvs-tree

Revision 1.6  2001/03/03 16:01:29  mpopp
minor changes

Revision 1.5  2001/02/25 17:32:34  mpopp
small bug fix

Revision 1.3  2001/02/25 12:32:41  mpopp
*** empty log message ***

Revision 1.2  2001/02/22 14:47:43  mbauer
new Gui-look implemented

Revision 1.1  2001/02/20 17:34:58  mbauer
initital release



"""
import pManager

class cErrorDataGrabber:
    """Responsible for error messages"""

    def __init__(self, cGuiRequestHandler):
        """Constructor"""
        self.cGuiRequestHandler = cGuiRequestHandler

    def GetHtml(self, dParams):
        """Return complete HTML-page

        begin with tag <html>
        end with tag </html>

        http headers etc are generated by proxy.

        """

        # Get Header
        sHeader = self.cGuiRequestHandler.GetHeader('iOwl.net - error')

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

        # Generate Content
        sContent =  """<h2>Error</font></h2>
                       <p class="message">
                          Could not execute command.
                       </p>
                       <p class="message">
                          Reason: %s
                       </p>
                    """ % dParams['message']

        # Get second part of page
        sPart2 = self.cGuiRequestHandler.GetEndPage()

        # glue together
        sPage = sPart1 + sHeader + sContent + sPart2

        # return page and content-type
        return sPage, 'text/html'
