#!/bin/bash

# Run the parser, grab the "can't find these chars list" (if any), and
#   compare that with all the characters listed in the Roster files, and
#   show the difference in the format of the config file.

DPS_PARSES_DIR="_eq_ra/dps_parses"

EXISTING_CHARS="_eq_ra/data/full_members.ini _eq_ra/data/applicants.ini _eq_ra/data/others.ini"
BLACKLIST_FILE="_eq_ra/data/mobs_blacklist.ini"
PETS_FILE="_eq_ra/data/pet_owners.txt"

MISSING_CHARS_FILE="$$.missing"
OUT_FILE="$$.added"

# shellcheck disable=SC2069
python3 eqparsedpstables.py "$DPS_PARSES_DIR"/* 2>&1 >/dev/null |
  grep '^	' | sed -e 's/	//' | sort -u > "$MISSING_CHARS_FILE"

trap 'rm -f $OUT_FILE $MISSING_CHARS_FILE; exit' 1 2 3 15

[[ ! -s $MISSING_CHARS_FILE ]] && echo "No one is missing." && exit 0

ROSTER_FILE=$(./bin/get_chars.sh)

fgrep -f "$MISSING_CHARS_FILE" "$ROSTER_FILE" > "$OUT_FILE"

if [[ ! -s $OUT_FILE ]]; then
  cat $OUT_FILE
  echo "Cannot find ANY missing in the rosters."
  echo "  (pet? => $PETS_FILE)."
  echo "  (mob? => $BLACKLIST_FILE)."
  cat "$MISSING_CHARS_FILE"
  exit 0
fi

# If output is to tty explain, allow for appending to config file.

if [[ -t 1 ]]; then
  echo ""
  echo "Need to hand-merge these into one of:"
  echo " $EXISTING_CHARS"
  echo "    # because of the section headers"
  echo ""
fi

cat "$OUT_FILE"
rm -f "$OUT_FILE"

exit 0
