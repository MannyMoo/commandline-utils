#!/bin/bash

function get-mac-address() {
    info=`ifconfig $1`
    addresses=`echo $info | grep ether | sed "s/\s*ether //"`
    echo $addresses
}

function gen-mac-address() {
    openssl rand -hex 6 | sed 's/\(..\)/\1:/g; s/.$//'
}

function set-mac-address() {
    # The original MAC address should be restored on reboot.
    sudo ifconfig $1 ether $2
}

function spoof-mac-address() {
    dev="$1"
    original=`get-mac-address $dev`
    new=`gen-mac-address`
    set-mac-address $dev $new
    echo "Original MAC address for $1: $original"
    echo "New MAC address for $1:      $new"
}

function turn-device-on() {
    sudo ifconfig $1 up
}

function turn-device-off() {
    sudo ifconfig $1 down
}

function ssh-start-socks-tunnel() {
    # start an ssh SOCKS tunnel to the given port and server.
    local pid=$(ssh -D $1 -f -C -q -N $2 & echo $!)
    echo "tunnel pid: $pid"
    echo "set SOCKS proxy to:"
    echo "localhost:$1"
}
