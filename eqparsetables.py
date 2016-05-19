#!/usr/bin/env python3
"""Formats and filters GamParse spells and disc forum output."""

import sys
import argparse
import os
import gpcastreader as gpc
import tableformatter as tf
import parsedb
import castgrapher as cg

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
    config_path = cwd + '/config.ini'
    blacklist_path = cwd + '/blacklist.ini'
    default_path = cwd + '/parse.txt'
    dps_first = 1
    dps_last = sys.maxsize
    padding = '\n\n'

    parser = argparse.ArgumentParser(description='Transform GamParse output into you favorite forum table format.')
    parser.add_argument('paths', help='a list of paths containing GamParse output', nargs='*', metavar='PATHS')
    parser.add_argument('-b', '--blacklist', help='path to blacklist', metavar='PATH')
    parser.add_argument('-c', '--config', help='path to config CSV file', metavar='PATH')
    parser.add_argument('--dps', action='store_true', help='force dps formatting')
    parser.add_argument('--tty', action='store_true', help='output text (default is enjin post format)')
    parser.add_argument('-f', '--dpsfirst', help='highest ranking dpser to show', metavar='FIRST')
    parser.add_argument('-l', '--dpslast', help='lowest ranking dpser to show', metavar='LAST')

    args = parser.parse_args()

    if args.blacklist:
        blacklist_path = args.blacklist
    if args.config:
        config_path = args.config
    if args.dps:
        if args.dpsfirst:
            dps_first = int(args.dpsfirst)
            if dps_first < 1:
                dps_first = 1
        if args.dpslast:
            dps_last = int(args.dpslast)
            if dps_last < dps_first:
                dps_last = dps_first

    if args.dps:
        if args.paths:
            reader = gpc.GPDPSReader(args.paths[0], config_path)
        else:
            reader = gpc.GPDPSReader(default_path, config_path)
        if len(args.paths) > 1:
            print('Combining DPS parses is not currently supported. Ignoring input files {0}...'
                  .format(', '.join(args.paths[1:])))
        pdb = parsedb.ParseDB(reader.config, dps_reader=reader)
        dtab = pdb.get_dps_table(first=dps_first, last=dps_last)
        if args.tty:
            tf.print_table(tf.format_tty_table(dtab))
        else:
            tf.print_table(tf.format_enjin_table(dtab))
    else:
        if args.paths:
            reader = gpc.GPCastReader(args.paths[0], config_path, blacklist_path)
        else:
            reader = gpc.GPCastReader(default_path, config_path, blacklist_path)
        pdb = parsedb.ParseDB(reader.config, caster_dod=reader.caster_dod)
        if len(args.paths) > 1:
            for path in args.paths[1:]:
                reader = gpc.GPCastReader(path, config_path, blacklist_path)
                pdb.update_cast_parse(reader.caster_dod)
        if args.tty:
            for i, eq_class in enumerate(sorted(reader.classes)):
                if i:
                    print(padding)
                ptab = pdb.get_cast_table(eq_class)
                tf.print_table(tf.format_tty_table(ptab))
        else:
            for i, eq_class in enumerate(sorted(reader.classes)):
                if i:
                    print(padding)
                ptab = pdb.get_cast_table(eq_class)
                cg.generate_class_graphs(ptab)
                tf.print_table(tf.format_enjin_table(ptab))


if __name__ == '__main__':
    main(sys.argv[1:])
