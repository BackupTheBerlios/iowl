__version__ = "$Revision: 1.1 $"

"""
$Log: cJavaScriptTimer.py,v $
Revision 1.1  2001/03/24 19:22:58  i10614
Initial revision

Revision 1.1  2001/02/21 14:50:12  mbauer
initial release



"""

class cJavaScriptTimer:
    """a utility class for pGui.

    Generate little javascripts for pGui

    """

    def GetTimer(self, iTimeSeconds, sUrl):
        """Generate an auto-refresh-script

        iTimeSeconds    -- time to wait till refresh
        sUrl            -- url to load after refresh

        return:
            sScript     -- complete script to be included in html-pages (<script>....</script>
            sFunction   -- name of function to call in <body onload="funtion()">
            sForm       -- form element containing countdown timer (<form>...</form>

        """
        sScript ="""
                    <script language="JavaScript">
                    <!-- Hide from older browsers
                        var x = %s
                        var y = 1
                        function startclock()
                        {
                            x = x-y
                            if (x==0)
                            {
                                document.location = "%s"
                            }
                            else
                            {
                                document.timerform.clock.value = x
                                timerID = setTimeout("startclock()", 1000)
                            }
                        }
                    // -->
                    </script>
                 """ % (str(iTimeSeconds), str(sUrl))


        sForm = '<form method="POST" name="timerform"><input type="text" size="4" name="clock"></form>'

        sFunction = 'startclock()'

        return sScript, sFunction, sForm



###################################################################
### TEST FUNCTION####################
if __name__ == '__main__':
    generator = cJavaScriptTimer()
    script, function, form = generator.GetTimer(20, 'http://www.heise.de')
    print str((script, function, form))
