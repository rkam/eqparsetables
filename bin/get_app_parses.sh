#!/usr/bin/env bash

FILE="_eq_ra/guild/Reckless Ascension-20160503-153045.txt"
EVENTS_DIR="_eq_ra/dps_results"

OUT_DIR="app_perfs"
MAX_COMPARE_MEMBERS=15

declare -A APPS_BY_CLASS
declare -A MEMBERS_BY_CLASS

function make_egrep_list {
  local IFS='|'
  echo "($*)"
}

get_guild_members()
{
  if [[ $1 == "apps" ]]; then
    MEMBERS=$(bin/list_apps.sh    --dps "$FILE" | cut -d, -f 1 -f 2)
  else
    MEMBERS=$(bin/list_members.sh --dps "$FILE" | cut -d, -f 1 -f 2)
  fi

  for i in $MEMBERS
  do
    IFS="," read -r -a PARTS <<< "$i"

    CHAR="${PARTS[0]}"
    CLS="${PARTS[1]}"

    if [[ $1 == "apps" ]]; then
      OLD="${APPS_BY_CLASS[$CLS]}"

      [[ -z "$OLD" ]] && APPS_BY_CLASS[$CLS]="$CHAR"      && continue
                         APPS_BY_CLASS[$CLS]="$OLD $CHAR"
    else
      OLD="${MEMBERS_BY_CLASS[$CLS]}"

      [[ -z "$OLD" ]] && MEMBERS_BY_CLASS[$CLS]="$CHAR"      && continue
                         MEMBERS_BY_CLASS[$CLS]="$OLD $CHAR"
    fi

  done

}

get_guild_members "apps"
get_guild_members "full_members"

[[ -d $OUT_DIR ]] || mkdir "$OUT_DIR"

for f in $EVENTS_DIR/*
do
  echo "$f"

  for CLS in ${!APPS_BY_CLASS[*]}
  do
    echo " $CLS"

    # shellcheck disable=SC2086
    BASE=$(basename $f)               # keeps .txt
    OUT_FILE="$OUT_DIR/${CLS}_$BASE"
#    OUT_FILE="/dev/stdout"

    NEED_HEADER=1
    for APP in ${APPS_BY_CLASS[$CLS]}
    do
      echo "  $APP"

      LINE=$(fgrep "$APP" "$f")

      [[ $? -ne 0 ]] && continue

      if [[ $NEED_HEADER -eq 1 ]]; then
        NEED_HEADER=0
        {
          TITLE=$(sed -ne 2p "$f")
          TOTAL=$(fgrep "Total" "$f")
          echo "$TITLE" >> "$OUT_FILE"
          echo "$TOTAL" >> "$OUT_FILE"

        } >> "$OUT_FILE"
      fi

      echo "$LINE" >> "$OUT_FILE"

    done

    # If the app was sent to the file, then add members for comparison
    if [[ $NEED_HEADER -eq 0 ]]; then

      echo -e "\nOther $CLS for comparion\n" >> "$OUT_FILE"

      # shellcheck disable=SC2086
      ALL=$(make_egrep_list ${MEMBERS_BY_CLASS[$CLS]})

      egrep "$ALL" "$f" >> "$OUT_FILE"

      echo -e "\nParse top $MAX_COMPARE_MEMBERS for comparion\n" >> "$OUT_FILE"

      # shellcheck disable=SC2086
      ALL=$(make_egrep_list ${MEMBERS_BY_CLASS[*]})
      egrep "$ALL" "$f" | head -$MAX_COMPARE_MEMBERS >> "$OUT_FILE"
    fi
  done
done

FILES=$(ls ./"$OUT_DIR" 2>/dev/null)
[[ $? ]] && echo "$FILES"

rmdir "$OUT_DIR" > /dev/null 2>&1       # in case we created it and nop

