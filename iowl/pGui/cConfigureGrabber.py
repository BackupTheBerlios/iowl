__version__ = "$Revision: 1.5 $"

"""
$Log: cConfigureGrabber.py,v $
Revision 1.5  2002/03/02 14:32:49  Saruman
Fix bug #132: Configuration now works without javascript.

Revision 1.4  2002/02/19 18:53:57  aharth
tried to unify UI

Revision 1.3  2002/01/29 20:35:23  Saruman
changed priority of debug output

Revision 1.2  2001/08/10 18:31:48  i10614
minor cleanups

Revision 1.1  2001/07/15 10:14:15  i10614
initial commit



"""

import pManager

class cConfigureGrabber:
    """Responsible for displaying configuration page"""

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
        sHeader = self.cGui.GetHeader('iOwl.net - Configuration')

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

        # header
        sContent = '<h2>Configuration</h2>'

        # get content
        sContent = sContent + self.ParseConfig()

        # get end part
        sPart2 = self.cGui.GetEndPage()

        # Glue it
        sPage = sHeader + sPart1 + sContent + sPart2

        # return page and content-type
        return sPage, 'text/html'


    def ParseConfig(self):
        """Read configfile and build configuration
        page

        """

        # get configfile from manager
        Config = pManager.manager.GetConfHandle()

        sContent = ""

        for sect in Config.sections():
            # start table
            sContent = sContent + '\n<p>\n    <table border>\n'
            # header
            sContent = sContent + '        <tr>\n            <th colspan="3">'+sect+'</th>\n        </tr>'
            # iterate over available options for this section
            for opt in Config.options(sect):
                value = Config.get(sect,opt)
                # start formular
                sFormName = sect+opt
                sForm = """
        <tr>
            <form name="%s" method="get" action="http://my.iowl.net/command?">
            <td>%s</td>
            <input type="hidden" name="action" value="updateconfig">
            <input type="hidden" name="section" value="%s">
            <input type="hidden" name="option" value="%s">
            <td><input name="value" size=20 maxlength=40 value="%s"></td>
            <td><input type="submit" value=" Absenden "></td>
            </form>
        </tr>""" %(sFormName, opt, sect, opt, value)

                sContent = sContent + sForm

            # end table
            sContent = sContent + '\n    </table>\n</p>'

        # done all sections
        return sContent









##################################
if __name__=='__main__':
    import ConfigParser
    sContent = "<html><body>"
    cg = cConfigureGrabber(None)
    sContent = cg.ParseConfig(sContent)
    sContent = sContent + '</body></html>'
    print sContent











