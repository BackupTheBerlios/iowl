__version__ = "$Revision: 1.2 $"

"""
$Log: cBinaryDataGrabber.py,v $
Revision 1.2  2001/03/29 23:31:41  i10614
now takes care of path (data/pix/pixc.gif)

Revision 1.1.1.1  2001/03/24 19:22:59  i10614
Initial import to stio1 from my cvs-tree

Revision 1.2  2001/02/23 19:18:03  mbauer
fixed bug for binary file-reading under Windows

Revision 1.1  2001/02/22 14:46:58  mbauer
initial release

Revision 1.1  2001/02/21 14:50:13  mbauer
initial release



"""
import pManager
import urlparse
import os

class cBinaryDataGrabber:
    """Get results for a previously started recommendation request"""

    def __init__(self, cGuiRequestHandler):
        """Constructor"""
        self.cGuiRequestHandler = cGuiRequestHandler


    def GetData(self, sPath):
        """Return raw file

        sPath   -- path/to/file

        return  -- raw data from file, string containing content-type

        """

        # build absolute path
        sFullPath = pManager.manager.GetBaseDir() + sPath
        sFullPath = os.path.normcase(sFullPath)

        data = ''
        try:
            # open file -> look in current directory
            # open in binary mode!
            # file = open(lPath[len(lPath)-1], 'rb')
            file = open(sFullPath, 'rb')
            # read data
            data = file.read()
            file.close()
        except:
            # pManager.manager.DebugStr('cBinaryDataGrabber '+ __version__ +': Could not find "'+str(lPath[len(lPath)-1])+'"')
            pManager.manager.DebugStr('cBinaryDataGrabber '+ __version__ +': Could not find "'+sFullPath+'"')

        if sPath.endswith('.gif'):
            return data, 'image/gif'
        if sPath.endswith('.html'):
            return data, 'text/html'

