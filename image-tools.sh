#!/bin/bash

function img-creation-date() {
    # Get the creation date of an image. Must have either identify or exiftool installed
    img=$1
    if [ ! -z "$(command -v identify)" ] ; then
	info="$(identify -verbose $img)"
    elif [ ! -z "$(command -v exiftool)" ] ; then
	info="$(exiftool DSC_0318.JPG)"
    else
	echo "Requires identify or exiftool!"
    fi
    info="$(echo ${info} | grep 'Create \?Date' | tail -n 1 | sed 's/T/ /')"
    cdate="$(echo ${info} | awk '{print $(NF-1), $NF}')"
    echo "$cdate"
}
