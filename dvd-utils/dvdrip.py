#!/usr/bin/env python

'''Rip a dvd using HandBrakeCLI.'''

import subprocess, os, re, sys
from tempfile import TemporaryFile
from datetime import datetime, timedelta
from copy import deepcopy

def is_sublist(sublist, fulllist) :
    '''Check if 'sublist' is contained in 'fulllist', in order. Returns
    the list of start indices of sublist in fulllist for all instances found,
    else an empty list.'''
    indices = []
    for istart in xrange(0, len(fulllist) - len(sublist) + 1) :
        if fulllist[istart:istart + len(sublist)] == sublist :
            indices.append(istart)
    return indices

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
                 savepreset = False, bitrate = '2200', logfile = sys.stdout) :

        self.input = input
        self.output = output
        self.scanlogfile = scanlogfile
        self.subtitles = subtitles
        self.audiotrack = audiotrack
        self.preset = preset
        self.quality = quality
        self.savepreset = savepreset
        self.titleinfos = self.dvd_scan()
        self.bitrate = bitrate
        self.logfile = logfile
        
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

        titles = {}
        for line in self.scanlogfile :
            line = line[:-1]
            if not line.lstrip().startswith('+') :
                continue
            #print line
            depth = line.find('+')/2
            line = line.lstrip(' +')
            if 0 == depth :
                titleno = line.split()[-1].replace(':','')
                info = {'titleno' : titleno}
                titles[titleno] = info
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
        if isinstance(titleinfo, (int,str)) :
            if not str(titleinfo) in self.titleinfos :
                raise ValueError("No title {0} on this DVD, options are: {1}"
                                 .format(titleinfo, self.titleinfos.keys()))
            titleinfo = self.titleinfos[str(titleinfo)]

        outputfile = self.output.format(str(titleinfo['titleno']).zfill(2))
        args = ['nice', '-n', '5', 'HandBrakeCLI', '-i', self.input, '-o', outputfile,
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
            '--decomb', '--no-deblock',]
        # Video
        # args += ['-e', 'x264', '--vfr',]
        if self.bitrate :
            args += ['-b', self.bitrate]
        # Audio
        # args += ['-E', 'av_aac,copy:ac3', '-B', '160,640', '--audio-fallback', 'av_aac',]
        # Advanced
        args += ['--encopts', 'level=4.1:vbv-bufsize=78125:vbv-maxrate=62500:ref=4:b-adapt=2:direct=auto:me=umh:subme=9:analyse=all',
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

    def _duration(self, timestr) :
        '''Convert a string of the format H:M:S to a duration in seconds.'''
        # Bit of abuse of datetime in order to parse the duration.
        # Shouldn't be a problem as we'll never have a DVD with a
        # title longer than 24 hrs (surely).
        zero = datetime(1900, 1, 1)
        duration = datetime.strptime(timestr, '%H:%M:%S')
        for attr in 'year', 'month', 'day' :
            setattr(duration, attr, getattr(zero, attr))
        return (duration - zero).total_seconds()
        
    def duration(self, titleinfo) :
        '''Get the duration in seconds of the given title.'''
        return self._duration(titleinfo['duration'])
        
    def total_duration(self, filterfunc = None) :
        '''Get the total duration of all titles.'''
        if not filterfunc :
            return sum(self.duration(title) for title in self.titleinfos.values())
        return sum(self.duration(title) for title in self.titleinfos.values() if filterfunc(title))
        
    def unique_titles(self) :
        '''Get unique titles in this DVD (since some have, eg, two titles with the same episode, or
        one title that contains others for a 'play all' functionality).'''

        # Copy titles.
        copytitles = deepcopy(self.titleinfos)
        for title in copytitles.values() :
            del title['titleno']
            for i, info in enumerate(title['extrainfo']) :
                title['extrainfo'][i] = re.sub('ttn [0-9]+, ', '', info)

        # Remove duplicates.
        titlenos = copytitles.keys()
        for i, titleno in enumerate(titlenos) :
            if not titleno in copytitles :
                continue
            for checktitleno in titlenos[i+1:] :
                if not checktitleno in copytitles :
                    continue
                if copytitles[checktitleno] == copytitles[titleno] :
                    print >> self.logfile, 'Title', checktitleno, 'is the same as title', titleno + ', removing it'
                    del copytitles[checktitleno]
                    
        # Check if one title's chapters are contained in another title's.
        # This checks by number of blocks and duration of each chapter
        # in order, so should be very unlikely to give a false positive.
        for title in copytitles.values() :
            chapters = []
            for chapter in title['chapters'] :
                # Remove the 'cell' number so it just has 'blocks' and 'duration'
                chapters.append(', '.join(chapter.split(', ')[1:]))
            title['chapters'] = chapters
            title['contains'] = []
        for ititle, title in copytitles.items() :
            for icheck, checktitle in copytitles.items() :
                if ititle == icheck :
                    continue
                istart = is_sublist(checktitle['chapters'], title['chapters'])
                if not istart :
                    continue
                for i in istart :
                    title['contains'].append((icheck, i))
                    
        uniquetitles = {}
        for ititle, title in copytitles.items() :
            if not title['contains'] :
                uniquetitles[ititle] = title
            title['contains'].sort(key = lambda pair : pair[1])
            containedchapters = []
            for icontained, istart in title['contains'] :
                containedchapters += copytitles[icontained]['chapters']
            if containedchapters == title['chapters'] :
                print >> self.logfile, 'Title', ititle, 'is the sum of titles', str([pair[0] for pair in title['contains']]) \
                    + ', removing it.'
            else :
                uniquetitles[ititle] = title
        return {titleno : self.titleinfos[titleno] for titleno in uniquetitles}

    def rip_all(self, onlyunique = True) :
        '''Rip all titles in the DVD, optionally only the unique ones.'''
        if onlyunique :
            titles = self.unique_titles()
        else :
            titles = self.titleinfos

        retvals = {}
        for titleno, title in titles.items() :
            titleretval = self.rip_title(title)
            if 0 != titleretval :
                print >> self.logfile, 'Error ripping title', titleno + '. Return value:', + titleretval
            retvals[titleno] = titleretval
        return retvals
    
if __name__ == '__main__' :
    from pprint import pprint
    #input = '/media/repository/media/dvdrips/queued/FARSCAPE_SEASON2_DISC6/FARSCAPE_SEASON2_DISC6.iso'
    input = '/media/repository/media/dvdrips/processing/FIREFLY_DISC1/FIREFLY_DISC1.iso'
    #input = '/media/repository/media/dvdrips/queued/TAXI_DRIVER/TAXI_DRIVER.iso'
    output = input[:-4] + '_Title_{0}.mp4'
    ripper = DVDRipper(input = input,
                       output = output,
                       scanlogfile = input[:-4] + '.scan',
                       quality = 'vfast',
                       bitrate = '100',
                       savepreset = True)
    ripper.rip_title(4)
    #uniquetitles = ripper.unique_titles()
    #pprint(uniquetitles)
