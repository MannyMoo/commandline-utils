#!/bin/bash


if [ -z $EMACS ] ; then 
    export EMACS=emacs
fi
export EMACSBASE=`basename $EMACS`

if [ -z $EMACSCLIENT ] ; then
    export EMACSCLIENT=emacsclient
fi

function grep-emacs-daemon() {
    ps aux | grep -i "emacs.*daemon"
}

function is-emacs-demon-running() {
    if [ `grep-emacs-daemon | wc -l` = 1 ] ; then
	echo 0
    else
	echo 1
    fi
}

function emacs-daemon() {
    if [ `is-emacs-demon-running` = 0 ] ; then
	$EMACS --daemon >& /dev/null
    fi
}

alias emd=emacs-daemon
if [ -z $USEEMACSDAEMON ] || [ ! "$USEEMACSDAEMON" = "0" ] ; then
    RUNEMACS="$EMACSCLIENT -c"
else
    RUNEMACS="$EMACS"
fi

alias em="$RUNEMACS -nw"
alias emn="em"

alias emwd="emd;em"
alias emnwd="emd;emn"
alias e=em
alias en=emn
