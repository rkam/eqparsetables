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
    print('eqparsedpstables.py -b <blacklist> -m <members> -a <applicants> -o <others> [-c] parse_dump_files')              ##TODO: basename $0
    print('  where blacklist is a file containing mobs to ignore')
    print('          members    is a file containing full member raiderss')
    print('          applicants is a file containing applicants')
    print('          others     is a file containing non-guild raiders')
    print("  -c include class in output (useful for later grep'ing)")
    print('')
    sys.exit(code)

def main(argv):
    include_class = False

    cwd = os.getcwd()
    config_files = {
        'members':   cwd + '/' + '_eq_ra/data/full_members.ini',
        'apps':      cwd + '/' + '_eq_ra/data/applicants.ini',
        'others':    cwd + '/' + '_eq_ra/data/others.ini',
        'blacklist': cwd + '/' + '_eq_ra/data/mobs_blacklist.ini'
    }

    # parse arguments
    try:
        opts, args = getopt.getopt(argv, 'hca:b:m:o:', ['applicants=', 'blacklist=', 'members=', 'others='])
    except getopt.GetoptError:
        usage(2)
    for opt, arg in opts:
        if opt == '-h':
            usage(0)
            sys.exit()
        elif opt in ('-a', '--applicants'): config_files['applicants']  = arg
        elif opt in ('-b', '--blacklist'):  config_files['blacklist']   = arg
        elif opt in ('-m', '--members'):    config_files['members']     = arg
        elif opt in ('-o', '--others'):     config_files['others']      = arg
        elif opt in ('-c', '--class'):      include_class = True

    for f in args:
        ecp.EnjinDPSPrinter(
            gpd.GPDPSReader(f, config_files)
        ).print_all_tables(include_class)


if __name__ == '__main__':
    main(sys.argv[1:])
