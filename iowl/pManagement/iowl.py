#!/usr/local/bin/python

__version__ = "$Revision: 1.16 $"

"""
$Log: iowl.py,v $
Revision 1.16  2002/02/27 14:10:52  Saruman
Dump message to stderr for "adress already in use" - error.

Revision 1.15  2002/02/27 13:45:37  Saruman
catch SystemExit exception for clean shutdown.

Revision 1.14  2002/02/25 16:46:43  Saruman
modified exit code(s).

Revision 1.13  2002/02/19 17:21:28  Saruman
installed handler for SIGUSR1 on unix-systems.
iOwl should now be able to be shut down with a kill -SIGUSR1.

Revision 1.12  2001/07/15 10:17:32  i10614
added doubleclick -> show iowl.net to trayicon

Revision 1.11  2001/05/26 11:39:10  i10614
changed win32-traymenu

Revision 1.10  2001/05/25 19:28:48  i10614
bugfix for menu

Revision 1.7  2001/05/24 19:26:49  i10614
Changed icon filename. Removed "stop iowl" from systray menu.

Revision 1.6  2001/05/20 16:16:10  i10614
small changes for .exe-building

Revision 1.5  2001/04/22 17:51:45  i10614
added win32 trayicon support

Revision 1.4  2001/04/22 16:20:47  i10614
Implemented changes for Python 2.1. Dont run with older versions of python\!

Revision 1.3  2001/04/22 13:26:10  i10614
modified starting to enable codefork depending on platform

Revision 1.2  2001/04/16 13:06:21  i10614
experimental GUI added

Revision 1.1.1.1  2001/03/24 19:22:36  i10614
Initial import to stio1 from my cvs-tree

Revision 1.11  2001/03/18 23:02:03  mbauer
added missing import socket

Revision 1.10  2001/03/18 22:24:23  mbauer
restored changelog

Revision 1.9  2001/03/18 17:35:48  mbauer
minor changes

Revision 1.8  2001/03/18 17:00:48  mbauer
Now catching all exceptions raised inside mainthread, stacktrace is
dumped to logfile and shutdown called.

Revision 1.7  2001/02/20 21:40:16  a
minor changes

Revision 1.6  2001/02/20 21:16:08  a
added default configfile path

Revision 1.5  2001/02/19 16:44:55  mbauer
changed shutdown-handling. Now accepts Ctrl-c for a clean shutdown.

Revision 1.4  2001/02/14 21:42:30  mbauer
iowl.py is now executable

Revision 1.3  2001/02/14 16:57:00  mbauer
Changed creation of pManager. Now anyone can access pManager through the
module attribute "manager".
Example:

	import pManager

	class foo:
		def output(self, text):
			pManager.manager.DebugStr(text)


This is some kind of pseudo-global variable :-)

Revision 1.2  2001/02/14 09:49:43  mbauer
minor fixes

Revision 1.1  2001/02/13 21:49:40  mbauer
Initial creation


"""



import getopt
import sys
import os
import pManager
import traceback
import socket
import thread

# os-specific stuff
if sys.platform[:3] == 'win':
    from win32api import *
    from win32gui import *
    import win32con
    import sys, os

    class TrayIcon:
        def __init__(self):
            message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_COMMAND: self.OnCommand,
                win32con.WM_USER+20 : self.OnTaskbarNotify,
                win32con.WM_QUERYENDSESSION: self.OnQueryEndSession,
            }
            # Register the Window class.
            wc = WNDCLASS()
            hinst = wc.hInstance = GetModuleHandle(None)
            wc.lpszClassName = "iOwl"
            wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
            wc.hCursor = LoadCursor( 0, win32con.IDC_ARROW )
            wc.hbrBackground = win32con.COLOR_WINDOW
            wc.lpfnWndProc = message_map # could also specify a wndproc.
            classAtom = RegisterClass(wc)
            # Create the Window.
            style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
            self.hwnd = CreateWindow( classAtom, "iOwl.net", style, \
                        0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                        0, 0, hinst, None)
            UpdateWindow(self.hwnd)

            # set icons
            iconPathName = "data/iowl.ico"
            if os.path.isfile(iconPathName):
                icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                self.hicon_act = LoadImage(hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
            else:
                # Can't find a Python icon file - using default
                self.hicon_act = LoadIcon(0, win32con.IDI_APPLICATION)

            iconPathName = "data/iowl_in.ico"
            if os.path.isfile(iconPathName):
                icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                self.hicon_inact = LoadImage(hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
            else:
                # Can't find a Python icon file - using default
                self.hicon_inact = LoadIcon(0, win32con.IDI_APPLICATION)

            flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
            nid = (self.hwnd, 0, flags, win32con.WM_USER+20, self.hicon_act, "iOwl.net")
            Shell_NotifyIcon(NIM_ADD, nid)

        def OnDestroy(self, hwnd, msg, wparam, lparam):
            nid = (self.hwnd, 0)
            Shell_NotifyIcon(NIM_DELETE, nid)
            # shutdown...
            StopiOwl()
            PostQuitMessage(0) # Terminate the app.

        def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
            if lparam==win32con.WM_LBUTTONUP:
                pass

            elif lparam==win32con.WM_LBUTTONDBLCLK:
                # Open Browser pointing to "http://my.iowl.net"
                ShellExecute(0, "open", "http://my.iowl.net", None, None, win32con.SW_SHOWNORMAL);

            elif lparam==win32con.WM_RBUTTONUP:
                menu = CreatePopupMenu()
                if (pManager.manager.bIsRunning == 0):
                    # we are not yet running. Display all options.
                    AppendMenu( menu, win32con.MF_STRING, 1023, "Activate")
                    AppendMenu( menu, win32con.MF_STRING, 1024, "De-Activate")
                    AppendMenu( menu, win32con.MF_STRING, 1025, "Show iOwl.net")
                    AppendMenu( menu, win32con.MF_STRING, 1027, "Hide menu")
                    AppendMenu( menu, win32con.MF_SEPARATOR, 1027, "bar")
                    AppendMenu( menu, win32con.MF_STRING, 1026, "Exit iOwl.net")
                else:
                    # we are running. Check state of iOwl.net and display according menu-options.
                    if pManager.manager.GetProxyInterface().GetStatus()==0:
                        # not recording
                        AppendMenu( menu, win32con.MF_STRING, 1023, "Activate")
                    else:
                        # recording
                        AppendMenu( menu, win32con.MF_STRING, 1024, "De-Activate")

                    AppendMenu( menu, win32con.MF_STRING, 1025, "Show iOwl.net")
                    AppendMenu( menu, win32con.MF_STRING, 1027, "Hide menu")
                    AppendMenu( menu, win32con.MF_SEPARATOR, 1027, "bar")
                    AppendMenu( menu, win32con.MF_STRING, 1026, "Exit iOwl.net")

                pos = GetCursorPos()
                TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)

            return 1

        def OnCommand(self, hwnd, msg, wparam, lparam):
            id = LOWORD(wparam)
            if id == 1023:
                # activate
                pManager.manager.GetProxyInterface().SetParam('recording','1')
                # Update trayicon to active
                self.SetIcon(1)
            elif id == 1024:
                # inactivate
                pManager.manager.GetProxyInterface().SetParam('recording','0')
                # Update trayicon to inactive
                self.SetIcon(0)
            elif id == 1025:
                # Open Browser pointing to "http://my.iowl.net"
                ShellExecute(0, "open", "http://my.iowl.net", None, None, win32con.SW_SHOWNORMAL);
            elif id == 1026:
                # Close iOwl.net
                # remove icon
                nid = (self.hwnd, 0)
                Shell_NotifyIcon(NIM_DELETE, nid)
                # stop iOwl
                StopiOwl()
            elif id == 1027:
                # do nothing, just a workaround for broken popup-menu
                pass

        def OnQueryEndSession(self, hwnd, msg, wparam, lparam):
            # Shutdown iOwl
            StopiOwl()
            return 1

        def SetIcon(self, bState):
            """ Set trayicon

            XXX Just modifying the icon should do the job. Ne need for completely deleting the icon from the taskbar.

            """

            # remove old icon
            nid = (self.hwnd, 0)
            Shell_NotifyIcon(NIM_DELETE, nid)
            if bState==0:
                # inactive
                flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
                nid = (self.hwnd, 0, flags, win32con.WM_USER+20, self.hicon_inact, "iOwl.net")
                Shell_NotifyIcon(NIM_ADD, nid)
            else:
                # active
                flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
                nid = (self.hwnd, 0, flags, win32con.WM_USER+20, self.hicon_act, "iOwl.net")
                Shell_NotifyIcon(NIM_ADD, nid)


def usage():
    print("Usage: python iowl.py -c configfile")


def winstart():
    """Start iOwl on win32

    Create a trayicon with basic iOwl commands
    """

    # create trayicon
    tray = TrayIcon()

    # start iOwl in new thread
    thread.start_new(StartiOwl, (tray,))

    # message loop
    PumpMessages()


def StopiOwl():
    """Shutdown iOwl."""
    pManager.manager.ShutDown()


def unixstart():
    """Start iOwl on unix platform"""
    StartiOwl(None)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "configfile="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(1)

    configfile = "iowl.cfg"
    output = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-c", "--configfile"):
            configfile = a

    # create pManager as attribute of Module pManager
    # Really strange, but works and enables everyone access to pManager through importing
    # modul pManager
    pManager.manager = pManager.cManager(configfile)

    # start, depending on os
    if sys.platform[:3] == 'win':
        # windows...
        winstart()
    else:
        # start console-based
        unixstart()


def signal_SIGUSR1(signo, frame):
    """signal handler for SIGUSR1

    initiate shutdown if SIGUSR1 is caught.
    """
    pManager.manager.DebugStr('pManager '+ __version__ +': Received signal SIGUSR1. Starting shutdown.')
    pManager.manager.ShutDown()
    sys.exit(0)


def StartiOwl(tray):
    if tray!=None:
        # pManager needs the trayicon to update it...
        pManager.manager.SetTray(tray)

    # install signal handler on non-win32 systems
    if sys.platform[:3] != 'win':
        import signal
        signal.signal(signal.SIGUSR1, signal_SIGUSR1)


    # start iOwl.net
    try:
        pManager.manager.StartOwl()
    except SystemExit:
        # caused by normal shutdown through SIGUSR1
        pass
    except KeyboardInterrupt:
        # Ctrl-C or SIGINT -> shutdown owl
        pManager.manager.DebugStr('pManager '+ __version__ +': Received Keyboard-interrupt. Starting shutdown.')
        pManager.manager.ShutDown()
        sys.exit(0)
    except socket.error:
        # socket error while trying to start proxy -> Adress in use
        # get exception
        eType, eValue, eTraceback = sys.exc_info()
        pManager.manager.DebugStr('pManager '+ __version__ +': Exception: Type: '+str(eType)+', value: '+str(eValue))
        pManager.manager.DebugStr('pManager '+ __version__ +': Now shutting down.')
        pManager.manager.ShutDown()
        # print info to stderr
        sys.stderr.write(os.linesep + os.linesep + "ERROR: Could not start iOwl - Adress already in use!" + os.linesep)
        sys.exit(2)
    except:
        # unknown error. log and try to shutdown

        # get exception
        eType, eValue, eTraceback = sys.exc_info()

        # build stacktrace string
        tb = ''
        for line in traceback.format_tb(eTraceback, 15):
            tb = tb + line

        pManager.manager.DebugStr('pManager '+ __version__ +': Unhandled error: Type: '+str(eType)+', value: '+str(eValue))
        pManager.manager.DebugStr('pManager '+ __version__ +': Traceback:\n'+str(tb))
        pManager.manager.DebugStr('pManager '+ __version__ +': Now shutting down.')
        pManager.manager.ShutDown()
        sys.exit(1)




####################################################
## Main ############################################

if __name__ == "__main__":

    main()

    # test()




####################################################
## TEST FUNCTIONS ##################################
def test():
    m = GetManager()
    print m
    print foo
    # m.StartOwl()

