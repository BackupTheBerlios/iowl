__version__ = "$Revision: 1.10 $"

"""
$Log: cGuiRequestHandler.py,v $
Revision 1.10  2001/08/10 18:32:15  i10614
added debuglevel to all messages.

Revision 1.9  2001/07/15 14:37:55  i10614
updated configuration GUI

Revision 1.8  2001/07/15 10:15:26  i10614
added commands "showconfig" and "showlog"

Revision 1.7  2001/05/26 16:27:43  i10614
changed default path

Revision 1.6  2001/05/26 14:00:06  i10614
changed default params

Revision 1.5  2001/05/25 12:43:43  i10614
adapted bckcolor

Revision 1.4  2001/04/22 13:24:03  i10614
changed html meta-tags to disable caching of iOwl-pages

Revision 1.3  2001/03/28 19:53:07  i10614
replaced http://iowl with http://my.iowl.net

Revision 1.2  2001/03/26 12:08:23  i10614
added version and build date

Revision 1.1.1.1  2001/03/24 19:22:56  i10614
Initial import to stio1 from my cvs-tree

Revision 1.10  2001/03/18 23:12:42  mbauer
removed obsolete usage of cHistoryDataGrabber

Revision 1.9  2001/03/18 22:22:55  mbauer
removed debug output

Revision 1.8  2001/02/22 20:41:49  mbauer
revamped gui :-)

Revision 1.6  2001/02/21 18:46:03  mbauer
added about page configuration

Revision 1.5  2001/02/21 14:51:08  mbauer
added more user-functions

Revision 1.3  2001/02/20 21:22:34  mbauer
bugfix concerning helpfile-location



"""

import pManager
import cgi
import urlparse
import cDefaultDataGrabber
import cErrorDataGrabber
import cHelpDataGrabber
import cAboutDataGrabber
import cSessionRecommendationDataGrabber
import cLongtermRecommendationDataGrabber
import cSingleRecommendationDataGrabber
import cGetRecommendationsDataGrabber
import cBinaryDataGrabber
import cCommandValidator
import cLogfileGrabber
import cConfigureGrabber


class cGuiRequestHandler:
    """The main class of pGui.

    Accepts commands and collects necessary answers, formats them to html
    and returns documents

    """

    def __init__(self):
        """Constructor"""

        # create grabber classes for request types
        self.cDefaultDataGrabber = cDefaultDataGrabber.cDefaultDataGrabber(self)
        self.cErrorDataGrabber = cErrorDataGrabber.cErrorDataGrabber(self)
        self.cHelpDataGrabber = cHelpDataGrabber.cHelpDataGrabber(self)
        self.cAboutDataGrabber = cAboutDataGrabber.cAboutDataGrabber(self)
        self.cSessionRecommendationDataGrabber = cSessionRecommendationDataGrabber.cSessionRecommendationDataGrabber(self)
        self.cLongtermRecommendationDataGrabber = cLongtermRecommendationDataGrabber.cLongtermRecommendationDataGrabber(self)
        self.cSingleRecommendationDataGrabber = cSingleRecommendationDataGrabber.cSingleRecommendationDataGrabber(self)
        self.cGetRecommendationsDataGrabber = cGetRecommendationsDataGrabber.cGetRecommendationsDataGrabber(self)
        self.cBinaryDataGrabber = cBinaryDataGrabber.cBinaryDataGrabber(self)
        self.cLogfileGrabber = cLogfileGrabber.cLogfileGrabber(self)
        self.cConfigureGrabber = cConfigureGrabber.cConfigureGrabber(self)

        # create cCommandValidator
        self.cCommandValidator = cCommandValidator.cCommandValidator()

        # set default filenames
        self.cHelpDataGrabber.SetHelpFileName('data/gui/help.ht')
        self.cAboutDataGrabber.SetAboutFileName('data/gui/about.ht')
        self.sActiveFilename = 'data/gui/interfaceact.ht'
        self.sInactiveFilename = 'data/gui/interfaceinact.ht'
        self.sEndFilename = 'data/gui/interfacefooter.ht'


    def SetParam(self, sOption, sValue):
        """Accept settings

        Set parameter

        available options:
        mainpage     - location of main.html
        helppage     - location of help.html

        """

        if sOption == 'helppage':
            self.cHelpDataGrabber.SetHelpFileName(str(sValue))
        elif sOption == 'aboutpage':
            self.cAboutDataGrabber.SetAboutFileName(str(sValue))
        elif sOption == 'activepage':
            self.sActiveFilename = str(sValue)
        elif sOption == 'inactivepage':
            self.sInactiveFilename = str(sValue)
        elif sOption == 'endpage':
            self.sEndFilename = str(sValue)



    def AcceptCommand(self, sUrl):
        """accept command from pProxy

        Parse url and generate html-answer.


        sUrl    -- complete url containing command

        return  -- html code with answer

        """

        # parse url -> only need to know sQuery
        sScheme, iHostport, sPath, lParams, sQuery, fragment = urlparse.urlparse(sUrl)

        # detect file requests
        if sPath.endswith('.gif') or sPath.endswith('.jpg') or sPath.endswith('.png'):
            pManager.manager.DebugStr('cGuiRequestHandler '+ __version__ +': Query for gif "'+str(sPath)+'"', 3)
            # return gif
            return self.cBinaryDataGrabber.GetData(sPath)
        if sPath.endswith('.html'):
            pManager.manager.DebugStr('cGuiRequestHandler '+ __version__ +': Query for html "'+str(sPath)+'"', 3)
            # return html
            return self.cBinaryDataGrabber.GetData(sPath)

        # log query
        pManager.manager.DebugStr('cGuiRequestHandler '+ __version__ +': Got Query: '+str(sQuery), 2)

        # Get dictionary containing all options / values for request
        dQuery = cgi.parse_qs(sQuery)

        dParams ={}
        if len(dQuery.keys()) == 0:
            # No request. Display default iOwl page
            return self.cDefaultDataGrabber.GetHtml(dParams)

        # parse query
        sCommand, dParams = self.cCommandValidator.ValidateQuery(dQuery)

        # execute command
        if sCommand == 'showhelp':
            # return help page
            return self.cHelpDataGrabber.GetHtml(dParams)
        elif sCommand == 'showabout':
            # return about page
            return self.cAboutDataGrabber.GetHtml(dParams)
        elif sCommand == 'showhistory':
            # return history page
            # --> return default page
            return self.cDefaultDataGrabber.GetHtml(dParams)
        elif sCommand == 'showlog':
            # return logfile page
            return self.cLogfileGrabber.GetHtml(dParams)
        elif sCommand == 'showconfig':
            # return configuration page
            return self.cConfigureGrabber.GetHtml(dParams)
        elif sCommand == 'singlerecommendation':
            # return single recommendation for url stored in dParams
            return self.cSingleRecommendationDataGrabber.GetHtml(dParams)
        elif sCommand == 'sessionrecommendation':
            # return recommendations for current session
            return self.cSessionRecommendationDataGrabber.GetHtml(dParams)
        elif sCommand == 'longtermrecommendation':
            # return all-time recommendations
            return self.cLongtermRecommendationDataGrabber.GetHtml(dParams)
        elif sCommand == 'getrecommendations':
            # return single recommendation for url stored in dParams
            return self.cGetRecommendationsDataGrabber.GetHtml(dParams)
        elif sCommand == 'activate':
            # activate clickstream recording
            pManager.manager.UpdateConfig('pProxy','recording','1')
            # return mainpage
            return self.cDefaultDataGrabber.GetHtml(dParams)
        elif sCommand == 'deactivate':
            # deactivate clickstream recording
            pManager.manager.UpdateConfig('pProxy','recording','0')
            # return mainpage
            return self.cDefaultDataGrabber.GetHtml(dParams)
        elif sCommand == 'remove':
            # remove url from clickstream
            # get clickstreaminterface
            cs = pManager.manager.GetClickstreamInterface()
            # remove url from clickstream
            cs.RemoveUrl(dParams['sUrl'])
            return self.cDefaultDataGrabber.GetHtml(dParams)
        elif sCommand == 'updateconfig':
            # update configuration
            pManager.manager.UpdateConfig(dParams['section'], dParams['option'], dParams['value'])
            # return updated config dialog
            return self.cConfigureGrabber.GetHtml(dParams)
        elif sCommand == 'error':
            # return error page
            return self.cErrorDataGrabber.GetHtml(dParams)





    def GetHeader(self, sTitle, sScript='', sFunction=''):
        """return header part for iOwl-pages

        sTitle - title of page
        sScript - script to include in header
        sFunction - function to start in body-tag

        returns -- string containg <html>....<body>

        """

        sData = ''
        if sScript =='':
            # no scripts needed
            sData = """<html>
                    <head>
                    <title>%s</title>
                    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
                    <base href="http://my.iowl.net/">
                    </head>
                    <body bgcolor="#CCCCCC" text="#000000" link="#AA0000" vlink="#880000" alink="#AA0000" background="data/pix/back.gif">
                    """ %sTitle
        else:
            # need script in header and attribute onload="..."
            sData = """<html>
                    <head>
                    <title>%s</title>
                    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
                    <base href="http://my.iowl.net/">
                    %s
                    </head>
                    <body bgcolor="#BBBBBB" text="#000000" link="#AA0000" vlink="#880000" alink="#AA0000" background="data/pix/back.gif" onload ="%s">
                    """ % (sTitle, sScript, sFunction)

        return sData


    def GetActivePage(self):
        """Return first part of guipage with state == active """

        # load from disc
        file = open(self.sActiveFilename, 'r')

        # read activefile to string
        sContent = file.read()

        return sContent


    def GetInactivePage(self):
        """Return first part of guipage with state == inactive """

        # load from disc
        file = open(self.sInactiveFilename, 'r')

        # read inactivefile to string
        sContent = file.read()

        return sContent


    def GetEndPage(self):
        """Return end part of guipage"""
        # load from disc
        file = open(self.sEndFilename, 'r')

        # read endfile to string
        sContent = file.read()

        return sContent




##########################################################################################
### TEST FUNCTIONS #######################################################################

def test():
    # url to test
    sUrl = 'http://my.iowl.net/command?action=saveconfig&proxyip=1.2.3.4&proxyport=4096'
    sEmpty = 'http://my.iowl.net'
    sEmpty2 = 'http://my.iowl.net/'
    sEmpty3 = 'http://my.iowl.net/index.html'


    """
    handler = cGuiRequestHandler()

    handler.AcceptCommand(sUrl)
    handler.AcceptCommand(sEmpty)
    handler.AcceptCommand(sEmpty2)
    handler.AcceptCommand(sEmpty3)
    """

if __name__=='__main__':
    test()














