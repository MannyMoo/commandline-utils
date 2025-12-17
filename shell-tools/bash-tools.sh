#!/bin/bash

# Tools for bash. 
source $COMMANDLINEUTILSROOT/shell-tools/script-tools.sh

function fresh-bash() {
    env -i SHELL=/bin/bash HOME=$HOME TERM=$TERM USER=$USER PATH=/usr/sue/bin:/bin:/usr/bin:/usr/sbin:/sbin bash $@
}

function fresh-bash-login(){
    fresh-bash --login $@
}

function bash-script() {
    # Create a new executable bash script with the given name and either
    # fill it with commands or edit it. 
    exe-script bash $1 $2
}

function fix-newline() {
    # Fix when newlines get messed up in the terminal
    stty sane
}
