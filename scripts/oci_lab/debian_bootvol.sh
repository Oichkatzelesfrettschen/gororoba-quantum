#!/bin/sh
# Rebuild an E2.1.Micro on Debian without a custom image: Always Free
# tenancies hold a custom-image-count quota of 0, so the instance is
# terminated with its boot volume preserved, the volume is attached to a
# running writer instance, Debian's verified genericcloud image is written onto
# it raw, and a new instance launches from that boot volume. cloud-init's
# Oracle datasource then injects the SSH key and grows the root partition.
#
# Usage: sh debian_bootvol.sh OLD_NAME NEW_NAME SUBNET_VAR PRIVATE_IP PUBLIC(true|false) WRITER_ID WRITER_SSH
#   SUBNET_VAR names an inventory variable (SUBNET_PUBLIC_ID or SUBNET_PRIVATE_ID).
#   DEBIAN_QCOW2 points at the qcow2 already checked against Debian's SHA512SUMS.
set -eu

OCI_LAB_DIR=${OCI_LAB_DIR:-$HOME/.oci/lab}
SSH_PUB=${OCI_LAB_SSH_PUB:-$HOME/.ssh/oci_lab_ed25519.pub}
old=$1 new=$2 subnet_var=$3 ip=$4 public=$5 writer=$6 writer_ssh=$7
: "${DEBIAN_QCOW2:?}"
# shellcheck disable=SC1091
. "$OCI_LAB_DIR/inventory.env"
eval "subnet=\$$subnet_var"
TENANCY=$(sed -n 's/^tenancy=//p' "$HOME/.oci/config")
AD=$(oci iam availability-domain list --compartment-id "$TENANCY" --query 'data[0].name' --raw-output)
raw=${DEBIAN_QCOW2%.qcow2}.raw.gz
if [ ! -f "$raw" ]; then
	# qemu-img writes only to a seekable file, so the raw image is staged
	# beside the qcow2 and compressed for the transfer.
	qemu-img convert -O raw "$DEBIAN_QCOW2" "${raw%.gz}"
	gzip -1 "${raw%.gz}"
fi

inst=$(oci compute instance list --compartment-id "$TENANCY" --display-name "$old" --lifecycle-state RUNNING \
	--query 'data[0].id' --raw-output 2>/dev/null || true)
if [ -n "$inst" ]; then
	bv=$(oci compute boot-volume-attachment list --compartment-id "$TENANCY" --availability-domain "$AD" \
		--instance-id "$inst" --query 'data[0]."boot-volume-id"' --raw-output)
	oci compute instance terminate --instance-id "$inst" --preserve-boot-volume true --force \
		--wait-for-state SUCCEEDED >/dev/null
	printf 'BOOTVOL_%s=%s\n' "$(echo "$new" | tr a-z- A-Z_)" "$bv" >>"$OCI_LAB_DIR/inventory.env"
else
	bv=$(sed -n "s/^BOOTVOL_$(echo "$new" | tr a-z- A-Z_)=//p" "$OCI_LAB_DIR/inventory.env" | tail -1)
fi
[ -n "$bv" ] || { echo "no boot volume for $old" >&2; exit 1; }

att=$(oci compute volume-attachment attach --instance-id "$writer" --volume-id "$bv" --type paravirtualized \
	--wait-for-state ATTACHED --query data.id --raw-output)
# The writer sees the new paravirtualized disk as the only whole disk that
# holds no mounted partition; lsblk names it on the writer side.
ssh "$writer_ssh" 'set -eu; d=$(lsblk -dnpo NAME,TYPE | awk "\$2==\"disk\"{print \$1}" | while read -r x; do lsblk -no MOUNTPOINT "$x" | grep -q . || echo "$x"; done | head -1); [ -n "$d" ]; echo "target $d"; gzip -dc | sudo dd of="$d" bs=4M conv=fsync status=none; sudo sync' <"$raw"
oci compute volume-attachment detach --volume-attachment-id "$att" --force --wait-for-state SUCCEEDED >/dev/null

id=$(oci compute instance launch --compartment-id "$TENANCY" --availability-domain "$AD" \
	--display-name "$new" --hostname-label "$new" --shape VM.Standard.E2.1.Micro \
	--source-boot-volume-id "$bv" --subnet-id "$subnet" --private-ip "$ip" --assign-public-ip "$public" \
	--ssh-authorized-keys-file "$SSH_PUB" \
	--wait-for-state RUNNING --query data.id --raw-output)
printf '%s_ID=%s\n' "$(echo "$new" | tr a-z- A-Z_)" "$id" >>"$OCI_LAB_DIR/inventory.env"
echo "$new running"
