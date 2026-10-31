#!/bin/sh
# Report when the Pay As You Go upgrade reaches the service limits. A Free
# Tier tenancy carries a 0 service limit on paid compute shapes
# (standard-e4-core-count); the upgrade raises it, and the A1 service limit
# then shows the free allowance the paid account holds. Polls every 30 minutes
# for up to 72 hours and writes each reading to $OCI_LAB_DIR/payg-watch.log.
set -eu
OCI_LAB_DIR=${OCI_LAB_DIR:-$HOME/.oci/lab}
TENANCY=$(awk -F= '/^tenancy/ { gsub(/ /, ""); print $2 }' "$HOME/.oci/config")
log=$OCI_LAB_DIR/payg-watch.log
limit() {
	oci limits value list --compartment-id "$TENANCY" --service-name compute --name "$1" \
		--query 'max(data[].value)' --raw-output
}
n=0
while [ "$n" -lt 144 ]; do
	n=$((n + 1))
	e4=$(limit standard-e4-core-count || echo error)
	a1=$(limit standard-a1-core-count || echo error)
	a1m=$(limit standard-a1-memory-count || echo error)
	printf '%s e4=%s a1_cores=%s a1_mem_gb=%s\n' "$(date -u +%FT%TZ)" "$e4" "$a1" "$a1m" >>"$log"
	case $e4 in
	0 | error) sleep 1800 ;;
	*)
		msg="PAYG active: A1 service limit ${a1} OCPU / ${a1m} GB"
		echo "$msg" >>"$log"
		if command -v notify-send >/dev/null; then notify-send "OCI lab" "$msg"; fi
		exit 0
		;;
	esac
done
exit 75
