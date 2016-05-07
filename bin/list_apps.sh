#!/bin/bash

# Extract all players and their class from RaidRoster dumps

GUILD_ROSTER_DIR="./_eq_ra/guild"

OUTFILE="apps_$(date +'%y%m%d')"

# TODO: should auto find just latest file..

# shellcheck disable=SC2086
PROG="$(basename $0)"

[[ $# -eq 0 ]] && echo "Usage: $PROG -verbose -dps guild_roster_file" && exit 1

VERBOSE=0
DPS_APPS=0

WANT_APPS=
[[ $PROG == "list_members.sh" ]] && WANT_APPS="-v"

# TRIVIAL: order matters, etc.
[[ $# -gt 0 && $1 =~ -v ]] && VERBOSE=1 && shift
[[ $# -gt 0 && $1 =~ -d ]] && DPS_APPS=1 && shift   # -d -dps   --dps,   etc.

ROSTER_FILE="$1"
if [[ ! -f "$ROSTER_FILE" ]]; then
  ROSTER_FILE="$GUILD_ROSTER_DIR/$ROSTER"
  if [[ ! -f "$ROSTER_FILE" ]]; then
    echo "Can't find roster file: $ROSTER_FILE"
    exit 1
  fi
fi

grep -h $WANT_APPS 'Applicant' "$ROSTER_FILE" |
  ruby -n -e '
  a = $_.chomp.split("\t")

  next if a[1] == "50"      # shouldnt happen

  app_date = a[-1].split(" ")[-1]

  long = [  "Bard", "Beastlord", "Berserker", "Cleric", "Druid",
            "Enchanter", "Magician", "Monk", "Necromancer", "Paladin",
            "Ranger", "Rogue", "Shadow Knight", "Shaman", "Warrior", "Wizard" ]

  short = %w[ BRD BST BER CLR DRU ENC MAG MNK NEC PAL RNG ROG SHD SHA WAR WIZ ]

  i = long.find_index(a[2])

  print("#{a[0]},#{short[i]},#{a[0]}\t# #{app_date}\n")
' |
  sort -u -t, -k2,3 > "$OUTFILE"

if [[ $DPS_APPS -ne 0 ]]; then
  < "$OUTFILE" ruby -n -e '
    dps = %w[ BRD BST BER ENC MAG MNK NEC RNG ROG WIZ ]
    puts $_ if dps.find_index($_.split(",")[1])
  '
else
  cat "$OUTFILE"
fi


rm "$OUTFILE"

[[ $VERBOSE -eq 0 ]] && exit 0

echo ""
echo "TODO:"
echo "convert list_of_apps to 'class' => [ "app1", "app2", ... ]  "
echo "for class in list "
echo "    for hmm_dates for app "
echo "        highlight app in part between those dates"
echo ""
echo "well, something like that.."
echo ""
