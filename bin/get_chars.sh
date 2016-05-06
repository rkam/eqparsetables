#!/bin/bash

# Extract all players and their class from RaidRoster dumps

ROSTERS_DIR="./_eq_ra/roster"

OUTFILE="all_players_$(date +'%y%m%d')"

# the != 50 excludes Vox runs

# shellcheck disable=SC2016
grep -h '^[0-9]' $ROSTERS_DIR/Raid*.txt |
  ruby -n -e '
  a = $_.split("\t")

  next if a[2] == "50"

  long = [  "Bard", "Beastlord", "Berserker", "Cleric", "Druid",
            "Enchanter", "Magician", "Monk", "Necromancer", "Paladin",
            "Ranger", "Rogue", "Shadow Knight", "Shaman", "Warrior", "Wizard" ]

  short = %w[ BRD BST BER CLR DRU ENC MAG MNK NEC PAL RNG ROG SHD SHA WAR WIZ ]

  i = long.find_index(a[3])

  print("#{a[1]},#{short[i]},#{a[1]}\n")
' |
  sort -u -t, -k2,3 > "$OUTFILE"

ls "$OUTFILE"

