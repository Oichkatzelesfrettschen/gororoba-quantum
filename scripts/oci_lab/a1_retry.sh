#!/bin/sh
# Retry the A1 launch every 30 minutes for at most 96 attempts (48 hours),
# stopping on the first success or on any error other than "Out of host
# capacity". Runs in tmux; progress lines go to $OCI_LAB_DIR/a1-retry.log.
set -eu
here=$(dirname "$0")
OCI_LAB_DIR=${OCI_LAB_DIR:-$HOME/.oci/lab}
log=$OCI_LAB_DIR/a1-retry.log
n=0
while [ "$n" -lt 96 ]; do
	n=$((n + 1))
	rc=0
	sh "$here/../oci_lab_provision.sh" a1 >/dev/null 2>>"$log" || rc=$?
	printf '%s attempt %d rc=%d\n' "$(date -u +%FT%TZ)" "$n" "$rc" >>"$log"
	case $rc in
	0) msg="lab-a1 launched on attempt $n" ;;
	75) sleep 1800; continue ;;
	*) msg="lab-a1 launch stopped: error rc=$rc on attempt $n (see $log)" ;;
	esac
	echo "$msg" >>"$log"
	command -v notify-send >/dev/null && notify-send "OCI lab" "$msg"
	exit "$rc"
done
echo "lab-a1: no capacity after $n attempts" >>"$log"
command -v notify-send >/dev/null && notify-send "OCI lab" "lab-a1: no capacity after $n attempts"
exit 75
