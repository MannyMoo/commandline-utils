#!/usr/bin/env python3

import argparse
import subprocess
import time
import getpass
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('command', nargs = '+', help = 'Command to execute')
parser.add_argument('--interval', type = int, default = 24*3600,
                    help = 'Interval at which to execute the command [s]')

args, unknown = parser.parse_known_args()
# Will this always work as intended?
command = list(args.command) + list(unknown)
print('Will execute command:')
print(' '.join(command))
print('every', args.interval, 'seconds')

pw = getpass.getpass('Enter password:')

while True:
    print('Call', ' '.join(command), 'at', datetime.datetime.today())
    proc = subprocess.Popen(command, stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            stdin = subprocess.PIPE,
                            text = True)
    stdout, stderr = proc.communicate(pw)
    if proc.poll() != 0:
        raise OSError('''Failed to call:
{0}
exit code: {1}
stdout:
{2}
stderr:
{3}
'''.format(' '.join(command), proc.poll(), stdout, stderr))

    print('stdout:')
    print(stdout)
    time.sleep(args.interval)
