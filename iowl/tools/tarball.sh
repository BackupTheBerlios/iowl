#!/bin/sh
#
#  nightly
#
#  This shell script is designed to take a snapshot of this
#  sourceforge project's current CVS state, making a "nightly
#  tarball" of the sources, which can be downloaded from
#  the project's sourceforge web site.

mkdir tmp_iowl
cd tmp_iowl
# get the project name from pwd
pwd=`pwd`
projname=iowl #`basename $pwd`

# set cvs variables for anonymous checkout
export CVS_RSH=ssh
export CVSROOT=:pserver:anonymous@cvs.$projname.berlios.de:/cvsroot/$projname 
export CVS_PASSFILE=./temp-cvs-passfile

# fake out cvs login, so we don't have to use expect to
# drive the login/password prompt.  (sf.net doesn't have expect)
echo $CVSROOT A > $CVS_PASSFILE
#cvs login
cvs -z3 co $projname
rm $CVS_PASSFILE

# delete old tarball
#rm -f htdocs/nightly/*

# change build date in pManager.py
../Python-2.1/python ../update_version.py

# insert iowl.cfg with kingfisher as entryowl
cp ~/iowl.cfg iowl

# create new tarball
date=`date +%Y%m%d`
tar cfz /home/groups/iowl/htdocs/nightly/$projname-$date.tar.gz --exclude=CVS --exclude=CVSROOT $projname

rm /home/groups/iowl/htdocs/nightly/current-iowl.tar.gz
ln -s /home/groups/iowl/htdocs/nightly/$projname-$date.tar.gz /home/groups/iowl/htdocs/nightly/current-iowl.tar.gz 

# delete temporary iowl dir
cd ..
rm -r tmp_iowl
