#!/bin/sh
# iOwl.net - iowl.sh: start|stop|restart|kill

# the executable
# PYTHON="python"
PYTHON="python2.2"

# arguments:
ARGUMENTS="pManagement/iowl.py"

# var's - PIDLIST
#PIDLIST=`pidof $PYTHON $IOWL_DIR/$ARGUMENTS`
PIDOF=`which pidof`

# set Pythonpath so python can find all our modules and append original $PYTHONPATH.
PYTHONPATH=$IOWL_DIR/pAssoRules:$IOWL_DIR/pClickstream:$IOWL_DIR/pGui:$IOWL_DIR/pManagement:$IOWL_DIR/pMisc:$IOWL_DIR/pNetwork:$IOWL_DIR/pProxy:$IOWL_DIR/pRecommendation:$IOWL_DIR/pStatistics:$PYTHONPATH
export PYTHONPATH

# how start|stop|kill does work

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
		$PYTHON $IOWL_DIR/$ARGUMENTS 2>&1 &
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

# iOwl.net start|stop|restart|kill
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
   *)
	echo "Usage: iowl.sh {start|stop|restart|kill}"
	exit 1
	;;
esac

# thats it
exit 0