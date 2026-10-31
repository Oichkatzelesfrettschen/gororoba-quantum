#!/bin/sh
# Launch the lab's A1 hosts once the home availability domain has capacity.
# The free capacity report (a1_capacity.py) polls every 5 minutes for up to
# 48 hours; a launch runs only when it reports AVAILABLE, and a launch that
# still loses the race returns to polling. A1_HOSTS lists name:private-ip
# pairs, each launched with A1_OCPUS and A1_MEM_GB; the default pair splits
# the tenancy's 2 OCPU / 12 GB A1 allowance into two
# 1 OCPU / 6 GB hosts. Progress lines go to $OCI_LAB_DIR/a1-retry.log.
set -eu
here=$(dirname "$0")
PYTHON=${PYTHON:-python3}
OCI_LAB_DIR=${OCI_LAB_DIR:-$HOME/.oci/lab}
A1_OCPUS=${A1_OCPUS:-1}
A1_MEM_GB=${A1_MEM_GB:-6}
A1_HOSTS=${A1_HOSTS:-lab-a1:10.42.1.20 lab-a1b:10.42.1.21}
export A1_OCPUS A1_MEM_GB
log=$OCI_LAB_DIR/a1-retry.log
say() {
	printf '%s %s\n' "$(date -u +%FT%TZ)" "$1" >>"$log"
	if command -v notify-send >/dev/null; then notify-send "OCI lab" "$1"; fi
}
n=0
while [ "$n" -lt 576 ]; do
	n=$((n + 1))
	if "$PYTHON" -I "$here/a1_capacity.py" "$A1_OCPUS" "$A1_MEM_GB" >/dev/null 2>>"$log"; then
		pending=0
		for host in $A1_HOSTS; do
			rc=0
			A1_NAME=${host%%:*} A1_IP=${host#*:} sh "$here/../oci_lab_provision.sh" a1 >/dev/null 2>>"$log" || rc=$?
			printf '%s poll %d launch %s rc=%d\n' "$(date -u +%FT%TZ)" "$n" "${host%%:*}" "$rc" >>"$log"
			case $rc in
			0) ;;
			75) pending=1 ;;
			*)
				say "A1 launch of ${host%%:*} stopped: rc=$rc (see $log)"
				exit "$rc"
				;;
			esac
		done
		if [ "$pending" -eq 0 ]; then
			say "A1 hosts launched: $A1_HOSTS"
			exit 0
		fi
	fi
	sleep 300
done
say "A1: no capacity after $n polls"
exit 75
