#!/bin/sh
# Log path, mtime and size of each export part and table as it appears; exit when every table exists or the engine exits.
set -eu
ex=$HOME/a5/exports/e8nm-p32009-n15-v9
log=$HOME/a5/engine/v9/e8nm_d4_n15.tables.log
pid=$1
seen=""
while :; do
    for f in "$ex"/qM*.c*.txt "$ex"/qM*.txt "$ex"/qG.txt "$ex"/s.txt "$ex"/qB.txt; do
        [ -e "$f" ] || continue
        case " $seen " in *" $f "*) continue ;; esac
        seen="$seen $f"
        stat -c '%n %Y %s' "$f" >> "$log"
    done
    all=1
    for k in 2 3 4 5 6 7 8 9; do [ -e "$ex/qM$k.txt" ] || all=0; done
    [ -e "$ex/qG.txt" ] || all=0
    if [ "$all" = 1 ] || ! kill -0 "$pid" 2>/dev/null; then
        echo "end $(date -u +%s) all=$all" >> "$log"
        exit 0
    fi
    sleep 30
done
