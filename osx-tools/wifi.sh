#!/bin/bash

source network-tools.sh

words=(Blue blue Bleu bleu Bloo bloo)
for w1 in words ; do
    for w2 in words ; do
	for w3 in words ; do
	    connect-to-wifi-network virgin "$w1$w2$w3"
