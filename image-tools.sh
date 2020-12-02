#!/bin/bash

function img-creation-date() {
    # Get the creation date of an image. Must have either identify or exiftool installed
    img=$1
    if [ ! -z "$(command -v identify)" ] ; then
	info="$(identify -verbose $img)"
    elif [ ! -z "$(command -v exiftool)" ] ; then
	info="$(exiftool $img)"
    else
	echo "Requires identify or exiftool!"
    fi
    info="$(echo ${info} | grep 'Create \?Date' | tail -n 1 | sed 's/T/ /')"
    if [ -z "$info" ] ; then
	echo "Couldn't get creation date for $img"
	return 1
    fi
    cdate="$(echo ${info} | awk '{print $(NF-1), $NF}' | sed 's/-/:/g')"
    echo "$cdate"
}

function img-rename-to-cdate() {
    fname=$1
    cdate="$(img-creation-date $fname)"
    if [ $? != 0 ] ; then
	echo "$cdate"
	return 1
    fi
    suffix="$(echo $fname | sed 's/\./ /g' | awk '{print $NF}')"
    datename="$(echo $cdate | sed 's/://g' | sed 's/ /_/')"
    newname="${datename}.${suffix}"
    if [ -e "$newname" ] ; then
	i=1
	newname="${datename}_${i}.${suffix}"
	while [ -e "$newname" ] ; do
	    let i+=1
	    newname="${datename}_${i}.${suffix}"
	done
    fi
    if [ ! -z "$2" ] ; then
	echo "mv $fname $newname"
    else
	mv "$fname" "$newname"
    fi
}
