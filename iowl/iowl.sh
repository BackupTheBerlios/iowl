#!/bin/sh
# iOwl.net - iowl.sh: start|stop|restart|kill

# the executable
# PYTHON="python"

# debian needs this:
PYTHON="python2.2"

# arguments:
ARGUMENTS="pManagement/iowl.py"

# check if iOwl is already running
PIDLIST=$(/bin/pidof $PYTHON $ARGUMENTS)

# set Pythonpath so python can find all our modules and append original $PYTHONPATH.
PYTHONPATH=./pAssoRules:./pClickstream:./pGui:./pManagement:./pMisc:./pNetwork:./pProxy:./pRecommendation:./pStatistics:$PYTHONPATH
export PYTHONPATH

# var's for stop
BEFEHL="python2.2 pManagement/iowl.py"
PSAUSGABE=`ps U $UID | egrep "$BEFEHL" | head -1 | tail -1` 
PROG=`echo "$PSAUSGABE" | cut -c27-56`
IOWLPID=`echo "$PSAUSGABE" | cut -c-5`

# how start|stop|kill does work

iowl_start () {
	if [ ! -n "$PIDLIST" ]
	then
  	# no pids found. start iOwl.net
	# start iOwl
  	$PYTHON $ARGUMENTS &
  	
	else
	# iOwl already running
  	echo "iOwl.net already running!"
  	echo "(PIDs: "$PIDLIST")"
	
	fi
}

iowl_stop () {
   	case "$PROG" in

   	*"$BEFEHL"* )
		kill -2 $IOWLPID
		echo "iOwl.net processes stopped"
	;;

	* )		
		echo "No iOwl.net running" 
	;;

   esac
}  

iowl_kill () {
   case "$PROG" in

   	*"$BEFEHL"* )
		kill -9 $IOWLPID
		echo "iOwl.net processes killed"
	;;

	* )		
		echo "No iOwl.net running" 
	;;

   esac
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
	sleep 3
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