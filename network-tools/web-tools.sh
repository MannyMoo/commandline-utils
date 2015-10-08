#!/bin/bash

function external-ip() {
    wget -qO- http://ipecho.net/plain ; echo
}

