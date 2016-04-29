#!/usr/bin/env python3
"""Formats and filters GamParse spells and disc forum output."""

import sys
import getopt
import sqlite3
import os
import gpcastreader as gpc
# import enjinprinter as ep

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
    spells_cast_by_class = reader.get_spells_cast_by_class()

    # setup db connection
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()

    # populate db
    # ep.create_class_tables(cur, spells_cast_by_class, reader.classes)
    # ep.populate_class_tables(cur, caster_dod, cfg)

    # print it out
    # ep.print_tables_enjin(cur, spells_cast_by_class, reader.classes)

    # clean up db connection
    cur.close()
    conn.close()


if __name__ == '__main__':
    main(sys.argv[1:])