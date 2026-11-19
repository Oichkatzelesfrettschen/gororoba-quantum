#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
snapshot=$(pwd)
terminal=docs/local/windows-full.done
trap 'status=$?; printf "%s\n" "$status" > "$terminal"' EXIT
for slug in e8-nm e8-np; do
    for mode in write check; do
        case "$mode" in write) deadline=1500 ;; check) deadline=300 ;; esac
        unit="e8-closure-$slug-$mode-666b0a074.service"
        log="$snapshot/docs/local/windows-full-$slug-$mode.log"
        if systemd-run --user --unit="$unit" --wait --property="RuntimeMaxSec=$deadline" \
            --property=KillMode=control-group --property=TimeoutStopSec=10 \
            --property="StandardOutput=append:$log" --property="StandardError=append:$log" \
            --working-directory="$snapshot" /bin/sh "$snapshot/docs/local/closure-windows-service.sh" \
            "$slug" "$mode" "$unit"; then
            status=0
        else
            status=$?
        fi
        if systemctl --user show "$unit" --property=Result --property=ExecMainCode --property=ExecMainStatus \
            --property=ActiveState --property=SubState --property=RuntimeMaxUSec --property=MemoryMax \
            --property=MemorySwapMax --property=MemoryHigh --property=KillMode --property=TimeoutStopUSec \
            > "docs/local/windows-full-$slug-$mode-unit-status.txt"; then
            :
        else
            printf 'The completed transient unit has unloaded; systemd-run terminal status=%s\n' "$status" \
                >> "docs/local/windows-full-$slug-$mode-unit-status.txt"
        fi
        printf '%s\n' "$status" > "docs/local/windows-full-$slug-$mode.done"
        printf 'STAGE_TERMINAL slug=%s mode=%s status=%s\n' "$slug" "$mode" "$status"
        test "$status" -eq 0 || exit "$status"
    done
done
