#!/usr/bin/env python

'''Rip a dvd using HandBrakeCLI.'''

import subprocess, os
from tempfile import TemporaryFile

class DVDRipper(object) :

    # These are stored in ~/.config/ghb/presets.json
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

    def __init__(self, input, output, scanlogfile = None, subtitles = 'all',
                 audiotrack = 'all', preset = None, quality = 'hq',
                 savepreset = False) :

        self.input = input
        self.output = output
        self.scanlogfile = scanlogfile
        self.subtitles = subtitles
        self.audiotrack = audiotrack
        self.preset = preset
        self.quality = quality
        self.savepreset = savepreset
        self.titleinfos = self.dvd_scan()

        if isinstance(subtitles, str) :
            if subtitles.lower() == 'all' :
                self.subtitles = 'all'
            else :
                self.subtitles = (subtitles,)

        self.audioname = None

    def dvd_scan(self) :
        '''Scan a DVD and parse the info on the titles it contains. 'scanlogfile' can be a
        file containing the output of a previous call to HandBrakeCLI --scan, in which
        case that's parsed instead.'''

        if not self.scanlogfile :
            self.scanlogfile = TemporaryFile()
            proc = subprocess.Popen(['HandBrakeCLI', '-i', device, '-t', '0', '--scan'],
                                    stdout = self.scanlogfile, stderr = self.scanlogfile)
            proc.wait()
            self.scanlogfile.seek(0)
        elif isinstance(self.scanlogfile, str) :
            self.scanlogfile = open(self.scanlogfile)

        titles = []
        for line in self.scanlogfile :
            line = line[:-1]
            if not line.lstrip().startswith('+') :
                continue
            #print line
            depth = line.find('+')/2
            line = line.lstrip(' +')
            if 0 == depth :
                info = {'titleno' : line.split()[-1].replace(':','')}
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
        self.scanlogfile.close()
        return titles

    def rip_title(self, titleinfo) :
        if isinstance(titleinfo, int) :
            infos = filter(lambda info : info['titleno'] == str(titleinfo), self.titleinfos)
            if not infos :
                raise ValueError("No title {0} on this DVD, options are: {1}"
                                 .format(titleinfo, [info['titleno'] for info in self.titleinfos]))
            titleinfo = infos[0]

        outputfile = self.output.format(titleinfo['titleno'])
        args = ['HandBrakeCLI', '-i', self.input, '-o', outputfile,
                '-t', str(titleinfo['titleno'])]

        width, height = titleinfo['size'].split('x')
        aspectratio, fps = titleinfo['display aspect'].split(', ')
        displaywidth = str(int(float(height) * float(aspectratio)))

        if not self.preset :
            preset = DVDRipper.presets[self.quality + '_' + height]
        elif self.preset in DVDRipper.presets :
            preset = DVDRipper.presets[self.preset]
        args += ['--preset', preset]

        # "Optimal" settings, following:
        # https://forums.plex.tv/t/dvd-rip-quality-on-plex-roku-ultra/172481/12

        args += [
            # Picture
            '-w', width, '-l', height, '--display-width', displaywidth,
            '--custom-anamorphic', '--modulus', '2',
            # Filter
            '--decomb', '--no-deblock',
            # Video
            # '-e', 'x264', '--vfr',
            '-b', '2200',
            # Audio
            # '-E', 'av_aac,copy:ac3', '-B', '160,640', '--audio-fallback', 'av_aac',
            # Advanced
            '--encopts', 'level=4.1:vbv-bufsize=78125:vbv-maxrate=62500:ref=4:b-adapt=2:direct=auto:me=umh:subme=9:analyse=all',
        ]
        if self.savepreset :
            args += ['--preset-export', os.path.split(outputfile)[1],
                     '--preset-export-file', outputfile + '.preset.json']

        # Optimise for streaming and add chapter markers.
        args += ['-O', '-m']

        if self.subtitles :
            if self.subtitles == 'all' :
                args += ['-s', ','.join(str(i+1) for i in xrange(len(titleinfo['subtitle tracks'])))]
            else :
                args += ['--subtitle-lang-list', ','.join(self.subtitles)]

        if self.audiotrack :
            if self.audiotrack.lower() == 'all' :
                audiotrack = ','.join(str(i+1) for i in range(len(titleinfo['audio tracks'])))
                audioname = ','.join(name.replace(',', '') for name in titleinfo['audio tracks'])
            else :
                audiotrack = self.audiotrack
                audioname = titleinfo['audio tracks'][int(audiotrack)+1].replace(',', '')
            args += ['-a', audiotrack, '-A', audioname]

        with open(outputfile + '.handbrake.log', 'w') as logfile :
            proc = subprocess.Popen(args, stdout = logfile, stderr = logfile)
            proc.wait()
        return proc.poll()

if __name__ == '__main__' :
    from pprint import pprint
    ripper = DVDRipper(input = '/media/repository/media/dvdrips/queued/FARSCAPE_SEASON2_DISC1/FARSCAPE_SEASON2_DISC1.iso',
                       output = '/tmp/test-farscape-hq576-{0}.mp4',
                       scanlogfile = '/media/repository/media/dvdrips/queued/FARSCAPE_SEASON2_DISC1/FARSCAPE_SEASON2_DISC1.scan',
                       quality = 'hq',
                       savepreset = True)
    ripper.rip_title(1)
