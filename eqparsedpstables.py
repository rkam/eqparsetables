#!/usr/bin/env python3
"""Formats and filters GamParse spells and disc forum output."""

import sys
import getopt
import os

import gpdpsreader     as gpd
import enjindpsprinter as ecp

__author__     = 'Ric Kamicar'
__copyright__  = 'Copyright 2016, Ric Kamicar'
__credits__    = ['Ric Kamicar', 'Andrew Quinn']
__license__    = 'Simplified BSD'
__version__    = '0.1'
__maintainer__ = 'Ric Kamicar'
__email__      = 'rkamicar@gmail.com'
__status__     = 'Prototype'

def usage(code):
    print('eqparsedpstables.py args parse_dump_files')      ##TODO: basename $0
    print('  where args are:')
    print('     -a --applicants=   a file containing applicants')
    print('     -b --blacklist=    a file containing mobs to ignore')
    print('     -g --group_makeup= a file containing raid group makeup (no default)')
    print('     -m --members=      a file containing full member raiderss')
    print('     -o --others=       a file containing non-guild raiders')
    print("        -add-class,")
    print("        -add-group-id,")
    print("        -add-group-classes,")
    print("        -add-group-members:")
    print("             include XXX in output (useful for later grep'ing)")
    print('')
    sys.exit(code)

def main(argv):
    add_columns = []

    cwd = os.getcwd()
    config_files = {
        'apps':      cwd + '/' + '_eq_ra/data/applicants.ini',
        'blacklist': cwd + '/' + '_eq_ra/data/mobs_blacklist.ini',
        'groups':    None,
        'members':   cwd + '/' + '_eq_ra/data/full_members.ini',
        'others':    cwd + '/' + '_eq_ra/data/others.ini',
    }

    # parse arguments
    try:
        opts, args = getopt.getopt(argv, 'ha:b:g:m:o:',
                        ['applicants=', 'blacklist=', 'members=', 'others=',
                         'group_makeup=',
                         'add-class', 'add-group-id',
                         'add-group-classes', 'add-group-members',
                         ])
    except getopt.GetoptError:
        usage(2)
    for opt, arg in opts:
        if opt == '-h':
            usage(0)
            sys.exit()
        elif opt in ('-a', '--applicants'):   config_files['applicants'] = arg
        elif opt in ('-b', '--blacklist'):    config_files['blacklist']  = arg
        elif opt in ('-m', '--members'):      config_files['members']    = arg
        elif opt in ('-o', '--others'):       config_files['others']     = arg

        elif opt in ('-g', '--group_makeup'): config_files['groups']     = arg

        elif opt in ('--class'):             add_columns.append('class')
        elif opt in ('--add-group-id'):      add_columns.append('groupID')
        elif opt in ('--add-group-classes'): add_columns.append('groupClasses')
        elif opt in ('--add-group-members'): add_columns.append('groupMembers')

    for f in args:
        ecp.EnjinDPSPrinter(
            gpd.GPDPSReader(f, config_files)
        ).print_all_tables(add_columns)


if __name__ == '__main__':
    main(sys.argv[1:])
