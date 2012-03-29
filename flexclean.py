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


import os
import re
import sys
from glob import glob

def handle_arguments():
    defaults = { 'p':'.',
                 'm':'*.tar',
                 'd':1,
                 'r':'(.*)\.([0123456789])\.([0123456789]{12})\..*' }

    try:
        import argparse
    except ImportError:
        print "No argparse module available. Using defaults only."
        return defaults
        

    """Handle command line parameters.
    """
    description="Simple python script to clean up outdated 'timestamped' files created by the flexbackup software. "\
                "Without any parameters, the script will search the" \
                "current working directory for all files with postfix" \
                "'*.tar'. The files found are then matched against a regular expression, which will split "\
                "the filenames in three parts: prefix, level and timestamp. The filenames are then "\
                "grouped by prefix, then by level and finally ordered by timestamp inside each group. "\
                "After all this, the selected number of 'oldest' files per level are selected for deletion. "\
                "Before deleting anything, the script requires the user to write a word 'confirm', after which "\
                "it will delete all files listed to be deleted."
    
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-p', action='store', metavar='path', default=defaults['p'], type=str,
                        help='Path to clean up (default: current directory)')
    parser.add_argument('-m', action='store', metavar='wildcard', default=defaults['m'], type=str,
                        help='Wildcard of files to match - only these will be checked (default: *.tar)')
    parser.add_argument('-d', action='store', metavar='depth', default=defaults['d'], type=int,
                        help='Number of files per level to keep (default: 1)')
    parser.add_argument('-r', action='store', metavar='regexp', default=defaults['r'],
                        type=str,
                        help='Regular expression to match the filenames against '\
                        '(default: (.*)\.([0123456789])\.([0123456789]{12})\..*). Please note that the regexp must '\
                        'return three values: <prefix>,<level>,<timestamp> to be compatible with this script')
    
    # Reading through the dict, just to be able to do the default() thingy
    return parser.parse_args().__dict__


def main():
    # Arguments
    arguments = handle_arguments()
    path = arguments['p']
    match = arguments['m']
    extract = arguments['r']
    keep_depth = arguments['d']

    print "FlexClean v1.2 - A Really simple tool to clean up obsolete files from a flexbackup timestamped archive"

    # Stupid user check
    assert keep_depth > 0

    # Get files
    files = glob( os.path.join(path, match) )
    if len(files) == 0:
        print "No matching (%s) files found from given path (%s) - will do nothing" % \
              (match, path)
        print "Try parameter -h for help and options"
        sys.exit(1)


    # split and organize
    filesbyprefix = {}

    try:
        extract_re=re.compile(extract)
    except re.error:
        print "Failed to compile the given regular expression. Please check your regexp or use the default."
        sys.exit(1)

    for infile in files:
        match = extract_re.match(infile)
        if match:
            try:
                prefix,level,timestamp = match.groups()
            except ValueError:
                print "Failed to get required three fields from the regexp!"
                print "The regular expression must match three groups in order:"
                print "<prefix>,<level>,<timestamp>"
                sys.exit(1)

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
        print "**** Keeping files: ****"
        for f in kept_files:
            print f[1]
    else:
        print "No files to keep! This is probably an error, will not continue!"
        sys.exit(1)

    if len(deleted_files) > 0:
        print "\n**** About to delete files: ****"
        for f in deleted_files:
            print f[1]

        inp=raw_input("Type in 'confirm' to delete these files, or anything else to abort: ")
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
