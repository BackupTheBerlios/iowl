
__version__ = "$Revision: 1.1 $"

"""
$Log: timer.py,v $
Revision 1.1  2001/03/24 19:22:37  i10614
Initial revision

Revision 1.5  2001/03/18 22:23:59  mbauer
added try-except to timer-function

Revision 1.4  2001/02/14 21:03:41  mbauer
bugfixes

Revision 1.2  2001/02/14 12:26:59  mbauer
removed previously forced function parameter 'interval'. WatchDog-Function must have zero parameters now.

Revision 1.1  2001/02/13 22:33:38  mbauer
Initial checkin


"""
import time
import thread

class sleeper:
    """Representation of sleeping/waiting task"""
    def __init__(self, function, interval, id):
        self.originterval = interval
        self.interval = interval
        self.function = function
        self.keepRunning = 1;
        self.id = id

    def sleep(self):
        while self.keepRunning == 1:
            # wait
            time.sleep(self.interval)

            # wake up
            if self.keepRunning:
                # need offset since time.sleep() is not very exact :-(
                offset = 0.5
                runningtime = time.time() - self.starttime
                if runningtime >= self.interval - offset:
                    # call function
                    try:
                        self.function()
                    except:
                        # function failed! Log and continue
                        # get exception
                        eType, eValue, eTraceback = sys.exc_info()

                        # build stacktrace string
                        tb = ''
                        for line in traceback.format_tb(eTraceback, 15):
                            tb = tb + line

                        pManager.manager.DebugStr('pManager '+ __version__ +': Unhandled error in timer-called function: Type: '+str(eType)+', value: '+str(eValue))
                        pManager.manager.DebugStr('pManager '+ __version__ +': Traceback:\n'+str(tb))
                        pManager.manager.DebugStr('pManager '+ __version__ +': Trying to continue...')

                    # reset interval
                    self.interval = self.originterval
                    # reset starttime
                    self.starttime = time.time()
                else:
                    # there was a reset somewhere.
                    # sleep on for remaining interval
                    self.interval = self.originterval - (time.time() - self.starttime)


    def stop(self):
        """stop thread"""
        self.keepRunning = 0


    def run(self):
        """Start thread"""
        self.starttime = time.time()
        thread.start_new_thread(self.sleep,())

    def reset(self):
        """Reset thread"""
        self.starttime = time.time()


class timer:
    """Timer to schedule actions

    register with function and intervall and timer
    calls registered function after interval has expired.

    """

    def __init__(self):
        """Constructor"""
        # initialize sleeper list
        self.Sleepers = []
        self.nextid = 0


    def register(self, function, interval):
        """Create new sleeper and start it"""

        # create
        s = sleeper(function, interval, len(self.Sleepers))

        # add to list
        self.Sleepers.append(s)

        # start
        s.run()

        # return id
        return s.id


    def reset(self, id):
        """reset timer of sleeper <id>"""
        self.Sleepers[id].reset()


    def stop(self, id):
        """delete sleeper <id>"""
        self.Sleepers[id].stop()
        # del self.Sleepers[id]









#########################################################
### TEST FUNCTIONS ######################################

def prnt():
    print('WakeUp!')

def prnt2():
    print('lemme sleep...')

def test1():
    t = timer()

    s1 = t.register(prnt,5)
    s2 = t.register(prnt2,1)

    time.sleep(10)

    print 'stopping s1'
    t.stop(s1)
    # print 'trying to reset s2'
    # t.reset(s2)
    print 'resetting s2'
    t.reset(s2)
    time.sleep(4)
    print 'resetting s2'
    t.reset(s2)

    time.sleep(20)


if __name__ == '__main__':
    test1()





