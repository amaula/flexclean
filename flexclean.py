#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

import argparse
import os
import re
from glob import glob

def handle_arguments():
    """Handle command line parameters.
    """
    parser = argparse.ArgumentParser()
    #parser.add_argument('-r', action='store', metavar='num', default=20, type=int,
    #                    help='Number of corrects required before considering as "learned" (default: 20)')
    #parser.add_argument('-m', action='store', metavar='num', default=0.4, type=float,
    #                    help='Required mean delay between characters (default: 0.4)')
    #parser.add_argument('-s', action='store', metavar='num', default=0.25, type=float,
    #                    help='Required standard deviation between characters (default: 0.25)')
    #parser.add_argument('-i', action='store', metavar='num', default=5, type=int,
    #                    help='History length to consider when checking mean/std values (default: 5)')
    
    return parser.parse_args()


def main():
    # Parameters
    path = './files'
    match = '*.tar'
    extract = '(.*)\.([0123456789])\.([0123456789]{12})\..*'
    keep_depth = 1
    
    # Arguments
    arguments = handle_arguments()

    # Get files
    files = glob( os.path.join(path, match) )

    # split and organize
    filesbyprefix = {}
    extract_re=re.compile(extract)
    for infile in files:
        match = extract_re.match(infile)
        if match:
            prefix,level,timestamp = match.groups()

            filesbylevel = filesbyprefix.get(prefix, {}) 
            files = filesbylevel.get(str(level), [])
            files.append( ( timestamp, infile ) )
            filesbylevel[str(level)] = files
            filesbyprefix[prefix] = filesbylevel

    print "Number of prefixes:", len(filesbyprefix), [ p for p in filesbyprefix ]

    # select for delete
    deleted_files = []
    kept_files = []
    for fg in filesbyprefix:
        filesbylevel = filesbyprefix[fg]
        # At this point filesbylevel contains a dict of files keyed by level.
        for level in sorted(filesbylevel):
            files = filesbylevel[str(level)]
            files.sort(key=lambda e: e[1], reverse=True)
            #print files
            # At this point, files contains a list of tuples of (timestamp, filename),
            # ORDERED by the timestamp in ascending order (newest on top)
            fcount = len(files)
            to_keep = files[:keep_depth]
            to_delete = files[keep_depth:]
            deleted_files.extend(to_delete)
            kept_files.extend(to_keep)

    # Now print
    print "Keeping files:"
    for f in kept_files:
        print f[1]

    if len(deleted_files) > 0:
        print "About to delete files:"
        for f in deleted_files:
            print f[1]

        inp=raw_input("Type in 'confirm' to delete these files: ")
        if inp == 'confirm':
            for f in deleted_files:
                os.remove(f[1])
                print "Deleted file", f[1]
        else:
            print "Not confirmed, will not delete anything."
    else:
        print "No files to delete."


            
if __name__ == '__main__':
    main()
    print "Exit."
