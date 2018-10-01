#!/usr/bin/env python

'''Rip a dvd using HandBrakeCLI.'''

import subprocess
from tempfile import TemporaryFile

def dvd_scan(logfile = None, device = '/dev/dvd') :
    '''Scan a DVD and parse the info on the titles it contains. 'logfile' can be a
    file containing the output of a previous call to HandBrakeCLI --scan, in which
    case that's parsed instead.'''
    
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

presets = {
    'vfast_1080' : 'Very Fast 1080p30',
    'vfast_720' : 'Very Fast 720p30',
    'vfast_576' : 'Very Fast 576p25',
    'vfast_480' : 'Very Fast 480p30',
    'fast_1080' : 'Fast 1080p30',
    'fast_720' : 'Fast 720p30',
    'fast_576' : 'Fast 576p25',
    'fast_480' : 'Fast 480p30',
    'hq_1080' : 'HQ 1080p30 Surround',
    'hq_720' : 'HQ 720p30 Surround',
    'hq_576' : 'HQ 576p25 Surround',
    'hq_480' : 'HQ 480p30 Surround',
    'superhq_1080' : 'Super HQ 1080p30 Surround',
    'superhq_720' : 'Super HQ 720p30 Surround',
    'superhq_576' : 'Super HQ 576p25 Surround',
    'superhq_480' : 'Super HQ 480p30 Surround',
}

def rip_title(inputfile, titleno, titleinfo, outputfile, preset = None, quality = 'hq',
              subtitles = 'all', audiotrack = 'all') :
    args = ['HandBrakeCLI', '-i', inputfile, '-o', outputfile, '-t', str(titleno)]

    if not preset :
        preset = titleinfo['size'].split('x')[0]
        preset = presets[quality + '_' + size]
    elif preset in presets :
        preset = presets[preset]
    args += ['--preset', preset]

    # Optimise for streaming and add chapter markers.
    args += ['-O', '-m']
    
    if subtitles :
        if isinstance(subtitles, str) :
            if subtitles.lower() == 'all' :
                subtitles = 'all'
            else :
                subtitles = (subtitles,)

        if subtitles == 'all' :
            args += ['-s', ','.join(str(i+1) for i in xrange(len(titleinfo['subtitle tracks'])))]
        else :
            args += ['--subtitle-lang-list', ','.join(subtitles)]
        #args += ['--srt-file', outputfile + '.srt']
        
    if audiotrack :
        if audiotrack.lower() == 'all' :
            audiotrack = ','.join(str(i+1) for i in range(len(titleinfo['audio tracks'])))
        args += ['-a', audiotrack]
        
    with open(outputfile + '.handbrake.log', 'w') as logfile :
        proc = subprocess.Popen(args, stdout = logfile, stderr = logfile)
        proc.wait()
    return proc.poll()
    
if __name__ == '__main__' :
    from pprint import pprint
    info = dvd_scan('/media/repository/media/dvdrips/queued/FIREFLY_DISC4.scan')
    rip_title('/media/repository/media/dvdrips/queued/FIREFLY_DISC4.iso',
              #len(info)-1, info[-1],
              1, info[0],
              '/tmp/test.mp4', quality = 'hq')
