#!/bin/sh
# iOwl.net - iowl.sh: start|stop|restart|kill

# the executable
# PYTHON="python"
PYTHON="python2.2"

# arguments:
ARGUMENTS="pManagement/iowl.py"

# var's for start - stop
IOWLPS=`ps U $UID | egrep "$PYTHON $IOWL_DIR/$ARGUMENTS" | head -1 | tail -1` 
PROG=`echo "$IOWLPS" | cut -c27-90`
IOWLPID=`echo "$IOWLPS" | cut -c-5`

# set Pythonpath so python can find all our modules and append original $PYTHONPATH.
PYTHONPATH=./pAssoRules:./pClickstream:./pGui:./pManagement:./pMisc:./pNetwork:./pProxy:./pRecommendation:./pStatistics:$PYTHONPATH
export PYTHONPATH

# how start|stop|kill does work

iowl_start () {
	case "$PROG" in

		*"$PYTHON $IOWL_DIR/$ARGUMENTS" )
			echo "iOwl.net already running!"
		;;

		* )
			$PYTHON $IOWL_DIR/$ARGUMENTS &
		;;
	
	esac
}

iowl_stop () {
   	case "$PROG" in

   		*"$PYTHON $IOWL_DIR/$ARGUMENTS" )
			kill -2 $IOWLPID
			echo "iOwl.net processes stopped!"
		;;

		* )		
			echo "iOwl.net is not running!" 
		;;

   	esac
}  

iowl_kill () {
	case "$PROG" in

   		*"$PYTHON $IOWL_DIR/$ARGUMENTS" )
			kill -9 $IOWLPID
			echo "iOwl.net processes killed!"
		;;

		* )		
			echo "iOwl.net is not running!" 
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