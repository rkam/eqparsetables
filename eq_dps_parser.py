#!/usr/bin/env python3
"""Formats and filters GamParse spells and disc forum output."""

import sys

import argparse
import os
import dps_shims as shims
import dps_gp_reader as gpdps
import eq_game_reader as eqgr

__author__ = 'Andrew Quinn'
__copyright__ = 'Copyright 2015-2016, Andrew Quinn'
__credits__ = ['Andrew Quinn']
__license__ = 'Simplified BSD'
__version__ = '0.1'
__maintainer__ = 'Andrew Quinn'
__email__ = 'andrew@under.co.nz'
__status__ = 'Prototype'

game_readers = {}
game_readers['eq'] = eqgr

output_formatters = {}
output_formatters['tty'] = shims.TtyDPSFormatter()
output_formatters['enjin'] = shims.EnjinDPSFormatter()

def main(argv):
    dps_first = 1
    dps_last = sys.maxsize

    parser = argparse.ArgumentParser(description='Transform GamParse output into you favorite forum table format.')

    parser.add_argument('--game', help='specify the game, e.g. eq', metavar='GAME')
    parser.add_argument('-g', '--guild_roster', help='path to guild roster file', metavar='PATH')
    parser.add_argument('-r', '--raid_roster', help='path to raid roster config file', metavar='PATH')
    parser.add_argument('-o', '--owner_pet', help='path to pet-owners config file', metavar='PATH')
    parser.add_argument('-a', '--aliases', help='path to character aliases config file', metavar='PATH')
    parser.add_argument('-p', '--parsefile', help='path to GamParse output', metavar='PATH')
    parser.add_argument('-i', '--ignore', help='path to mobs-to-ignore config file', metavar='PATH')

    parser.add_argument('--dps', action='store_true', help='force dps formatting')
    parser.add_argument('--tty', action='store_true', help='output text (default is enjin post format)')
    parser.add_argument('-f', '--dpsfirst', help='highest ranking dpser to show', metavar='FIRST')
    parser.add_argument('-l', '--dpslast', help='lowest ranking dpser to show', metavar='LAST')

    parser.add_argument('--dir', help='look for files relative to dir, rather than "."', metavar='PATH')

    args = parser.parse_args()

    if not args.dps:
        print('Non dps parse not supported. Use ./eqparsetables.py');
        sys.exit(1)

    game = "eq"

    if args.dir:
        cfg_dir = args.dir
    else:
        cfg_dir = os.getcwd()

    config_files = { 'guild':      cfg_dir + '/guild_roster.txt',
                     'raid':       cfg_dir + '/raid_roster.txt',
                     'aliases':    cfg_dir + '/aliases.txt',
                     'ignore':     cfg_dir + '/mobs_blacklist.txt',
                     'pet_owners': cfg_dir + '/pet_owners.txt',
                    }
    parse_file = cfg_dir + '/parse.txt'

    if args.guild_roster:
        config_files['guild'] = args.guild_roster
    if args.raid_roster:
        config_files['raid'] = args.raid_roster
    if args.owner_pet:
        config_files['pet_owners'] = args.owner_pet
    if args.ignore:
        config_files['ignore'] = args.ignore
    if args.aliases:
        config_files['aliases'] = args.aliases
    if args.parsefile:
        parse_file = args.parsefile
    if args.game:
        game = args.game

    if args.dpsfirst:
        dps_first = int(args.dpsfirst)
        if dps_first < 1:
            dps_first = 1
    if args.dpslast:
        dps_last = int(args.dpslast)
        if dps_last < dps_first:
            dps_last = dps_first

    if not game in game_readers:
        print("Unknown game: " + game)
        sys.exit(1)

    game_reader = game_readers[game].GameReader(config_files)
    parse_reader = gpdps.GPDPSReader2(parse_file, game_reader)

    parse_tab = shims.make_dps_table(parse_reader, first=dps_first, last=dps_last)

    dest = "tty" if args.tty else "enjin"     # TODO: specify on cmdline
    fm = output_formatters[dest]
    shims.print_table_with_formatter(fm, parse_tab)

if __name__ == '__main__':
    main(sys.argv[1:])
