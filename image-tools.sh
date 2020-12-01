#!/bin/bash

function img-creation-date() {
    # Get the creation date of an image. Must have either identify or exiftool installed
    img=$1
    if [ ! -z "$(command -v identify)" ] ; then
	info="$(identify -verbose $img | grep 'Create \?Date')"
    elif [ ! -z "$(command -v exiftool)" ] ; then
	info="$(exiftool DSC_0318.JPG | grep 'Create \?Date' | tail -n 1 | sed 's/T/ /')"
    else
	echo "Requires identify or exiftool!"
    fi

    cdate="$(echo ${info} | sed 's/Create.*Date[ ]*: //')"
    echo "$cdate"
}
