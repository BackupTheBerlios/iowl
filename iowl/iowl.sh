#!/bin/sh
# iOwl.net - iowl.sh: start|stop|restart|status|kill

# !! Important look for the Variable IOWL_DIR and change it !!

##vars: $PYTHON -> should python2.2 but works also with python
## 	$ARGUMENTS -> path to iowl.py in $IOWL_DIR
##	$PIDOF -> path to pidof normally /bin or /sbin (autodetected)
##
##	 the path to pidof normally autodetected; if it doesn't run   
##	 check out the path for yourself and uncomment the first PIDOF
##	 with a # and use your own
##
##	$IOWL_DIR -> maybe $HOME/iowl/ or something
##	$PYTHONPATH -> path to the modules of iOwl.net + original $PYTHONPATH
###############################################################################

# PYTHON="python"
PYTHON="python2.2"

ARGUMENTS="pManagement/iowl.py"

# PIDOF=path_to_your_pidof

IOWL_DIR=`pwd`

# a little test if $IOWL_DIR is true

if [ ! -d $IOWL_DIR ]; 
then echo $IOWL_DIR "does not exist .. please change iowl.sh"
exit 1;
fi

PYTHONPATH=$IOWL_DIR/pAssoRules:$IOWL_DIR/pClickstream:$IOWL_DIR/pGui:$IOWL_DIR/pManagement:$IOWL_DIR/pMisc:$IOWL_DIR/pNetwork:$IOWL_DIR/pProxy:$IOWL_DIR/pRecommendation:$IOWL_DIR/pStatistics:$PYTHONPATH

###############################################################################
# special for pidof on non Debian Systems
###############################################################################

if [ -x /bin/pidof ]; then
PIDOF=/bin/pidof;
fi

if [ -x /sbin/pidof ]; then 
PIDOF=/sbin/pidof;
fi

if [ -x /usr/bin/pidof ]; then 
PIDOF=/usr/bin/pidof;
fi

if [ -x /usr/sbin/pidof ]; then
PIDOF=/usr/sbin/pidof;
fi


###############################################################################
# how start|stop|status|kill does work
###############################################################################

iowl_start () {
	# is it running?
	PIDLIST=`$PIDOF $PYTHON $IOWL_DIR/$ARGUMENTS`
	# if runs do nothing; else start it
	if [ -n "$PIDLIST" ];
        	then
        	# iOwl.net already running
        	echo "iOwl.net already running!  (PID's: "$PIDLIST")";

		else
		# iOwl.net isnt running
		export PYTHONPATH
		$PYTHON $IOWL_DIR/$ARGUMENTS &
		# TODO: Check return value from iOwl;
	fi
}

iowl_stop () {
	# is it running?
	PIDLIST=`$PIDOF $PYTHON $IOWL_DIR/$ARGUMENTS`
	# if runs stop it; else do nothing
   	if [ -n "$PIDLIST" ];
        	then 
        	# iOwl.net is already running
        	echo "iOwl.net is already running!  (PID's: "$PIDLIST")"
        	kill -2 $PIDLIST
        	echo "iOwl.net processes stopped!";

		else
		# iOwl.net is not running
		echo "iOwl.net is not running!";
	fi
}  

iowl_status () {
	# is it running?
	PIDLIST=`$PIDOF $PYTHON $IOWL_DIR/$ARGUMENTS`
	# if runs print PIDLIST; if not print "is not running"
	if [ -n "$PIDLIST" ];
        	then 
        	# iOwl.net is already running
        	echo "iOwl.net is already running!  (PID's: "$PIDLIST")";

		else
		# iOwl.net is not running
		echo "iOwl.net is not running!";
	fi
}

iowl_kill () {
	# is it running?
	PIDLIST=`$PIDOF $PYTHON $IOWL_DIR/$ARGUMENTS`
	# if runs kill it; if not do nothing
	if [ -n "$PIDLIST" ];
        	then 
        	# iOwl.net is already running
        	echo "iOwl.net is already running!  (PID's: "$PIDLIST")"
        	kill -9 $PIDLIST
        	echo "iOwl.net processes killed!";

		else
		# iOwl.net is not running
		echo "iOwl.net is not running!";
	fi
}

###############################################################################
# iOwl.net start|stop|restart|kill|status
###############################################################################
case "$1" in

   start)
	iowl_start
	;;
   stop)
	iowl_stop	
	;;
   restart)
	iowl_stop	
	sleep 5
	iowl_start	
	;;
   kill)
	iowl_kill
	;;
   status)
	iowl_status
	;;
   *)
	echo "Usage: iowl.sh {start|stop|restart|status|kill}"
	exit 1
	;;
esac

# thats it
exit 0