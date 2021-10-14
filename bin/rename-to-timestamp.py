#!/usr/bin/env python3

'''Rename files to their EXIF timestamp.'''
from __future__ import print_function
import subprocess
import shutil
import argparse
import os
import sys
import click


@click.group()
def main():
    pass


def get_timestamp_identify(fname) :
    '''Get the EXIF timestamp from a photo file. Requires Imagemagick for identify.'''
    proc = subprocess.Popen(['identify', '-verbose', fname], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout, stderr = proc.communicate()
    stdout = stdout.decode(sys.stdout.encoding)
    stderr = stderr.decode(sys.stderr.encoding)
    if 0 != proc.poll() :
        raise OSError("Failed to call 'identify' (requires imagemagick to be installed) \n" + stderr)

    dline = filter(lambda l : 'DateTime' in l, stdout.splitlines())[0]
    return ' '.join(dline.split()[-2:])


def get_timestamp_exif(fname):
    '''Get the EXIF timestamp from a photo file. Requires exif commandline tool.'''
    args = ['exif', '-m', fname]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    stdout = stdout.decode(sys.stdout.encoding)
    stderr = stderr.decode(sys.stderr.encoding)
    if 0 != proc.poll():
        raise OSError('Failed to call {0!r} (requires exif to be installed)\n'.format(' '.join(args))
                      + stderr)
    stdout = stdout.splitlines()
    date = ''
    dline = list(filter(lambda l : l.startswith('Date and Time'), stdout))
    if dline:
        date += dline[0].split('\t')[-1].strip()
    msline = list(filter(lambda l : l.startswith('Sub-second Time'), stdout))
    if msline:
        ms = msline[0].split('\t')[-1].strip()
        date += '.' + ms.zfill(3)
    return date


def md5sum(fname):
    '''Get the md5sum of the file.'''
    args = ['md5sum', fname]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    stdout = stdout.decode(sys.stdout.encoding)
    stderr = stderr.decode(sys.stderr.encoding)
    if 0 != proc.poll():
        raise OSError('Failed to call {0!r} (requires md5sum to be installed)\n'.format(' '.join(args))
                      + stderr)
    return stdout.split()[0]


class Renamer(object):
    '''File renamer.'''
    def __init__(self, dryrun=False, outputdir=None, logs=(sys.stdout,),
                 get_timestamp=get_timestamp_exif):
        self.dryrun = dryrun
        self.outputdir = outputdir
        self.logs = logs
        self.get_timestamp = get_timestamp
        
    def _rename(self, fname, newname):
        '''Rename a file.'''
        for f in self.logs:
            print(fname, '->', newname, file=f)
        if self.dryrun or fname == newname:
            return
    
        # Try using shutil, if that fails for whatever reason try using system mv.
        try :
            shutil.move(fname, newname)
        except :
            result = subprocess.call(['mv', fname, newname])
            if 0 != result :
                raise OSError("Couldn't rename " + fname + " to " + newname + "!")

    def output_name(self, fname):
        '''Get the output name of a file.'''
        date = self.get_timestamp(fname)
        date = date.replace(' ', '_').replace(':', '-')
        if not self.outputdir:
            outputdir = os.path.dirname(fname)
        else:
            outputdir = self.outputdir
        datename = os.path.join(outputdir, date)
        md5 = md5sum(fname)
        filetype = '.' + fname.split('.')[-1].lower()
        newname = datename + '_' + md5 + filetype
        return newname

    def rename(self, fname):
        '''Rename the file to its EXIF timestamp.'''
        newname = self.output_name(fname)
        self._rename(fname, newname)
        return newname


@main.command()
@click.argument('files', nargs=-1)
@click.option('-o', '--outputdir', default=None,
              help='Output directory for renamed files (default same as input files).')
@click.option('-f', '--logfile', default=None,
              help='Log file for renamings')
@click.option('-n', '--dryrun', is_flag=True,
              help='Dry run - output renamings but don\'t rename files.')
def rename(files, outputdir, dryrun, logfile):
    if outputdir and not os.path.exists(outputdir):
        os.makedirs(outputdir)
        
    logs = [sys.stdout,]
    if logfile:
        fout = open(logfile, 'w')
        logs.append(fout)

    renamer = Renamer(dryrun=dryrun, outputdir=outputdir, logs=logs)
    for fname in files:
        renamer.rename(fname)
        
    if logfile:
        fout.close()


if __name__ == '__main__' :
    main()
