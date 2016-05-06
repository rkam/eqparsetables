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

def main(argv):
    cwd = os.getcwd()
    config_path    = cwd + '/_eq_ra/data/config.ini'
    blacklist_path = cwd + '/_eq_ra/data/mobs_blacklist.ini'

    # parse arguments
    try:
        opts, args = getopt.getopt(argv, 'hp:b:', ['parsefile=', 'blacklist='])
    except getopt.GetoptError:
        print('myst.py -b <blacklist>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('myst.py -b <blacklist> files')
            sys.exit()
        elif opt in ('-b', '--blacklist'):
            blacklist_path = arg

    for f in args:
        ecp.EnjinDPSPrinter(
            gpd.GPDPSReader(f, config_path, blacklist_path)
        ).print_all_tables()


if __name__ == '__main__':
    main(sys.argv[1:])
