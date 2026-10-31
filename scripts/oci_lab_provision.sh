#!/bin/sh
# Provision the OCI Always Free lab: one VCN, a public edge subnet holding the
# WireGuard and NAT micro, and a private subnet holding the A1 host and the
# second micro. Each phase finds its resources by display name before creating
# them, so a rerun creates nothing twice. OCIDs and addresses go to
# $OCI_LAB_DIR/inventory.env (mode 600) and never to stdout.
#
# Usage: sh scripts/oci_lab_provision.sh network|image|edge|route|private|a1|volume|bastion|status
set -eu

OCI_LAB_DIR=${OCI_LAB_DIR:-$HOME/.oci/lab}
INV=$OCI_LAB_DIR/inventory.env
SSH_PUB=${OCI_LAB_SSH_PUB:-$HOME/.ssh/oci_lab_ed25519.pub}
VCN_CIDR=10.42.0.0/16
PUB_CIDR=10.42.0.0/24
PRIV_CIDR=10.42.1.0/24
WG_CIDR=10.66.0.0/24
EDGE_IP=10.42.0.10
A1_IP=10.42.1.20
MICRO2_IP=10.42.1.30
# Always Free compute: A1.Flex totals 2 OCPU and 12 GB; boot volumes and the
# data volume together stay within the 200 GB block-volume grant, and
# LaunchInstance refuses a boot volume below 50 GB.
A1_OCPUS=${A1_OCPUS:-2}
A1_MEM_GB=${A1_MEM_GB:-12}
A1_BOOT_GB=50
MICRO_BOOT_GB=50
DATA_GB=50

umask 077
mkdir -p "$OCI_LAB_DIR"
touch "$INV"
# shellcheck disable=SC1090
. "$INV"

TENANCY=$(sed -n 's/^tenancy=//p' "$HOME/.oci/config")
AD=$(oci iam availability-domain list --compartment-id "$TENANCY" --query 'data[0].name' --raw-output)

save() {
	grep -v "^$1=" "$INV" >"$INV.tmp" || true
	printf '%s=%s\n' "$1" "$2" >>"$INV.tmp"
	mv "$INV.tmp" "$INV"
	eval "$1=\$2"
}

q() { oci "$@" --raw-output 2>/dev/null || true; }

by_name() { # service-list-command... --query-name NAME
	name=$1
	shift
	q "$@" --compartment-id "$TENANCY" --all \
		--query "data[?\"display-name\"=='$name' && !contains(['TERMINATED','TERMINATING'], \"lifecycle-state\")].id | [0]"
}

image_for() { # shape os version
	oci compute image list --compartment-id "$TENANCY" --shape "$1" \
		--operating-system "$2" --operating-system-version "$3" \
		--sort-by TIMECREATED --sort-order DESC --query 'data[0].id' --raw-output
}

network() {
	id=$(by_name lab-vcn network vcn list)
	[ -n "$id" ] || id=$(oci network vcn create --compartment-id "$TENANCY" \
		--display-name lab-vcn --cidr-blocks "[\"$VCN_CIDR\"]" --dns-label lab \
		--wait-for-state AVAILABLE --query data.id --raw-output)
	save VCN_ID "$id"

	id=$(q network internet-gateway list --compartment-id "$TENANCY" --vcn-id "$VCN_ID" --query 'data[0].id')
	[ -n "$id" ] || id=$(oci network internet-gateway create --compartment-id "$TENANCY" \
		--vcn-id "$VCN_ID" --display-name lab-igw --is-enabled true \
		--wait-for-state AVAILABLE --query data.id --raw-output)
	save IGW_ID "$id"

	id=$(q network route-table list --compartment-id "$TENANCY" --vcn-id "$VCN_ID" \
		--query "data[?\"display-name\"=='lab-rt-public'].id | [0]")
	[ -n "$id" ] || id=$(oci network route-table create --compartment-id "$TENANCY" \
		--vcn-id "$VCN_ID" --display-name lab-rt-public \
		--route-rules "[{\"destination\":\"0.0.0.0/0\",\"destinationType\":\"CIDR_BLOCK\",\"networkEntityId\":\"$IGW_ID\"}]" \
		--wait-for-state AVAILABLE --query data.id --raw-output)
	save RT_PUBLIC_ID "$id"

	# The private table starts empty; the route phase points it at the edge.
	id=$(q network route-table list --compartment-id "$TENANCY" --vcn-id "$VCN_ID" \
		--query "data[?\"display-name\"=='lab-rt-private'].id | [0]")
	[ -n "$id" ] || id=$(oci network route-table create --compartment-id "$TENANCY" \
		--vcn-id "$VCN_ID" --display-name lab-rt-private --route-rules '[]' \
		--wait-for-state AVAILABLE --query data.id --raw-output)
	save RT_PRIVATE_ID "$id"

	all_egress='[{"destination":"0.0.0.0/0","protocol":"all","isStateless":false}]'
	pub_in="[{\"source\":\"0.0.0.0/0\",\"protocol\":\"6\",\"tcpOptions\":{\"destinationPortRange\":{\"min\":22,\"max\":22}}},
{\"source\":\"0.0.0.0/0\",\"protocol\":\"17\",\"udpOptions\":{\"destinationPortRange\":{\"min\":51820,\"max\":51820}}},
{\"source\":\"0.0.0.0/0\",\"protocol\":\"1\",\"icmpOptions\":{\"type\":3,\"code\":4}},
{\"source\":\"$VCN_CIDR\",\"protocol\":\"all\"}]"
	priv_in="[{\"source\":\"$VCN_CIDR\",\"protocol\":\"all\"},{\"source\":\"$WG_CIDR\",\"protocol\":\"all\"}]"
	for kind in public private; do
		id=$(q network security-list list --compartment-id "$TENANCY" --vcn-id "$VCN_ID" \
			--query "data[?\"display-name\"=='lab-sl-$kind'].id | [0]")
		if [ "$kind" = public ]; then rules=$pub_in; else rules=$priv_in; fi
		[ -n "$id" ] || id=$(oci network security-list create --compartment-id "$TENANCY" \
			--vcn-id "$VCN_ID" --display-name "lab-sl-$kind" \
			--ingress-security-rules "$rules" --egress-security-rules "$all_egress" \
			--wait-for-state AVAILABLE --query data.id --raw-output)
		if [ "$kind" = public ]; then save SL_PUBLIC_ID "$id"; else save SL_PRIVATE_ID "$id"; fi
	done

	id=$(q network subnet list --compartment-id "$TENANCY" --vcn-id "$VCN_ID" \
		--query "data[?\"display-name\"=='lab-public'].id | [0]")
	[ -n "$id" ] || id=$(oci network subnet create --compartment-id "$TENANCY" \
		--vcn-id "$VCN_ID" --display-name lab-public --cidr-block "$PUB_CIDR" --dns-label pub \
		--route-table-id "$RT_PUBLIC_ID" --security-list-ids "[\"$SL_PUBLIC_ID\"]" \
		--wait-for-state AVAILABLE --query data.id --raw-output)
	save SUBNET_PUBLIC_ID "$id"

	id=$(q network subnet list --compartment-id "$TENANCY" --vcn-id "$VCN_ID" \
		--query "data[?\"display-name\"=='lab-private'].id | [0]")
	[ -n "$id" ] || id=$(oci network subnet create --compartment-id "$TENANCY" \
		--vcn-id "$VCN_ID" --display-name lab-private --cidr-block "$PRIV_CIDR" --dns-label priv \
		--route-table-id "$RT_PRIVATE_ID" --security-list-ids "[\"$SL_PRIVATE_ID\"]" \
		--prohibit-public-ip-on-vnic true \
		--wait-for-state AVAILABLE --query data.id --raw-output)
	save SUBNET_PRIVATE_ID "$id"
}

launch() { # name shape image subnet private-ip boot-gb public(true|false) [shape-config]
	id=$(by_name "$1" compute instance list)
	if [ -z "$id" ]; then
		set -- "$@" ""
		cfg=$8
		id=$(oci compute instance launch --compartment-id "$TENANCY" --availability-domain "$AD" \
			--display-name "$1" --hostname-label "$1" --shape "$2" ${cfg:+--shape-config "$cfg"} \
			--image-id "$3" --subnet-id "$4" --private-ip "$5" --boot-volume-size-in-gbs "$6" \
			--assign-public-ip "$7" --ssh-authorized-keys-file "$SSH_PUB" \
			--wait-for-state RUNNING --query data.id --raw-output) || true
	fi
	# set -e is suspended when the caller tests this function in an if, so
	# an empty id is the failure signal that every caller sees.
	[ -n "$id" ] || return 1
	printf '%s' "$id"
}

edge() {
	img=$(image_for VM.Standard.E2.1.Micro "Oracle Linux" "9 Minimal")
	id=$(launch lab-edge VM.Standard.E2.1.Micro "$img" "$SUBNET_PUBLIC_ID" "$EDGE_IP" "$MICRO_BOOT_GB" false)
	save EDGE_ID "$id"
	vnic=$(oci compute instance list-vnics --instance-id "$EDGE_ID" --query 'data[0].id' --raw-output)
	# The edge forwards traffic for other hosts, which OCI drops unless the
	# VNIC skips its source/destination check.
	oci network vnic update --vnic-id "$vnic" --skip-source-dest-check true --force >/dev/null
	pip=$(oci network private-ip list --vnic-id "$vnic" --query 'data[0].id' --raw-output)
	save EDGE_PRIVATE_IP_ID "$pip"
	rid=$(by_name lab-edge-ip network public-ip list --scope REGION --lifetime RESERVED)
	[ -n "$rid" ] || rid=$(oci network public-ip create --compartment-id "$TENANCY" \
		--lifetime RESERVED --display-name lab-edge-ip --private-ip-id "$pip" \
		--wait-for-state ASSIGNED --query data.id --raw-output)
	save EDGE_PUBLIC_IP_ID "$rid"
	save EDGE_PUBLIC_IP "$(oci network public-ip get --public-ip-id "$rid" --query 'data."ip-address"' --raw-output)"
}

route() {
	oci network route-table update --rt-id "$RT_PRIVATE_ID" --force \
		--route-rules "[{\"destination\":\"0.0.0.0/0\",\"destinationType\":\"CIDR_BLOCK\",\"networkEntityId\":\"$EDGE_PRIVATE_IP_ID\"},
{\"destination\":\"$WG_CIDR\",\"destinationType\":\"CIDR_BLOCK\",\"networkEntityId\":\"$EDGE_PRIVATE_IP_ID\"}]" \
		--wait-for-state AVAILABLE >/dev/null
}

private() {
	img=$(image_for VM.Standard.E2.1.Micro "Oracle Linux" "9 Minimal")
	id=$(launch lab-micro2 VM.Standard.E2.1.Micro "$img" "$SUBNET_PRIVATE_ID" "$MICRO2_IP" "$MICRO_BOOT_GB" false)
	save MICRO2_ID "$id"
	img=$(image_for VM.Standard.A1.Flex "Canonical Ubuntu" "26.04")
	# A plain assignment propagates a failed launch to set -e; an argument
	# substitution would save an empty id and continue.
	id=$(launch lab-a1 VM.Standard.A1.Flex "$img" "$SUBNET_PRIVATE_ID" "$A1_IP" "$A1_BOOT_GB" false \
		"{\"ocpus\":$A1_OCPUS,\"memoryInGBs\":$A1_MEM_GB}")
	save A1_ID "$id"
}

volume() {
	id=$(by_name lab-data bv volume list)
	[ -n "$id" ] || id=$(oci bv volume create --compartment-id "$TENANCY" --availability-domain "$AD" \
		--display-name lab-data --size-in-gbs "$DATA_GB" --vpus-per-gb 10 \
		--wait-for-state AVAILABLE --query data.id --raw-output)
	save DATA_VOLUME_ID "$id"
	att=$(q compute volume-attachment list --compartment-id "$TENANCY" --instance-id "$A1_ID" \
		--query "data[?\"volume-id\"=='$DATA_VOLUME_ID' && \"lifecycle-state\"=='ATTACHED'].id | [0]")
	# Paravirtualized attachment with a consistent device path gives the
	# stable name /dev/oracleoci/oraclevdb for fstab.
	[ -n "$att" ] || att=$(oci compute volume-attachment attach --instance-id "$A1_ID" \
		--volume-id "$DATA_VOLUME_ID" --type paravirtualized --device /dev/oracleoci/oraclevdb \
		--wait-for-state ATTACHED --query data.id --raw-output)
	save DATA_ATTACHMENT_ID "$att"
}

bastion() {
	id=$(q bastion bastion list --compartment-id "$TENANCY" --name lab-bastion \
		--query "data[?\"lifecycle-state\"=='ACTIVE'].id | [0]")
	[ -n "$id" ] || id=$(oci bastion bastion create --compartment-id "$TENANCY" \
		--bastion-type STANDARD --name lab-bastion --target-subnet-id "$SUBNET_PRIVATE_ID" \
		--client-cidr-list '["0.0.0.0/0"]' --wait-for-state SUCCEEDED \
		--query 'data.resources[0].identifier' --raw-output)
	save BASTION_ID "$id"
}

status() {
	oci compute instance list --compartment-id "$TENANCY" \
		--query 'data[?"lifecycle-state"!=`TERMINATED`].{name:"display-name",shape:shape,state:"lifecycle-state"}' \
		--output table
}

# image: import Debian's verified genericcloud qcow2 (DEBIAN_QCOW2, checked
# against Debian's SHA512SUMS beforehand) as a paravirtualized custom image
# for the E2.1.Micro shape, then remove the uploaded object so it stops
# counting against the 20 GB Object Storage grant.
image() {
	ns=$(oci os ns get --query data --raw-output)
	oci os bucket get --bucket-name lab-images >/dev/null 2>&1 ||
		oci os bucket create --compartment-id "$TENANCY" --name lab-images >/dev/null
	id=$(by_name lab-debian-13 compute image list)
	if [ -z "$id" ]; then
		obj=$(basename "$DEBIAN_QCOW2")
		oci os object head --bucket-name lab-images --name "$obj" >/dev/null 2>&1 ||
			oci os object put --bucket-name lab-images --file "$DEBIAN_QCOW2" --name "$obj" --force >/dev/null
		id=$(oci compute image import from-object --compartment-id "$TENANCY" --display-name lab-debian-13 \
			--namespace "$ns" --bucket-name lab-images --name "$obj" \
			--source-image-type QCOW2 --launch-mode PARAVIRTUALIZED --operating-system Debian \
			--operating-system-version 13 --query data.id --raw-output)
		# import from-object takes no --wait-for-state; image get waits instead.
		oci compute image get --image-id "$id" --wait-for-state AVAILABLE \
			--max-wait-seconds 3600 >/dev/null
		oci os object delete --bucket-name lab-images --object-name "$obj" --force
	fi
	save DEBIAN_IMAGE_ID "$id"
	oci compute image-shape-compatibility-entry add --image-id "$DEBIAN_IMAGE_ID" \
		--shape-name VM.Standard.E2.1.Micro >/dev/null
}

# a1: one A1 launch attempt; exit 75 (EX_TEMPFAIL) on "Out of host capacity".
a1() {
	img=$(image_for VM.Standard.A1.Flex "Canonical Ubuntu" "26.04")
	if id=$(launch lab-a1 VM.Standard.A1.Flex "$img" "$SUBNET_PRIVATE_ID" "$A1_IP" "$A1_BOOT_GB" false \
		"{\"ocpus\":$A1_OCPUS,\"memoryInGBs\":$A1_MEM_GB}" 2>"$OCI_LAB_DIR/a1-last.err"); then
		save A1_ID "$id"
		return 0
	fi
	grep -q 'Out of host capacity' "$OCI_LAB_DIR/a1-last.err" && exit 75
	cat "$OCI_LAB_DIR/a1-last.err" >&2
	exit 1
}

case ${1:-} in
network | image | edge | route | private | a1 | volume | bastion | status) "$1" ;;
*)
	echo "usage: $0 network|image|edge|route|private|a1|volume|bastion|status" >&2
	exit 2
	;;
esac
