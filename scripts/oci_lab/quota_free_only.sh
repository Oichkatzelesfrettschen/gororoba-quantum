#!/bin/sh
# Hold the tenancy to its Always Free allowances with a quota policy.
# A quota refuses a create or resize that exceeds it before anything bills,
# which a budget (alert-only) cannot do. Statements are evaluated in order and
# a later statement on the same quota supersedes an earlier one, so each
# family (compute shapes, compute-core, compute-memory and the services) is zeroed first and its free allowance set after. MySQL publishes
# no quota names, so mysql_create.py's MySQL.Free shape is its only guard.
# A1_QUOTA_OCPUS / A1_QUOTA_MEM_GB raise the A1 ceiling once a free allowance
# above 2 OCPU / 12 GB is confirmed. Reruns update the policy lab-free-only.
set -eu
A1_QUOTA_OCPUS=${A1_QUOTA_OCPUS:-2}
A1_QUOTA_MEM_GB=${A1_QUOTA_MEM_GB:-12}
TENANCY=$(awk -F= '/^tenancy/ { gsub(/ /, ""); print $2 }' "$HOME/.oci/config")
statements=$(
	cat <<JSON
[
"zero compute quotas in tenancy",
"zero compute-core quotas in tenancy",
"zero compute-memory quotas in tenancy",
"set compute-core quota standard-a1-core-count to $A1_QUOTA_OCPUS in tenancy",
"set compute-core quota standard-a1-core-regional-count to $A1_QUOTA_OCPUS in tenancy",
"set compute-memory quota standard-a1-memory-count to $A1_QUOTA_MEM_GB in tenancy",
"set compute-memory quota standard-a1-memory-regional-count to $A1_QUOTA_MEM_GB in tenancy",
"set compute-core quota standard-e2-micro-core-count to 2 in tenancy",
"set compute quota vm-standard-e2-1-micro-count to 2 in tenancy",
"zero block-storage quotas in tenancy",
"set block-storage quota total-storage-gb to 200 in tenancy",
"set block-storage quota volume-count to 4 in tenancy",
"set block-storage quota backup-count to 5 in tenancy",
"zero database quotas in tenancy",
"set database quota adb-free-count to 2 in tenancy",
"zero load-balancer quotas in tenancy",
"set load-balancer quota lb-flexible-count to 1 in tenancy",
"set load-balancer quota lb-flexible-bandwidth-sum to 10 in tenancy",
"set object-storage quota storage-bytes to 21474836480 in tenancy",
"zero big-data quotas in tenancy",
"zero data-science quotas in tenancy",
"zero ocvp quotas in tenancy",
"zero goldengate quotas in tenancy",
"zero postgresql quotas in tenancy",
"zero redis quotas in tenancy",
"zero oci-kafka quotas in tenancy",
"zero open-search quotas in tenancy",
"zero data-flow quotas in tenancy",
"zero filesystem quotas in tenancy",
"zero network-firewall quotas in tenancy",
"zero analytics quotas in tenancy",
"zero integration quotas in tenancy",
"zero container-engine quotas in tenancy"
]
JSON
)
id=$(oci limits quota list --compartment-id "$TENANCY" --name lab-free-only \
	--query 'data[0].id' --raw-output 2>/dev/null || true)
if [ -z "$id" ]; then
	oci limits quota create --compartment-id "$TENANCY" --name lab-free-only \
		--description "Always Free allowances only" --statements "$statements" \
		--query 'data."lifecycle-state"' --raw-output
else
	oci limits quota update --quota-id "$id" --statements "$statements" --force \
		--query 'data."lifecycle-state"' --raw-output
fi
