#!/bin/bash

# Get the absolute path of a file or directory.
function abspath() {
    if [ $# = 1 ] ; then
	opwd=$OLDPWD
	dname=`dirname $1`
	if [ -d $dname ] ; then 
	    cd $dname
	    echo `pwd`/`basename $1`
	    cd $OLDPWD
	    if [ -d $opwd ] ; then
		cd $opwd
		cd $OLDPWD
	    fi
	else
	    echo "abspath $1: Directory \"$dname\" doesn't exist!"
	fi
	unset opwd dname
    else
	for fname in $@ ; do
	    abspath $fname
	done
    fi
}

# Make a directory and cd to it.
function mkdircd() {
    if [ ! -e $1 ] ; then
	mkdir -p $1 && cd $1
    elif [ ! -d $1 ] ; then
	echo "mkdircd: $1 exists and isn't a directory!"
    else
	cd $1
    fi
}

function rename() {
    for f in ${@:3} ; do
	local dest=`echo $f | sed "s/$1/$2/"`
	mv "$f" "${f/$1/$2}"
    done
}
