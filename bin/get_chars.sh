#!/bin/bash

# Extract all players and their class from RaidRoster dumps

ROSTERS_DIR="./_eq_ra/roster"

OUTFILE="all_players_$(date +'%y%m%d')"

# the != 50 excludes Vox runs

# shellcheck disable=SC2016
grep -h '^[0-9]' $ROSTERS_DIR/Raid*.txt |
  bin/raid_to_ini.rb |
  sort -u -t, -k2,3 > "$OUTFILE"

ls "$OUTFILE"

