__version__ = "$Revision: 1.21 $"

"""
$Log: cProxyHandler.py,v $
Revision 1.21  2001/08/10 18:37:38  i10614
added debuglevel to all messages.

Revision 1.20  2001/08/07 18:47:54  i10614
some changes

Revision 1.19  2001/07/19 19:46:52  i10614
removed warning at initial setting of options

Revision 1.18  2001/05/30 20:31:32  i10614
shortened debug output

Revision 1.17  2001/05/26 14:01:34  i10614
changed default params

Revision 1.16  2001/05/26 11:48:31  i10614
changed "No Title" to "Unknown Title".

Revision 1.15  2001/05/26 11:47:11  i10614
changed chunksize to 1024Byte -> needed for title extraction.

Revision 1.14  2001/05/26 11:42:12  i10614
removed page title from debug output

Revision 1.13  2001/05/25 19:16:53  i10614
removed debug output. CHanged Chunksize to 512byte.

Revision 1.12  2001/05/25 18:47:31  i10614
bugfix for downloading in chunks

Revision 1.11  2001/04/22 17:53:27  i10614
removed debug output

Revision 1.10  2001/04/22 16:20:48  i10614
Implemented changes for Python 2.1. Dont run with older versions of python\!

Revision 1.9  2001/04/22 13:28:50  i10614
added http-headers to prevent caching of iOwl-pages

Revision 1.8  2001/04/16 13:05:38  i10614
added debug output for unicode error

Revision 1.7  2001/04/15 19:12:51  i10614
now filtering clicks depending on status. Only 2xx is accepted, 302, 404 etc is skipped.

Revision 1.6  2001/04/14 15:04:07  i10614
fix for title-umlauts, workaround for keep-alive connections

Revision 1.5  2001/04/09 12:24:23  i10614
changed buffersize for answering requests to 4096bytes

Revision 1.4  2001/03/28 15:40:02  i10614
finally got rid of (most) thread exceptions (socket.error) under win32

Revision 1.3  2001/03/26 17:57:54  i10614
removed url from debug output to prevent logging of passwords

Revision 1.1.1.1  2001/03/24 19:23:03  i10614
Initial import to stio1 from my cvs-tree

Revision 1.15  2001/03/18 22:28:19  mbauer
catching socket-errors

Revision 1.14  2001/03/17 15:00:39  mbauer
changed comments

Revision 1.13  2001/03/05 10:18:23  mpopp
spelling unknown

Revision 1.12  2001/02/22 21:32:39  mbauer
added title to debug-output

Revision 1.11  2001/02/22 14:49:25  mbauer
added binary data handling

Revision 1.10  2001/02/21 16:26:49  mbauer
added title-extraction for clickstream recording

Revision 1.8  2001/02/20 21:17:02  mbauer
changed response html status to 200 OK

Revision 1.7  2001/02/20 17:37:12  mbauer
added SetRecording() and GetStatus()

Revision 1.6  2001/02/19 19:31:20  a
minor changes

Revision 1.5  2001/02/19 16:44:56  mbauer
changed shutdown-handling. Now accepts Ctrl-c for a clean shutdown.

Revision 1.3  2001/02/19 16:07:58  mbauer
Activated AddCLick for pClickstream


"""

import SocketServer
import pManager
import time
import string
import socket
import urlparse
import cClick
import htmlentitydefs
import sys
import cgi

class cProxyHandler(SocketServer.StreamRequestHandler):
    """The handler hook-in for the proxyServer

    inherits from StreamRequestHandler
    implements:
        - handle()-function.
        - __init__()-function

    """

    def __init__(self, request, client_address, server):
        """this is just the standard __init__() from
        BaseRequestHandler only thing added is a except-clause
        to get rid of these annoying socket-errors that only occur
        under win32...

        """

        try:
            SocketServer.StreamRequestHandler.__init__(self, request, client_address, server)
        except socket.error:
            pass


    def handle(self):
        """Get called by cProxyCore for each request"""

        try:
            # Parse request
            host, port, request = self.ParseRequest()

            # Check if this is a command for iOwl
            if self.IsCommand(host):
                # pass request to pGuiInterface
                self.HandleCommand()
                # close socket
                pManager.manager.DebugStr('cProxyHandler '+ __version__ +': Closing Socket (iOwl-Command).', 4)
                self.connection.close()
                return

            # init title string
            self.ClickTitle = 'Unknown Title'

            # Build Timestamp for click
            self.ClickTimestamp = time.time()

            # Connect to host and get handles
            server, client = self.Connect(host, port)

            # Send request to server
            self.SendRequest(client, request)

            # Handle response
            try:
                self.HandleResponse(server)
            except IOError:
                self.connection.close()
                return

        except socket.error:
            # request could not be fulfilled, most probably because user pressed interrupted his browser
            # close socket
            pManager.manager.DebugStr('cProxyHandler '+ __version__ +': Closing Socket.', 4)
            self.connection.close()
            return


        # close socket
        pManager.manager.DebugStr('cProxyHandler '+ __version__ +': Closing Socket.', 4)
        self.connection.close()

        # finished request
        # Now pass click to pClickstreamINterface, if it is an explicit one

        # check if this is an explicit click
        bIsExplicit = self.IsExplicit()

        if bIsExplicit:
            # Add Click to Clickstream
            ClickstreamInterface = pManager.manager.GetClickstreamInterface()
            pManager.manager.DebugStr('cProxyHandler '+ __version__ +': Detected explicit click. Title: '+str(self.ClickTitle)+' Status: '+str(self.ClickStatus), 3)

            click = cClick.cClick()

            click.SetClick(urlparse.urlparse(self.ClickUrl), \
                           self.ClickContent, self.ClickStatus, \
                           self.ClickTimestamp, self.ClickTitle, \
                           urlparse.urlparse(self.ClickReferer))

            ClickstreamInterface.AddClick(click)


    def ParseRequest(self):
        """Parse incoming request"""

        # read first line - http_request
        request = self.rfile.readline()

        # Get method, url and protocol
        try:
            method, url, protocol = string.split(request)
        except:
            self.error(400, "Can't parse request")
        if not url:
            self.error(400, "Empty URL")
        if method not in ['GET', 'HEAD', 'POST']:
            self.error(501, "Unknown request method (%s)" % method)

        # store url for clickstream
        self.ClickUrl = url

        # split url into site and path
        scheme, hostport, path, params, query, fragment = urlparse.urlparse(url)

        if string.lower(scheme) != 'http':
            self.error(501, "Unknown request scheme (%s)" % scheme)

        # Look for authentication strings
        sAuth = ''
        if '@' in hostport:
            sAuth, hostport = string.split(hostport, '@')

        # find port number
        if ':' in hostport:
            host, port = string.split(hostport, ':')
            port = string.atoi(port)
        else:
            # default port
            host = hostport
            port = 80

        # get path
        path = urlparse.urlunparse(('', '', path, params, query, fragment))

        # read headers
        dHeaders = self.ParseHeaders(self.rfile)
        if method == 'POST' and not dHeaders.has_key('content-length'):
            self.error(400, "Missing Content-Length for POST method")
        iLength = int(dHeaders.get('content-length', 0))
        # read content if any
        content = self.rfile.read(iLength)

        # store referrer for ClickStream
        self.ClickReferer = ''
        if dHeaders.has_key('referer'):
            self.ClickReferer = dHeaders['referer']

        # remove some unwanted headers. XXX - Why??
        self.try_del(dHeaders, 'accept-encoding')
        self.try_del(dHeaders, 'proxy-connection')
        # XXX Cant handle keep-alive <-- FIXME!
        self.try_del(dHeaders, 'connection')

        # build new request
        try:
            request = '%s %s HTTP/1.0\r\n%s\r\n%s' % (method, path,
                                                  self.JoinHeaders(dHeaders),
                                                  content)
        except:
            print "Method: "+method
            print "Path: "+path
            print "Content: "+content
            print "Headers: "+self.JoinHeaders(dHeaders)


        # finished!
        return host, port, request


    def ParseHeaders(self, input):
        """Get header info from <input>

        input   -- something providing .readline() function. Usually a socket.

        return  -- dictionary containing all headers (header : value)

        """

        headers = {}
        name = ''
        while 1:
            line = input.readline()
            if line == '\r\n' or line == '\n':
                break
            if line[0] in ' \t':
                # continued header
                headers[name] = headers[name] + '\r\n ' + string.strip(line)
            else:
                i = string.find(line, ':')
                assert(i != -1)
                name = string.lower(line[:i])
                if headers.has_key(name):
                    # merge value
                    headers[name] = headers[name] + ', ' + string.strip(line)
                else:
                    headers[name] = string.strip(line[i+1:])
        return headers


    def JoinHeaders(self, dHeaders):
        """convert header-dictionary back to string that can be passed to server"""
        data = []
        for name, value in dHeaders.items():
            data.append('%s: %s\r\n' % (name, value))
        return string.join(data, '')


    def Connect(self, host, port):
        """Connect to target server

        returns -- read-object, write-object

        """
        if pManager.manager.GetProxyInterface().GetUseParent():
            # replace host with proxy
            # XXX DOES NOT WORK!
            host, port = pManager.manager.GetProxyInterface().GetParent()

        try:
            addr = socket.gethostbyname(host)
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((addr, port))
        except socket.error, err:
            self.error(200, 'Error connecting to "%s" (%s)' % (host, err))
        return server.makefile('rb'), server.makefile('wb')


    def SendRequest(self, server, request):
        """Send request to target server"""
        try:
            server.write(request)
            pManager.manager.DebugStr('cProxyHandler '+ __version__ +': Sending request: '+str(request), 5)
            server.flush()
        except socket.error, err:
            self.error(500, 'Error sending data to "%s" (%s)' % (host, err))


    def HandleResponse(self, server):
        """get response from server and pass it back to client"""
        # response header should be in first line!
        response = server.readline()

        # split response
        fields = string.split(response)
        version = fields[0]
        status = fields[1]
        comment = string.join(fields[2:])

        #store status for ClickStream
        self.ClickStatus = string.strip(status)

        dHeaders = self.ParseHeaders(server)

        # store content-type for Clickstream:
        self.ClickContent = ''
        if dHeaders.has_key('content-type'):
            self.ClickContent = dHeaders['content-type']
        else:
            # Assume text/plain
            self.ClickContent = 'text/plain'

        # pass response to client
        try:
            self.wfile.write('HTTP/1.0 %s %s\r\n' % (status, comment))
            self.wfile.write(self.JoinHeaders(dHeaders))
            self.wfile.write('\r\n')

            bChecked = 0
            iBufferSize = 1024
            iCount = 0;
            # transfer actual document by chunks of iBufferSize
            while 1:
                iCount+=1
                # pManager.manager.DebugStr('cProxyHandler '+ __version__ +': Getting Chunk '+str(iCount))
                data = server.read(iBufferSize)
                if bChecked==0:
                    # pManager.manager.DebugStr('cProxyHandler '+ __version__ +': Extracting Title!', 5)
                    # need to look inside first buffer to determine if there is a <title></title> tag.
                    self.ClickTitle = self.ExtractTitle(str(data[:]))
                    bChecked = 1
                if not data:
                    break
                self.wfile.write(data)

            self.wfile.flush()

        except:
            # cant write to socket. probably user hit the stop-button of browser
            # ignore error
            pass


    def ExtractTitle(self, data):
        """look if there's a title tag inside data

        data    -- data as read from server
        return  -- string containing title

        """

        # be sure to have a string
        sData = str(data)

        # get a lowercase copy of string
        sLowData = sData.lower()

        iStart = sLowData.find('<title>')
        iEnd = sLowData.find('</title>')

        sTitle = u''
        if (iStart >= 0) and (iEnd > iStart):
            # okay, we have a complete title-tag
            sTitle = sData[iStart+len('<title>'):iEnd]

            # remove leading / trailing whitespaces
            sTitle = string.strip(sTitle)

            # be sure to get rid of umlauts etc
            sTitle = self.FilterUmlauts(sTitle)

            if len(sTitle) > 55:
                # cut off too long title
                sTitle = sTitle[:55] + '...'

            # replace html entities
            # for ent in htmlentitydefs.entitydefs.keys():
            #     string.replace(sTitle, '&'+ent+';', htmlentitydefs.entitydefs[ent])

            return sTitle

        return 'Unknown Title'



    def FilterUmlauts(self, s):
        """a quick hack to get rid of umlauts..."""

        dict={'ä':'ae', 'ö':'oe', 'ü':'ue', 'ß':'ss'}
        for key in dict.keys():
            s = s.replace(key, dict[key])
        return s



    def error(self, code, body):
        """Answer Client with an error page

        XXX Really not very nice page...

        """
        import BaseHTTPServer
        response = BaseHTTPServer.BaseHTTPRequestHandler.responses[code][0]
        try:
            self.wfile.write("HTTP/1.0 %s %s\r\n" % (code, response))
            self.wfile.write("Server: iOwl.net ProxyServer\r\n")
            self.wfile.write("Content-type: text/html\r\n")
            self.wfile.write("\r\n")
            self.wfile.write('<html><head>\n<title>%d %s</title>\n</head>\n'
                    '<body>\n%s\n</body>\n</html>' % (code, response, body))
            self.wfile.flush()
            self.wfile.close()
            self.rfile.close()
        except IOError:
            # probably user aborted browser so we dont have a socket left to write to
            pass

        # Exit thread
        raise SystemExit


    def try_del(self, dict, key):
        """delete key from dict without raising somethin"""
        try:
            del dict[key]
        except KeyError:
            pass


    def IsExplicit(self):
        """True if we handle an explicit click

        Compare timestamp with last explicit click.
        If difference > clicktime --> explicit click

        """

        # first get status. am i recording clicks or am i just a transparent proxy?
        bRecording = pManager.manager.GetProxyInterface().GetStatus()
        if bRecording == 0:
            # do not record any clicks!
            return 0

        if self.ClickContent != 'text/html':
            # only type text/html is allowed!
            return 0

        # dont record invalid or temporary urls
        if self.ClickStatus.startswith('3') or self.ClickStatus.startswith('4') or self.ClickStatus.startswith('5'):
            pManager.manager.DebugStr('cProxyHandler '+ __version__ +': Skipping Click (Status: '+str(self.ClickStatus)+')', 4)
            return 0

        # Get cProxyInterface
        cProxyInterface = pManager.manager.GetProxyInterface()

        # Get time of last explicit click
        iLastClick = cProxyInterface.GetLastExplicit()

        if (self.ClickTimestamp - iLastClick) > cProxyInterface.GetClickTime():
            # this is a new explicit click
            cProxyInterface.SetLastExplicit(self.ClickTimestamp)
            return 1
        else:
            # implicit click
            return 0


    def IsCommand(self, host):
        """true if this request is a command for iOwl

        commands have a url of type http://my.iowl.net
        -> if host == iowl i received a command.

        """

        if str(host) == 'my.iowl.net':
            return 1

        return 0


    def HandleCommand(self):
        """Pass command to pGui and forward answer to client"""

        # Get pGuiInterface
        pGuiInterface = pManager.manager.GetGuiInterface()

        # Get Response from pGui
        htmlResponse, sContentType = pGuiInterface.AcceptCommand(self.ClickUrl)

        # write header
        self.wfile.write("HTTP/1.0 %s %s\r\n" % ('200', 'OK'))
        self.wfile.write("Server: iOwl.net ProxyServer\r\n")
        self.wfile.write("Cache-Control: no-cache\r\n")
        self.wfile.write("Expires: -1\r\n")
        self.wfile.write("Pragma: no-cache\r\n")
        self.wfile.write("Content-type: %s\r\n" % sContentType)
        self.wfile.write("\r\n")

        # write html from pGui
        self.wfile.write(htmlResponse)

        # flush buffer
        self.wfile.flush()


if __name__ == '__main__':
    Server = SocketServer.ThreadingTCPServer(('', 1234), cProxyHandler)
    # thread.start_new_thread(Server.serve_forever, ())
    Server.serve_forever()
