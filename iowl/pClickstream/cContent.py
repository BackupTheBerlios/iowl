
__version__ = "$Revision: 1.3 $"

"""
$Log: cContent.py,v $
Revision 1.3  2002/03/18 14:25:59  aharth
try/except for title extraction

Revision 1.2  2002/03/16 13:30:35  aharth
bugfixes for #104 and #139

Revision 1.1  2002/03/16 11:03:25  aharth
added title extraction to pclickstream


"""

import urlparse
import string
import cDOM

import htmllib
import formatter

class SearchContent(htmllib.HTMLParser):
    """ HTML parser class inherited from htmllib """
    
    def __init__(self):
        self.start = 0
        self.c_data = ''
        self.title = ''
        self.alist = []
        htmllib.HTMLParser.__init__(self, formatter.NullFormatter())

    def anchor_bgn(self,href,name,type):
        #print "start_a href:", href, "\nname:", name, "\ntype:", type
        self.href = href
        self.c_data = ""

    def anchor_end(self):
        # check wheter anchor has href attribute
        if len(self.href) != 0:
            self.alist.append([self.href, self.c_data])

    def start_title(self, attrs):
        self.c_data = ""

    def end_title(self):
        # return a copy of the data variable
        self.title = self.c_data

    def handle_data(self, data):
        self.c_data = self.c_data+data

    def getTitle(self):
        return self.title
    
    def getLinkList(self):
        return self.alist



class cContent:

    """Content class.

    Parses content from html. Title extraction is all right now.

    """

    def __init__(self, htmlstr):
        self.htmlstr = htmlstr


    def GetTitle(self):
        """ Extract title from html string. """
        parser = SearchContent()
        parser.feed(self.htmlstr)
        sTitle = '(Untitled)'
        # try to extract title
        try:
            sTitle = parser.getTitle()
        # doesn't work? nevermind
        except:
            pass

        # strip leading and trailing whitespace
        sTitle = string.strip(sTitle)
            
        # be sure to get rid of umlauts etc
        sTitle = self.FilterUmlauts(sTitle)
            
        return sTitle


    def ClickIsValid(self, click):
        """Verify given click

        examines the click to prevent logging database-driven
        sites, passwords, cgi-bins etc.

        throw away:
            - wrong type of file (there are lots of .jpgs passed
              as text/html...)
            - username:password in uri
            - cgi-bins in uri

        If referrer contains a invalid uri, referrer gets deleted.


        XXX - modify invalid clicks (remove "user:password@", strip cgi-bins down
              to plain host/path/...) or just throw them away?

        return true if click should be recorded, false otherwise.

        """

        # tuple of strings that are not allowed in clicks:
        # ? -> cgi-bins
        # @ -> user/password
        # = -> doubleclick stuff
        tKillUrls = '?', '@', '='

        # tuple of endings that are not allowed:
        tKillTypes = '.jpg', '.gif', '.css'

        # get click data - lowercase
        sUrl = string.lower(urlparse.urlunparse(click.GetUrl()))
        sReferer = string.lower(urlparse.urlunparse(click.GetRefererUrl()))

        # check filetype
        for sType in tKillTypes:
            if sUrl.endswith(sType):
                # ignore click
                return 0

        # check url
        for sKiller in tKillUrls:
            if sKiller in sUrl:
                # ignore click
                return 0

        # url is okay. Now check referrer
        for sKiller in tKillUrls:
            if sKiller in sReferer:
                # just delete the referrer
                click.DeleteReferer()

        # this click is okay
        return 1


    def FilterUmlauts(self, s):
        """a quick hack to get rid of umlauts..."""
        
        dict={'ä':'ae', 'ö':'oe', 'ü':'ue', 'ß':'ss'}
        for key in dict.keys():
            s = s.replace(key, dict[key])
        return s





