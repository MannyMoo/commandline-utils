#!/bin/bash

# Tools for bash. 

alias fresh-bash="env -i SHELL=/bin/bash HOME=$HOME TERM=$TERM USER=$USER PATH=/usr/sue/bin:/bin:/usr/bin:/usr/sbin:/sbin bash"
alias fresh-bash-login="fresh-bash --login"

function bash-script() {
    # Create a new executable bash script with the given name and either
    # fill it with commands or edit it. 
    local fname=$1
    echo "#!/bin/bash
" > $fname
    chmod +x $fname
    if [ ! -z $2 ] ; then
	echo $2 >> $fname
    else 
	eval "$EDITOR $fname"
    fi
}