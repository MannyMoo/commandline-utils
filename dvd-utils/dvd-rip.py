#!/usr/bin/env python

'''Rip a dvd using HandBrakeCLI.'''

import subprocess
from tempfile import TemporaryFile

def dvd_scan(logfile = None, device = '/dev/dvd') :
    if not logfile :
        logfile = TemporaryFile()
        proc = subprocess.Popen(['HandBrakeCLI', '-i', device, '-t', '0', '--scan'],
                                stdout = logfile, stderr = logfile)
        proc.wait()
        logfile.seek(0)
    elif isinstance(logfile, str) :
        logfile = open(logfile)

    titles = []
    for line in logfile :
        line = line[:-1]
        if not line.lstrip().startswith('+') :
            continue
        #print line
        depth = line.find('+')/2
        line = line.lstrip(' +')
        if 0 == depth :
            info = {}
            titles.append(info)
        elif 1 == depth :
            vals = filter(None, line.split(':'))
            # if it's the name of a list of attributes, like 'chapters'
            if len(vals) == 1 :
                # if it's an info line without a name
                if not ':' in line :
                    info['extrainfo'] = info.get('extrainfo', []) + [line]
                    continue
                # else make a list to contain the sub-info.
                subinfo = []
                info[vals[0]] = subinfo
            # special treatment for 'size' since it also contains other attributes on the same line.
            elif vals[0] == 'size' :
                vals = filter(None, line.split(', '))
                vals[-2:] = [', '.join(vals[-2:])]
                print line
                print vals
                for v in vals :
                    v = v.split(':')
                    info[v[0]] = v[1].strip()
            # if it's a single valued attribute.
            else :
                info[vals[0]] = ':'.join(vals[1:]).strip()
        elif 2 == depth :
            subinfo.append(line)
    logfile.close()
    return titles

if __name__ == '__main__' :
    from pprint import pprint
    pprint(dvd_scan('/media/repository/media/dvdrips/queued/FIREFLY_DISC2.scan'))
