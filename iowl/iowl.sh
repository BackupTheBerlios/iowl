#!/bin/sh
# iOwl.net - iowl.sh: start|stop|restart|status|kill

##vars: $PYTHON -> should python2.2 but works also with python
##	$PIDOF -> path to pidof normally /bin or /sbin (autodetected)
##	$IOWL_DIR -> maybe $HOME/iowl/ or something
##
##	 the path to python, pidof and iowl-dir normally autodetected; 
##	 if it doesn't run check out the path for yourself and set below.
##
## 	$ARGUMENTS -> path to iowl.py in $IOWL_DIR
##	$PYTHONPATH -> path to the modules of iOwl.net depend on $IOWL_DIR 
##			+ original $PYTHONPATH
##			is set below in line 94 normally is this right
###############################################################################

# PYTHON=your_path_to_python # absolute path to python2.2 or python set if not autodetect

# PIDOF=path_to_your_pidof # set if not autodetect

# IOWL_DIR=your_path_to_iowl # set if $IOWL_DIR is not set

ARGUMENTS="pManagement/iowl.py"

###############################################################################
# autodetect PIDOF, PYTHON, IOWL_DIR, PYTHONPATH
###############################################################################

# autodetect pidof executable
if [ -z $PIDOF ]; then

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

	if [ -z $PIDOF ]; then
		echo "There is no pidof executable found on default path. Edit iowl.sh and change PIDOF variable at line 21."
		exit 1
	fi
fi

# autodetect python executable
if [ -z $PYTHON ]; then

	if [ -x /usr/bin/python ]; then
	PYTHON=/usr/bin/python;
	fi

	if [ -x /usr/bin/python2.2 ]; then 
	PYTHON=/usr/bin/python2.2;
	fi

	if [ -x /usr/local/bin/python ]; then 
	PYTHON=/usr/local/bin/python;
	fi

	if [ -x /usr/local/bin/python2.2 ]; then
	PYTHON=/usr/local/bin/python2.2;
	fi
		
	if [ -z $PYTHON ]; then
		echo "There is no python2.2 or python executable found on default path. Edit iowl.sh and change PYTHON variable at line 17."
		exit 1
	else
		export PYTHON
	fi
fi

# autodetect locataion of iowl source
if [ -d "$IOWL_DIR" ]; then
	# If $IOWL_DIR is not set in global profile, bashrc or users 
	# own profile, bashrc -> set to working directory
	export IOWL_DIR

else
	# otherwise export local directory
	IOWL_DIR=`pwd`
	export IOWL_DIR	
fi

# $PYTHONPATH environment 
PYTHONPATH=$IOWL_DIR/pAssoRules:$IOWL_DIR/pClickstream:$IOWL_DIR/pGui:$IOWL_DIR/pManagement:$IOWL_DIR/pMisc:$IOWL_DIR/pNetwork:$IOWL_DIR/pProxy:$IOWL_DIR/pRecommendation:$IOWL_DIR/pStatistics:$PYTHONPATH

###############################################################################
# some tests
###############################################################################

# a little test if $IOWL_DIR is true

if [ ! -f $IOWL_DIR/$ARGUMENTS ]; then 
echo ./$ARGUMENTS "does not exist!"
echo "Your are not in the right directory to start iOwl.net"
exit 1;
fi

###############################################################################
# detect network status
###############################################################################

network () {
	proxy=`netstat -n | grep -e tcp | sed -n -e '/\<3228/ p'`
	iowl=`netstat -n | grep -e tcp | sed -n -e '/\<2323/ p'`
	# are there open ports?
	if [ -n "$proxy"  ]; then
			echo "There are open ports for iOwl.net-Proxy! Wait a short time and start again."
			exit 1;
	fi
	
	if [ -n "$iowl" ]; then
			echo "There are open ports for iOwl.net-Recommendation! Wait a short time and start again."
			exit 1;
	fi
}

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
        	echo "iOwl.net already running!"
		echo "(PID's: "$PIDLIST")";

		else
			network
		
			export PYTHONPATH
			$PYTHON $IOWL_DIR/$ARGUMENTS &
	fi
}

iowl_stop () {
	# is it running?
	PIDLIST=`$PIDOF $PYTHON $IOWL_DIR/$ARGUMENTS`
	# if runs stop it; else do nothing
   	if [ -n "$PIDLIST" ];
        	then 
        	# iOwl.net is already running
        	# echo "iOwl.net is already running!  (PID's: "$PIDLIST")"
        	kill -SIGUSR1 $PIDLIST
		# wait till iOwl stopped
        	# wait "$PIDLIST"
		echo "iOwl.net processes stopped!"
		sleep 1
		# check network status
		network

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
        	echo "iOwl.net is already running!"
		echo " (PID's: "$PIDLIST")";

		else
		# iOwl.net is not running
		echo "iOwl.net is not running!"
		# check network status
		network
	fi
}

iowl_kill () {
	# is it running?
	PIDLIST=`$PIDOF $PYTHON $IOWL_DIR/$ARGUMENTS`
	# if runs kill it; if not do nothing
	if [ -n "$PIDLIST" ];
        	then 
        	# iOwl.net is already running
        	# echo "iOwl.net is already running!  (PID's: "$PIDLIST")"
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
	sleep 2
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
