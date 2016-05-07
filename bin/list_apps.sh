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

if [[ $PROG == "list_members.sh" ]]; then
  GREP_WANT_APPS="-v"
  RUBY_WANT_APPS=
else
  GREP_WANT_APPS=
  RUBY_WANT_APPS="-a"
fi

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

grep -h $GREP_WANT_APPS 'Applicant' "$ROSTER_FILE" |
  bin/guild_to_ini.rb $RUBY_WANT_APPS |
  sort -u -t, -k2,3 > "$OUTFILE"

if [[ $DPS_APPS -ne 0 ]]; then
  bin/dps_from_ini.rb "$OUTFILE"
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
