#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-
"""
flexclean - A Really simple tool to clean up obsolete files from a flexbackup timestamped archive
Copyright (C) 2012 Antti Maula

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See <http://www.gnu.org/licenses/>.
"""



import argparse
import os
import re
import sys
from glob import glob

def handle_arguments():
    """Handle command line parameters.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store', metavar='path', default='.', type=str,
                        help='Path to clean up (default: current directory)')
    parser.add_argument('-m', action='store', metavar='wildcard', default='*.tar', type=str,
                        help='Wildcard of files to match - only these will be checked (default: *.tar)')
    parser.add_argument('-d', action='store', metavar='depth', default=1, type=int,
                        help='Number of files per level to keep (default: 1)')
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
    path = arguments.p
    match = arguments.m
    keep_depth = arguments.d

    # Stupid user check
    assert keep_depth > 0

    # Get files
    files = glob( os.path.join(path, match) )
    if len(files) == 0:
        print "No matching (%s) files found from given path (%s) - will do nothing" % \
              (match, path)
        sys.exit(1)


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
    if len(kept_files) > 0:
        print "Keeping files:"
        for f in kept_files:
            print f[1]
    else:
        print "No files to keep! This is probably an error, will not continue!"
        sys.exit(1)

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
