#!/usr/bin/env python

import os, fcntl, CDROM, sys

def drive_status(drive):
    fd = os.open(drive, os.O_RDONLY | os.O_NONBLOCK)
    rv = fcntl.ioctl(fd, CDROM.CDROM_DRIVE_STATUS)
    os.close(fd)
    return rv

if __name__ == '__main__' :
    # returns 1 if it's open, 0 if not.
    sys.exit(drive_status(sys.argv[1]) == CDROM.CDS_TRAY_OPEN)
