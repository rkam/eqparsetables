#!/bin/bash

# Run the parser, grab the "can't find these chars list" (if any), and
#   compare that with all the characters listed in the Roster files, and
#   show the difference in the format of the config file.

DPS_PARSES_DIR="_dps_parses"

EXISTING_CHARS="_data/config.ini"
BLACKLIST_FILE="_data/mobs_blacklist.ini"

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
  echo "Cannot find ANY missing in the rosters (pet? mob? => $BLACKLIST_FILE)."
  cat "$MISSING_CHARS_FILE"
  exit 1
fi

# If output is to tty explain, otherwise probably appending to $EXISTING_CHARS

if [[ -t 1 ]]; then
  echo ""
  echo "Need to hand-merge these into $EXISTING_CHARS"
  echo "    # because of the section headers"
  echo ""
fi

cat "$OUT_FILE"
rm "$OUT_FILE"
