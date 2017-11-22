#!/bin/sh

function source_all() {
    if [ ! -z "$COMMANDLINEUTILSROOT" ] ; then
        local d="$COMMANDLINEUTILSROOT"
    elif [ ! -z "$1" ] ; then 
	local d="$1"
    else
	# If you call this within a script this just finds the directory
	# of the parent script. 
	#local d="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
	local d='.'
    fi
    for f in `find "$d" -mindepth 2 -name "*.sh"` ; do
	#echo $f
	source $f
    done
}
