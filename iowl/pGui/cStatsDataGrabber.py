__version__ = "$Revision: 1.3 $"

"""
$Log: cStatsDataGrabber.py,v $
Revision 1.3  2002/02/21 12:46:18  Saruman
Added routingtable to statistics page

Revision 1.2  2002/02/13 10:50:48  Saruman
changed output



"""

import pManager

class cStatsDataGrabber:
    """Responsible for displaying statistics page"""

    def __init__(self, cGuiRequestHandler):
        """Constructor"""
        self.cGui = cGuiRequestHandler

    def GetHtml(self, dParams):
        """Return complete HTML-page

        return string
        - beginning with tag <html>
        - ending with tag </html>

        http headers etc are generated by proxy!

        """

        # Get Header
        sHeader = self.cGui.GetHeader('iOwl.net - Statistics')

        # Get recording Status of proxy
        bState = pManager.manager.GetProxyInterface().GetStatus()

        # Get first part of page
        sPart1 = ''
        if bState == 0:
            # Owl not logging
            # Get inactive page
            sPart1 = self.cGui.GetInactivePage()
        else:
            # owl is logging
            # get active page
            sPart1 = self.cGui.GetActivePage()

        # get NetworkInterface
        pni = pManager.manager.GetNetworkInterface()

        # get number of known owls
        iNumKnownOwls = pni.GetNumKnownOwls()

        # get number of active routing entrys
        iNumActiveRoutings = pni.GetNumActiveRoutings()

        # get number of pongs received
        iNumPongs = pni.GetNumPongsReceived()

        # get number of Answers received
        iNumAnswers = pni.GetNumAnswersReceived()

        # get dictionary with current routing table
        dRoutingTable = pni.GetRoutingTable()
        # some magic numbers for request dictionary values for easy list index access
        iSourceOwl = 0
        iMaxAnswers = 1
        iRecvdAnswers = 2
        iTimeCreated = 3

        sContent = '<h2>Network Statistics</h2>\n'
        sContent = sContent + "<p>\n"
        sContent = sContent + "Known active owls: "+str(iNumKnownOwls)+"\n</p>"
        sContent = sContent + "<p>\n"
        sContent = sContent + "Currently active routing entries: "+str(iNumActiveRoutings)+"\n</p>"
        sContent = sContent + "<p>\n"
        sContent = sContent + "Total number of pongs received for myself: "+str(iNumPongs)+"\n</p>"
        sContent = sContent + "<p>\n"
        sContent = sContent + "Total number of recommendations received for myself: "+str(iNumAnswers)+"\n</p>"
        sContent = sContent + "<h3>Routing Table</h3>\n"

        # Head row
        sTable = "<table border=\"1\">\n"
        sTable = sTable + """<tr>
  <th>ID</th>
  <th>Sourceowl</th>
  <th>MaxAnswers</th>
  <th>ReceivedAnswers</th>
  <th>Time Created</th>
</tr>
"""
        # subsequent rows

        for id in dRoutingTable.keys():
            sTable = sTable + "<tr>\n"
            sTable = sTable + """
  <td>%s</td>\n  <td>%s</td>\n  <td>%s</td>\n  <td>%s</td>\n  <td>%s</td>
            """ %(str(id), (str(dRoutingTable[id][iSourceOwl].GetIP()) + ":" + str(dRoutingTable[id][iSourceOwl].GetPort())), str(dRoutingTable[id][iMaxAnswers]), str(dRoutingTable[id][iRecvdAnswers]), str(dRoutingTable[id][iTimeCreated]))

            sTable = sTable + "</tr>\n"

        sTable = sTable + "</table>\n\n"

        sContent = sContent + sTable

        sContent = sContent + '<h2>Recommendation Statistics</h2>\n'
        sContent = sContent + "<p>\n"
        sContent = sContent + "Still todo\n</p>"

        # get end part
        sPart2 = self.cGui.GetEndPage()

        # Glue it
        sPage = sHeader + sPart1 + sContent + sPart2

        # return page and content-type
        return sPage, 'text/html'











