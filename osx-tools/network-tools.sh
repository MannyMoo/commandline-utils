#!/bin/bash

function list-network-ports() {
    networksetup -listallhardwareports
}

function get-wifi-device() {
    list-network-ports | grep "Wi-Fi" -A 1 | grep "Device" | sed "s/Device: //"
}

function set-airport-power() {
    networksetup -setairportpower $1 $2
}

function turn-airport-off() {
    set-airport-power $1 off
}

function turn-airport-on() {
    set-airport-power $1 on
}

function turn-wifi-off() {
    turn-airport-off `get-wifi-device`
}

function turn-wifi-on() {
    turn-airport-on `get-wifi-device`
}

function get-wifi-network() {
    networksetup -getairportnetwork `get-wifi-device` | sed "s/Current Wi-Fi Network: //"
}

function is-wifi-network() {
    if [ "`get-wifi-network`" = "$1" ] ; then
	echo 1
    else
	echo 0
    fi
}

function connect-to-wifi-network() {
    # Got "Error: -3905  Timeout error" doing connect-to-wifi-network "The Subethernet"
    networksetup -setairportnetwork `get-wifi-device` $1 $2
}

