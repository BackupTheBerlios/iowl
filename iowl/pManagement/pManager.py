
__version__ = "$Revision: 1.14 $"

"""
$Log: pManager.py,v $
Revision 1.14  2001/07/15 14:38:39  i10614
implemented config-change from GUI

Revision 1.13  2001/07/15 10:18:39  i10614
added functions to get logfile and configfile handles

Revision 1.12  2001/05/26 14:00:58  i10614
changed default params

Revision 1.11  2001/05/26 13:00:49  i10614
changed iowl version and formated it

Revision 1.10  2001/05/26 11:40:34  i10614
added changing trayicon

Revision 1.9  2001/05/20 16:16:22  i10614
small changes for .exe-building

Revision 1.8  2001/04/22 13:26:10  i10614
modified starting to enable codefork depending on platform

Revision 1.7  2001/04/16 13:06:21  i10614
experimental GUI added

Revision 1.6  2001/04/14 14:56:51  i10614
cosmetic changes

Revision 1.5  2001/04/07 17:06:24  i10614
many, many bugfixes for working network communication

Revision 1.4  2001/03/29 23:31:41  i10614
now takes care of path (data/pix/pixc.gif)

Revision 1.3  2001/03/28 15:29:37  i10614
renamed timer to watchdog to prevent collisions with win32 extensions

Revision 1.2  2001/03/26 12:09:21  i10614
added version and build

Revision 1.1.1.1  2001/03/24 19:22:36  i10614
Initial import to stio1 from my cvs-tree

Revision 1.23  2001/02/21 16:27:44  mbauer
added flush() to logfile-writing

Revision 1.22  2001/02/20 20:59:08  a
added interfaces for AssocRules and Recommendation

Revision 1.21  2001/02/20 17:38:06  mbauer
activated GUI

Revision 1.20  2001/02/19 19:19:51  mbauer
Added algorithm to detect the correct IP adress when having more than one interface

Revision 1.17  2001/02/18 19:55:58  mbauer
activated pProxy

Revision 1.16  2001/02/17 13:32:22  mbauer
removed some debug output

Revision 1.14  2001/02/14 21:45:02  mbauer
Added Watchdog-functions

Revision 1.13  2001/02/14 19:11:52  mbauer
added GetInterface-methods

Revision 1.11  2001/02/14 17:22:12  a
minor changes

Revision 1.10  2001/02/14 10:27:13  mbauer
moved entrypoint to pNetwork
added manual shutdown as pGui is not yet finished

Revision 1.9  2001/02/14 09:50:12  mbauer
removed some debug output

Revision 1.8  2001/02/13 22:38:10  mbauer
added timer and register()

Revision 1.5  2001/02/13 20:53:35  mbauer
Added function SaveParam()

Revision 1.4  2001/02/13 20:12:31  mbauer
major updates in pManager, more sections in iowl.cfg

Revision 1.2  2001/02/12 23:13:32  mbauer
test version for config

Revision 1.1  2001/02/12 22:55:08  mbauer
Initial Version


"""

import os
import thread
import mutex
import ConfigParser
import string
import time
import watchdog
import whrandom
import socket
import sys

import pProxyInterface
import pClickstreamInterface
import pGuiInterface
import pAssocRulesInterface
import pRecommendationInterface
import pNetworkInterface
import pStatisticsInterface


class cManager:

    """ This is the main class for package pManager.

    pManager is responsible for starting and stopping the
    modules of iOwl.net and provides some utility functions.
    A reference to pManager is passed on to all other classes.

    """

    # This is a "static" lock object (Semaphore) for debug output. It is the same
    # for all instances of cManager. (Most probably there is never more than only one
    # instance though...)
    DbgLock = thread.allocate_lock()


    def __init__(self, sConfigFileName):
        """Constructor."""

        # version
        self.iOwlVersion = 1.0

        # build date
        self.sBuild = '14 2001-05-26'

        # default logfile
        self.sLogFileName = "data/iowl.log"

        # open logfile in append mode
        try:
            self.LogFileHandle = open(self.sLogFileName, 'a')
        except:
            print('pManager v.'+ __version__ +': Can\'t open Logfile "'+self.sLogFileName+'"')

        # create timer
        self.timer = watchdog.timer()

        # my state
        self.bIsRunning = 0

        # tray icon
        self.tray=None

        # init parser for configfile
        self.Config = ConfigParser.ConfigParser()
        self.sConfigFileName = sConfigFileName

        # default Debug-level: 0 -> console only
        #                      1 -> logfile only
        #                      2 -> both
        self.iDebugLevel = 1


        # get basedir
        self.sBaseDir=os.getcwd()
        self.DebugStr('pManager '+ __version__ +': Basedir is "'+self.sBaseDir+'".')


    def DebugStr(self, sDebugInfo):
        """Handles Debug-Output from all classes.

        According to debuglevel either dump message to
        console (level 0), append it to logfile (level 1),
        or do both (level 2).
        Complete message with a timestamp prior to printing.

        sDebugInfo -- string containing message

        """

        # Queue up for critical section - only one output a time!
        # Acquire Lock
        self.DbgLock.acquire()

        # Build timestamp
        message = time.strftime('%d.%m.%y %H:%M:%S', time.localtime(time.time()))
        message = message + ' -- '
        message = message + sDebugInfo

        # Handle output according to debuglevel
        if self.iDebugLevel == 0:
            print(message)
        elif self.iDebugLevel == 1:
            # write message to logfile only
            self.LogFileHandle.write(message+'\n')
            self.LogFileHandle.flush()
        elif self.iDebugLevel == 2:
            # Write message to logfile and print on console
            print(message)
            self.LogFileHandle.write(message+'\n')
            self.LogFileHandle.flush()

        # now its safe to release Lock
        self.DbgLock.release()


    def StartOwl(self):
        """Start the iOwl.

        Called by mainloop. Initializes and starts all packages. Focus does not return
        until iOwl is completely shut down.

        """

        # initialize iOwl
        self.Initialize()

        # Set Config for all packages (including myself)
        self.SetConfig()

        # Log start of iOwl
        self.DebugStr('pManager '+ __version__ +': Starting iOwl...')

        # Start all Packages
        self.StartPackages()

        # iOwl is shut down. Return to main().
        return


    def Initialize(self):
        """Initialize the interface classes."""

        # Create instances
        self.intfProxy = pProxyInterface.pProxyInterface()
        self.intfClickstream = pClickstreamInterface.pClickstreamInterface()
        self.intfGui = pGuiInterface.pGuiInterface()
        self.intfAssocRules = pAssocRulesInterface.pAssocRulesInterface()
        self.intfRecommendation = pRecommendationInterface.pRecommendationInterface()
        self.intfNetwork = pNetworkInterface.pNetworkInterface()
        self.intfStatistics = pStatisticsInterface.pStatisticsInterface()

        # Create dictionary for all available packages and their interface-class
        # Need this for SetConfig()
        self.dPackages = {
            'pProxy': self.intfProxy,
            'pClickstream': self.intfClickstream,
            'pGui': self.intfGui,
            'pAssocRules': self.intfAssocRules,
            'pRecommendation': self.intfRecommendation,
            'pStatistics': self.intfStatistics,
            'pNetwork': self.intfNetwork,
            'pManager': self
            }


    def SetConfig(self):
        """Reads configfile and calls for each entry in each section
        interface.SetParam.

        ConfigFile has to be specified at commandline.

        """

        self.DebugStr('pManager '+ __version__ +': Info -- parsing config file.')

        # check for existance of configfile
        if not os.access(self.sConfigFileName,os.F_OK):
            # cant find configfile. Create an empty one.
            ConfHandle = open(self.sConfigFileName, 'w')
            for sect in self.dPackages.keys():
                self.Config.add_section(sect)

            self.Config.write(ConfHandle)
            ConfHandle.close()


        # read configfile
        self.Config.read(self.sConfigFileName)

        # iterate over available sections
        for sect in self.Config.sections():
            # Look if this section is valid
            if sect in self.dPackages.keys():
                # self.DebugStr('pManager '+ __version__ +': Setting Options for package "'+sect+'".')
                # iterate over available options for this section
                for opt in self.Config.options(sect):
                    # call SetParam() for each option.
                    # self.DebugStr('pManager '+ __version__ +': Setting Option "'+opt+'" with value "'+ self.Config.get(sect,opt)+'".')
                    self.dPackages[sect].SetParam(opt, self.Config.get(sect,opt))
            else:
                # This is an unknown section!
                self.DebugStr('pManager '+ __version__ +': Warning: Skipping unknown section "'+sect+'" in configfile "'+self.sConfigFileName+'"')

        self.DebugStr('pManager '+ __version__ +': Info -- finished parsing config file.')


    def GetConfHandle(self):
        """return configparser"""
        return self.Config


    def SetParam(self, sOption, sValue):
        """ Accept settings

        Available parameters:

        logfilename -- complete path to logfile
        debuglevel -- Debug Level (0,1,2)

        """

        if sOption == 'logfilename':
            # if names differ -> close old logfile, open new one
            if self.sLogFileName != sValue:
                # Acquire Lock
                self.DbgLock.acquire()
                # close old file
                self.LogFileHandle.close()
                # store new name
                self.sLogFileName = sValue
                # open new logfile in append mode
                try:
                    self.LogFileHandle = open(self.sLogFileName, 'a')
                finally:
                    # release lock
                    self.DbgLock.release()

        elif sOption == 'debuglevel':
            self.iDebugLevel = int(sValue)

        else:
            # unknown option!
            self.DebugStr('pManager '+ __version__ +': Warning: Trying to set unknown parameter "'+sOption+'".')


    def UpdateConfig(self, sSection, sOption, sValue):
        """Update configuration of running iOwl.

        Called by pGui if user changes options through GUI.

        sSection -- Section in Configfile
        sOption  -- Option to set
        sValue   -- Value for option

        returns true if successfull set new param, false otherwise

        """

        # is section valid?
        if sSection in self.dPackages.keys():
            # self.DebugStr('pManager '+ __version__ +': Setting Options for package "'+sSection+'".')
            # set new parameter
            try:
                self.dPackages[sSection].SetParam(sOption, sValue)
            except:
                # could not set option!
                return 0

            # now save to configfile to make changes permanent
            self.SaveParam(sSection, sOption, sValue)
            # okay, return
            return 1

        else:
            # unknown section!
            return 0


    def SaveParam(self, sSection, sOption, sValue):
        """Save given data in configfile

        sSection -- Section in Configfile
        sOption  -- Option to set
        sValue   -- Value for option

        """

        self.DebugStr('pManager '+ __version__ +': Updating Configfile ['+sSection+','+sOption+','+sValue+'].')

        # update ConfigParser
        self.Config.set(sSection, sOption, sValue)

        # get filehandle
        ConfHandle = open(self.sConfigFileName, 'w')

        # write file
        self.Config.write(ConfHandle)

        # close filehandle
        ConfHandle.close()


    def StartPackages(self):
        """Activate all packages

        Here begins real operation of iOwl.net.
        Focus does only return from pProxy if iOwl is shut down.

        """

        self.intfClickstream.Start()
        self.intfGui.Start()
        self.intfAssocRules.Start()
        self.intfRecommendation.Start()
        self.intfNetwork.Start()
        self.intfStatistics.Start()

        # we are running
        self.bIsRunning = 1

        # Focus does not come back from pProxy until iOwl is shut down
        self.intfProxy.Start()

        # we are running
        self.bIsRunning = 0

        # Focus returned. iOwl is shut down.
        self.DebugStr('pManager '+ __version__ +': iOwl shut down. Now exiting.')


    # Interface provider functions:
    def GetClickstreamInterface(self):
        """return ClickstreamInterface"""
        return self.intfClickstream

    def GetGuiInterface(self):
        """return GuiInterface"""
        return self.intfGui

    def GetAssocRulesInterface(self):
        """return AssocRulesInterface"""
        return self.intfAssocRules

    def GetRecommendationInterface(self):
        """return RecommendationInterface"""
        return self.intfRecommendation

    def GetNetworkInterface(self):
        """return NetworkInterface"""
        return self.intfNetwork

    def GetStatisticsInterface(self):
        """return StatisticsInterface"""
        return self.intfStatistics

    def GetProxyInterface(self):
        """return ProxyInterface"""
        return self.intfProxy


    def ShutDown(self):
        """Initiate shutdown

        Call each package's shutdown().

        XXX Maybe should start own thread for shutting down? Probably
            collisions with active focus if pProxy is stopped from its own thread.

        """

        self.intfClickstream.Shutdown()
        self.intfGui.Shutdown()
        self.intfAssocRules.Shutdown()
        self.intfRecommendation.Shutdown()
        self.intfNetwork.Shutdown()
        self.intfStatistics.Shutdown()
        self.intfProxy.ShutDown()

        # close logfile
        try:
            self.LogFileHandle.close()
        except:
            pass

        # exit
        # sys.exit()
        # try alternative with os
        os._exit(0)

    def GetVersion(self):
        """return version of iOwl"""
        return str(self.iOwlVersion)


    def GetBuild(self):
        """return date of build"""
        return str(self.sBuild)


    def GetOwnIP(self):
        """return own ip-number"""
        return self.sOwnIP


    def GetBaseDir(self):
        """return string containing base iOwl directory"""
        return self.sBaseDir


    def SetDebugLevel(self, iLevel):
        """Set Debug-level.

        iLevel -- Type of Debug: 0 -> Console only
                                 1 -> Logfile only
                                 2 -> Both

        """

        # set level
        self.iDebugLevel = iLevel

        # log change
        # self.DebugStr('pManager '+ __version__ +': Changed Debug-level to ' + str(iLevel) + '.')


    def RegisterWatchdog(self, function, interval):
        """register a function to call every <interval> seconds

        This is a simple mapping to timer class.
        Once registered, functions get called as long as cManager exists.
        Registered function gets called with interval as argument.

        """

        # register with timer
        return self.timer.register(function, interval)


    def ResetWatchdog(self, id):
        """reset timer-id"""

        self.timer.reset(id)


    def StopWatchdog(self, id):
        """Stop timer"""

        self.timer.stop(id)


    def GetUniqueNumber(self):
        """returns a unique 20-digit sequence

        Used to give network-packets and requests a unique id.

        XXX - Need a better method to provide REALLY global unique
              identifiers AND be anonymous as possible

        return -- a 20-digit sequence of numbers (string)

        """

        sNumber = ''
        for i in range(20):
            sNumber = sNumber + str(whrandom.randint(0,9))

        return sNumber


    def SetOwnIP(self, ownIP):
        """Set Own IP"""
        self.DebugStr('pManager '+ __version__ +': Setting own IP to ' + str(ownIP)+ '.')
        self.sOwnIP = ownIP


    def SetTray(self, tray):
        """Set trayicon-handle"""
        self.tray = tray


    def SetIcon(self, bState):
        """Change trayicon"""

        if self.tray==None:
            return

        self.tray.SetIcon(bState)


    def GetLogfilePath(self):
        """return string containing path to logfile"""

        return self.sLogFileName




####################################################################
## TEST FUNCTIONS ##################################################

def test():
    m = cManager('iowl.cfg')
    # m.StartOwl()
    m.Initialize()
    # m.SetDebugLevel(2)
    m.SetConfig()
    m.SaveParam('pManager','entryport','2323')

def test2():
    m = cManager('iowl.cfg')
    m.SetDebugLevel(2)
    m.SetParam('logfilename','testlog')
    m.DebugStr("blafasel")

def DebugStrTest():
    class tester:
        def __init__(self, pm, text):
            self.pm = pm
            self.text = text

        def run(self):
            print('starting thread!')
            thread.start_new_thread(self.f,())

        def f(self):
            for i in range(1000):
                self.pm.DebugStr(self.text)


    man = cManager('iowl.cfg')
    man.SetDebugLevel(0)

    t1 = tester(man, 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    t2 = tester(man, 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')

    t1.run()
    t2.f()

def test3():
    man = cManager('iowl.cfg')
    for i in range(10):
        print man.GetUniqueNumber()

if __name__ == '__main__':
    # DebugStrTest()
    test3()

