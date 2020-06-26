#!/bin/bash

function dvd_title() {
    #blkid -o value -s LABEL /dev/dvd
    # This has the advantage of returning an empty string if the dvd tray is open,
    # while blkid closes the dvd tray.
    udevadm info -n dvd -q property | sed -n 's/^ID_FS_LABEL=//p'
}
