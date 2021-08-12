#!/bin/bash

# Aliases for tmux

function tn() {
    if [ -z "$1" ] ; then
	name=default
    else
	name="$1"
    fi
    tmux new-session -s $name
}

function ta() {
    if [ -z "$1" ] ; then
	name=default
    else
	name="$1"
    fi
    tmux attach -d -t $name
}

alias tl="tmux ls"
