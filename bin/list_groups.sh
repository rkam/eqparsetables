#!/usr/bin/env bash

GUILD_ROSTER_DIR="./_eq_ra/guild"

OUTFILE="raid_by_groups_$(date +'%y%m%d')"

# TODO: should auto find just latest file..

# shellcheck disable=SC2086
#PROG="$(basename $0)"

ROSTER_FILE="$1"
if [[ ! -f "$ROSTER_FILE" ]]; then
  ROSTER_FILE="$GUILD_ROSTER_DIR/$ROSTER"
  if [[ ! -f "$ROSTER_FILE" ]]; then
    echo "Can't find roster file: $ROSTER_FILE"
    exit 1
  fi
fi

sort -n "$ROSTER_FILE" | bin/group_makeup.rb > "$OUTFILE"

ls "$OUTFILE"
