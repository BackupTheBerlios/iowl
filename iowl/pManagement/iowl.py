#!/usr/local/bin/python

__version__ = "$Revision: 1.2 $"

"""
$Log: iowl.py,v $
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
import pManager
import traceback
import socket
import Tkinter
import thread

def usage():
    print("Usage: python iowl.py -c configfile")


def DisplayGui():
    root = Tkinter.Tk()
    root.title("iOwl.net")
    root.protocol('WM_DELETE_WINDOW', StopiOwl)
    # frame = Tkinter.Frame()
    # frame.pack()
    Tkinter.Label(root, text="Intelligent Owl Network").pack(side=Tkinter.TOP)
    Tkinter.Button(root, text="start iOwl", command=Start).pack(side=Tkinter.LEFT)
    Tkinter.Button(root, text="stop iOwl", command=StopiOwl).pack(side=Tkinter.RIGHT)
    root.mainloop()


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "configfile="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

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

    # start gui
    DisplayGui()
    # StartiOwl()

def Start():
    thread.start_new(StartiOwl, ())

def StartiOwl():
    # start iOwl.net
    try:
        pManager.manager.StartOwl()
    except KeyboardInterrupt:
        # shutdown owl
        pManager.manager.DebugStr('pManager '+ __version__ +': Received Keyboard-interrupt. Starting shutdown.')
        pManager.manager.ShutDown()
    except socket.error:
        # socket error while trying to start proxy -> Adress in use
        # get exception
        eType, eValue, eTraceback = sys.exc_info()
        pManager.manager.DebugStr('pManager '+ __version__ +': Exception: Type: '+str(eType)+', value: '+str(eValue))
        pManager.manager.DebugStr('pManager '+ __version__ +': Now shutting down.')
        pManager.manager.ShutDown()
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

def StopiOwl():
    pManager.manager.ShutDown()



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

