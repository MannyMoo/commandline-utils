#!/bin/bash

function exe-script() {
    # Create a new executable script with the given name and shell 
    # and either fill it with commands or edit it. 
    local shell=$1
    local fname=$2
    if [ "python" = "$shell" ] ; then
	echo "#!/usr/bin/env python
" > $fname
    else 
	echo "#!$(which $shell)
" > $fname
    fi
    chmod +x $fname
    if [ ! -z $3 ] ; then
	echo $3 >> $fname
    else 
	eval "$EDITOR $fname"
    fi
}

function python-script() {
    exe-script python $1 $2
}
