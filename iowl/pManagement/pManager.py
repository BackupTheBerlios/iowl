
__version__ = "$Revision: 1.1 $"

"""
$Log: pManager.py,v $
Revision 1.1  2001/03/24 19:22:36  i10614
Initial revision

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
import timer
import whrandom
import socket


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
        self.iOwlVersion = 0.2

        # create timer
        self.timer = timer.timer()

        # init parser for configfile
        self.Config = ConfigParser.ConfigParser()
        self.sConfigFileName = sConfigFileName

        # default Debug-level: 0 -> console only
        #                      1 -> logfile only
        #                      2 -> both
        self.iDebugLevel = 0

        # set own ip
        # XXX What to do if adress changes while owl is running?
        #     What to do if machine has more than one interface?
        #self.sOwnIP = socket.gethostbyname(socket.gethostname())

        # default logfile
        self.sLogFileName = "iowl.log"

        # open logfile in append mode
        try:
            self.LogFileHandle = open(self.sLogFileName, 'a')
        except:
            print('pManager v.'+ __version__ +': Can\'t open Logfile "'+self.sLogFileName+'"')


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

        # XXX - Manual shutdown since pGui is not finished yet!
        time.sleep(3)
        self.ShutDown()

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



    def SetParam(self, sOption, sValue):
        """ Accept settings

        Available parameters:

        logfilename -- complete path to logfile
        debuglevel -- Debug Level (0,1,2)

        """

        if sOption == 'logfilename':
            # if names differ -> close old logfile, open new one
            if self.sLogFileName != sValue:
                # close old file
                self.LogFileHandle.close()
                # store new name
                self.sLogFileName = sValue
                # open new logfile in append mode
                try:
                    self.LogFileHandle = open(self.sLogFileName, 'a')
                except:
                    print('pManager '+ __version__ +': Can\'t open Logfile!')
                    raise

        elif sOption == 'debuglevel':
            self.iDebugLevel = int(sValue)

        else:
            # unknown option!
            self.DebugStr('pManager '+ __version__ +': Warning: Trying to set unknown parameter "'+sOption+'".')


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

        # Focus does not come back from pProxy until iOwl is shut down
        self.intfProxy.Start()

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


    def GetVersion(self):
        """return version of iOwl"""
        return str(self.iOwlVersion)


    def GetOwnIP(self):
        """return own ip-number"""
        return self.sOwnIP


    def SetDebugLevel(self, iLevel):
        """Set Debug-level.

        iLevel -- Type of Debug: 0 -> Console only
                                 1 -> Logfile only
                                 2 -> Both

        """

        # set level
        self.iDebugLevel = iLevel

        # log change
        self.DebugStr('pManager '+ __version__ +': Changed Debug-level to ' + str(iLevel) + '.')


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

        return -- a 20-digit sequence of numbers

        """

        number = ''
        for i in range(20):
            number = number + str(whrandom.randint(0,9))

        return number


    def SetOwnIP(self, ownIP):
        """Set Own IP"""
        self.DebugStr('pManager '+ __version__ +': Setting own IP to ' + str(ownIP)+ '.')
        self.sOwnIP = ownIP


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

