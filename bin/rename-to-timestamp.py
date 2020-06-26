#!/usr/bin/env python

'''Rename files to their EXIF timestamp.'''

import subprocess, shutil, argparse, os

def get_timestamp(fname) :
    '''Get the EXIF timestamp from a photo file. Requires Imagemagick for identify.'''
    proc = subprocess.Popen(['identify', '-verbose', fname], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if 0 != proc.poll() :
        raise OSError("Failed to call 'identify' (requires imagemagick to be installed) \n" + stderr)
    
    dline = filter(lambda l : 'DateTime' in l, stdout.splitlines())[0]
    return ' '.join(dline.split()[-2:])

def rename(fname, newname) :
    '''Rename a file.'''
    # Try using shutil, if that fails for whatever reason try using system mv.
    try :
        shutil.move(fname, newname)
    except :
        result = subprocess.call(['mv', fname, newname])
        if 0 != result :
            raise OSError("Couldn't rename " + fname + " to " + newname + "!")

def rename_to_timestamp(fname, dryrun = False, prevrenames = ()) :
    '''Rename the file to its EXIF timestamp.'''

    date = get_timestamp(fname)
    dirname = os.path.dirname(fname)
    datename = os.path.join(dirname, date.replace(' ', '_').replace(':', ''))
    filetype = '.' + fname.split('.')[-1].lower()
    newname = datename + filetype
    if newname == fname :
        if dryrun :
            print fname, '->', newname
        return newname
    
    # Check if a file of that name exists, or would exist in the case of a dry run.
    if os.path.exists(newname) or newname in prevrenames :
        i = 1
        newname = datename + '_' + str(i) + filetype
        while os.path.exists(newname) or newname in prevrenames :
            i += 1
            newname = datename + '_' + str(i) + filetype
    if dryrun :
        print fname, '->', newname
        return newname

    rename(fname, newname)
    return newname

def main() :
    '''Main method.'''
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--dryrun', '-n', action = 'store_true',
                           help = "Don't rename anything, just print what would be renamed")
    argparser.add_argument('files', nargs = '+', help = 'Files to rename.')

    args = argparser.parse_args()

    renames = []
    for fname in args.files :
        renames.append(rename_to_timestamp(fname, dryrun = args.dryrun, prevrenames = renames))

    # For any photos with the same timestamp, and a _0 suffix to the first one, so they're correctly ordered
    # alphabetically.
    # There might be a tidier way to do this.
    for fname in filter(lambda f : f.split('.')[-2].endswith('_1'), renames) :
        # Remove the _1.
        name = '.'.join(fname.split('.')[:-1])[:-2]
        filetype = '.' + fname.split('.')[-1]
        newname = name + '_0' + filetype
        name += filetype
        if os.path.exists(newname) :
            raise OSError("Can't rename " + name + " -> " + newname + " as a file named " + newname \
                          + " already exists!")

        if args.dryrun :
            print name, '->', newname
        else :
            rename(name, newname)
        
if __name__ == '__main__' :
    main()
