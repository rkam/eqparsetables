#!/usr/bin/env python3
"""Formats and filters GamParse spells and disc forum output."""

import sys
import getopt
import os
import gpcastreader as gpc
import enjincastprinter as ecp

__author__ = 'Andrew Quinn'
__copyright__ = 'Copyright 2015-2016, Andrew Quinn'
__credits__ = ['Andrew Quinn']
__license__ = 'Simplified BSD'
__version__ = '0.1'
__maintainer__ = 'Andrew Quinn'
__email__ = 'andrew@under.co.nz'
__status__ = 'Prototype'


def main(argv):
    cwd = os.getcwd()
    config_path = cwd + '/config.txt'
    input_path = cwd + '/parse.txt'
    blacklist_path = cwd + '/blacklist.txt'

    # parse arguments
    try:
        opts, args = getopt.getopt(argv, 'hp:b:', ['parsefile=', 'blacklist='])
    except getopt.GetoptError:
        print('myst.py -p <parsefile> -b <blacklist>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('myst.py -p <parsefile> -b <blacklist>')
            sys.exit()
        elif opt in ('-p', '--parsefile'):
            input_path = arg
        elif opt in ('-b', '--blacklist'):
            blacklist_path = arg

    reader = gpc.GPCastReader(input_path, config_path, blacklist_path)
    printer = ecp.EnjinCastPrinter(reader.get_spells_cast_by_class(), reader.classes,
                                   reader.caster_dod, reader.config)

    printer.print_all_tables()


if __name__ == '__main__':
    main(sys.argv[1:])
