
__version__ = "$Revision: 1.6 $"

"""
$Log: pClickstreamInterface.py,v $
Revision 1.6  2001/03/29 22:45:42  i10614
Catch self.Session == None in GetHistory()

Revision 1.5  2001/03/27 18:22:12  i10614
Changed Session handling. A new session is created inside AddClick(). Whith
each new Session a new watchdog is registered.
The Watchdog now calls CloseSession() and gets discarded.

Revision 1.4  2001/03/26 17:48:01  i10614
activated filtering of invalid urls

Revision 1.3  2001/03/24 23:26:50  i10614
fixed bug when creating lots of empty sessions.

Revision 1.2  2001/03/24 19:27:41  i10614
cvs does not like empty dirs while importing. Trying to add manually.

Revision 1.1.1.1  2001/03/24 19:22:33  i10614
Initial import to stio1 from my cvs-tree

Revision 1.20  2001/03/19 23:10:30  mbauer
changed os.path.normpath() to os.path.normcase(). I'm too tired ;-)

Revision 1.18  2001/03/19 00:41:30  mbauer
added better handling for corrupt xml-files

Revision 1.17  2001/03/17 15:19:35  mbauer
removed lots of debug output

Revision 1.16  2001/02/22 23:38:32  a
added comment only

Revision 1.15  2001/02/22 21:53:18  a
bug fixes for supporting history list

Revision 1.14  2001/02/22 15:12:27  a
added RemoveUrl method

Revision 1.13  2001/02/21 16:02:57  a
minor changes

Revision 1.12  2001/02/21 14:28:25  a
embedded sessions handling into pClickstreamInterface

Revision 1.11  2001/02/20 21:40:31  a
minor changes

Revision 1.10  2001/02/20 20:33:19  a
added Get* methods

Revision 1.9  2001/02/20 18:02:59  a
minor bugfix

Revision 1.8  2001/02/20 17:36:20  a
supporting different clickstream files

Revision 1.7  2001/02/19 17:46:21  a
added cClick class

Revision 1.6  2001/02/19 11:34:53  mbauer
fixed spelling ;-)

Revision 1.5  2001/02/19 11:23:26  a
added AddClick with arguments

Revision 1.4  2001/02/14 20:29:23  a
don't know really what changed ;-)

Revision 1.3  2001/02/14 17:31:15  a
added cData

Revision 1.2  2001/02/14 17:22:11  a
minor changes

Revision 1.1  2001/02/14 16:02:33  a
initial release of pClickstream


"""

import cSession
import urlparse
import re
import os
import time
import string
import pManager

class pClickstreamInterface:

    """Core clickstream class.
    
    Storing sessions in memory and on disk as xml files.

    """

    def __init__(self):
        """Constructor."""
        # clickstream is stored in clickstream2001-93-435.xml
        self.sClickstreamPathName = 'data/'
        self.iWatchdogID = 0
        self.iRestart = 1200
        self.lSessions = []
        self.SetFileName()
        self.Session = None


    def SetFileName(self):
        """Set filename with current timestamp."""
        self.sClickstreamFileName = 'clickstream'+str(time.time())+'.xml'


    def Start(self):
        """Kind of constructor."""

        # read old sessions
        self.OpenSessions()

        # Mike - changed session management, watchdog registering now happens in StartNewSession(),
        #        StartNewSession() is called from within AddClick()

        # start current session
        # self.StartNewSession()

        # register watchdog
        # if self.iWatchdogID == 0:
        #     self.iWatchdogID = pManager.manager.RegisterWatchdog(\
        #         self.StartNewSession, self.iRestart)


    def SetParam(self, sParameter, sValue):
        """Get config from pManagement.

        sParameter -- key
        sValue -- value

        """
        if (sParameter == 'clickstreampathname'):
            self.sClickstreamPathName = sValue
        elif (sParameter == 'restartsession'):
            self.iRestart = string.atoi(sValue)


    def Shutdown(self):
        """Kind of destructor."""

        pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Shutting down.')

        # Mike
        try:
            self.Session.CloseFile()
        except:
            # could not close file, probably because Session is not yet created
            # Happens when start of iOwl fails (mostly common "adress in use" - Error)
            pass


    def RemoveUrl(self, sUrl):
        """Remove URL in clickstream.

        sUrl -- url

        """
        # XXX                 should be string
        tUrl = urlparse.urlparse(sUrl[0])

        lSessions = self.GetSessions()

        for session in lSessions:
            session.RemoveUrl(tUrl)


    def GetSessions(self):
        """Return a list of sessions.

        return -- lSessions, list of sessions read from disk

        """
        # self.lSessions stores only the last sessions
        # current session is in self.Session
        list = self.lSessions[:]
        if self.Session != None:
            list.append(self.Session)
        list.reverse()
        return list


    def GetItemCount(self):
        """Return number of all items in clickstream.

        return -- iCount, overall number of urls

        """
        iCount = 0
        for session in self.lSessions:
            iCount = iCount+session.GetClicksCount()

        return iCount


    def OpenSessions(self):
        """Read sessions into list."""

        # XXX OpenSessions is called periodically
        # should only be called once
        # ...and from sessions on disk
        # XXX gefixt - Mike

        # normalize path: no change on unix, lowercase and forward slashes on win32
        self.sClickstreamPathName = os.path.normcase(self.sClickstreamPathName)

        list = os.listdir(self.sClickstreamPathName)
        for file in list:
            match = re.compile("""clickstream.*xml$""")
            if match.match(file):
                session = cSession.cSession()
                fullname = os.path.join(self.sClickstreamPathName, file)
                try:
                    session.OpenFile(fullname)
                    self.lSessions.append(session)
                except:
                    # Probably corrupt xml-file on disk.
                    # Log error and continue
                    pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Warning: Could not read/parse clickstream file "'+str(fullname)+'"')
                    # try to close file
                    try:
                        session.CloseFile()
                    except:
                        pass
                    # rename file to prevent further read/write attempts
                    sNewName = fullname + '_broken'
                    pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Renaming file "'+str(fullname)+'" to "'+sNewName+'".')
                    try:
                        os.rename(fullname, sNewName)
                    except:
                        pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Could not rename file "'+str(fullname)+'". Please move/delete it yourself.')


    def CloseSession(self):
        """Close current session.

        Called by watchdog when session is over.

        XXX - Re-calculate assorules when a new session is finished!

        """

        # stop watchdog, he has done its duty.
        pManager.manager.StopWatchdog(self.iWatchdogID)
        self.iWatchdogID = 0

        if self.Session == None:
            # no active session
            pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Warning: Trying to close non-existant session.')
            return


        pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Closing current session.')
        # append old session to list of all available sessions
        if self.Session.GetClicksCount() > 0:
            self.lSessions.append(self.Session)
        else:
            pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Warning: Session is empty.')

        # close old session
        try:
            self.Session.CloseFile()
        except:
            pass

        # clear current session
        self.Session = None



    def StartNewSession(self):
        """Starting new session.

        """

        pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Starting new session.')

        # check if there is an old session active
        if self.Session != None:
            pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Error! Trying to start new session while there already is one.')
            return

        # Build new session
        self.Session = cSession.cSession()
        self.SetFileName()
        sFileName = os.path.join(self.sClickstreamPathName, self.sClickstreamFileName)
        self.Session.OpenFile(sFileName)

        # Register watchdog
        if self.iWatchdogID == 0:
            self.iWatchdogID = pManager.manager.RegisterWatchdog(self.CloseSession, self.iRestart)
        else:
            pManager.manager.DebugStr('pClickstreamInterface '+ __version__ +': Error! Trying to register watchdog while there already is one.')



    def AddClick(self, click):
        """Add click to internal list.

        if there is no session active, start a new one.

        """

        if self.Session == None:
            # First start a session
            self.StartNewSession()

        if self.ClickIsValid(click) > 0:
            # Okay, click is valid. Append to session.
            self.Session.AddClick(click)
            self.WasAdded = 1
        else:
            # click should not be recorded!
            pManager.manager.DebugStr('cClickstream '+ __version__ +': Did not add click to session.')

        # reset watchdog regardless wether click is recorded or not
        pManager.manager.ResetWatchdog(self.iWatchdogID)


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
        tKillUrls = '?', '@'

        # tuple of endings that are not allowed:
        tKillTypes = '.jpg', '.gif'

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


    def HasItemset(self, itemset):
        """Check whether itemset is in clickstream or not.

        itemset -- itemset to be checked if in clickstream

        """
        self.Session.HasItemset(itemset)


    def GetHistory(self):
        """ Return history. XXX show n entries or x sessions

        return -- list of clicks

        """

        if self.Session != None:
            return self.Session.GetClicks()
        else:
            # return empty list
            return []


####################################################################
## TEST FUNCTIONS ##################################################


def test2():
    """Built-in test method for this class."""
    
    click = pClickstreamInterface()
    click.SetParam('clickstreampathname', '/tmp/')
    click.Start()
    lSessions = click.GetSessions()
    for s in lSessions:
        for c in s.GetClicks():
            print urlparse.urlunparse(c.GetUrl())
    click.StartNewSession()
    click.Shutdown()

    while 1:
        pass


def test():
    """Built-in test method for this class."""
    
    import cClick
    
    clstream = pClickstreamInterface()
    clstream.SetParam('clickstreamfilename', '/tmp/clickstream.xml')
    clstream.Start()

    urltuple = urlparse.urlparse("http://harth.org")

    click = cClick.cClick()
    click.SetClick(urltuple, 'text/html', '200', '4625', 'ne seite', urltuple)
    
    clstream.Session.AddClick(click)

    #click.DeleteURL("http://www.schmuddel.com/")

    """
    i = 0
    while i < 1000:
        urltuple = urlparse.urlparse("http://slashdot.org"+str(i))
        click.Session.AddClick(urltuple, 'text/html', '200', '11:49:34', 'das ist eine html seite', urltuple2)
        i = i+1
    """
    
    clstream.Shutdown()


if __name__ == '__main__':
    pManager.manager = pManager.cManager('')
    test2()
