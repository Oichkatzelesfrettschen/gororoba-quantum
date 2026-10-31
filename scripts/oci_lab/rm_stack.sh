#!/bin/sh
# Capture the lab as a Resource Manager (Terraform) stack and plan it.
# Resource Discovery (stack create-from-compartment) writes Terraform for the
# live resources of the listed services together with a matching state file,
# so the stack adopts what exists rather than declaring duplicates. A plan job
# then shows the drift between that state and the tenancy; this script never
# runs an apply. Reruns plan the existing stack named lab-stack.
set -eu
OCI_LAB_DIR=${OCI_LAB_DIR:-$HOME/.oci/lab}
SERVICES=${RM_SERVICES:-'["core","bastion","database","mysql","ons","budget"]'}
TENANCY=$(awk -F= '/^tenancy/ { gsub(/ /, ""); print $2 }' "$HOME/.oci/config")
REGION=$(awk -F= '/^region/ { gsub(/ /, ""); print $2 }' "$HOME/.oci/config")
save() {
	grep -v "^$1=" "$OCI_LAB_DIR/inventory.env" >"$OCI_LAB_DIR/inventory.env.new" || true
	printf '%s=%s\n' "$1" "$2" >>"$OCI_LAB_DIR/inventory.env.new"
	mv "$OCI_LAB_DIR/inventory.env.new" "$OCI_LAB_DIR/inventory.env"
}
id=$(oci resource-manager stack list --compartment-id "$TENANCY" --display-name lab-stack \
	--lifecycle-state ACTIVE --query 'data[0].id' --raw-output 2>/dev/null || true)
if [ -z "$id" ]; then
	wr=$(oci resource-manager stack create-from-compartment --compartment-id "$TENANCY" \
		--config-source-compartment-id "$TENANCY" --config-source-region "$REGION" \
		--config-source-services-to-discover "$SERVICES" --display-name lab-stack \
		--description "Always Free lab, captured by Resource Discovery" \
		--wait-for-state SUCCEEDED --wait-for-state FAILED --max-wait-seconds 1800 \
		--query 'data.id' --raw-output)
	id=$(oci resource-manager work-request get --work-request-id "$wr" \
		--query 'data.resources[?"entity-type"==`ormstack`].identifier | [0]' --raw-output)
	# Discovery writes ignore_changes entries that index db_tools_details, which
	# the provider declares as a set of blocks; Terraform rejects an index into
	# a set, so the patched config ignores the whole block instead.
	cfg=$OCI_LAB_DIR/rm-config
	mkdir -p "$cfg/src"
	chmod 700 "$cfg"
	oci resource-manager stack get-stack-tf-config --stack-id "$id" --file "$cfg/stack.zip"
	(cd "$cfg/src" && bsdtar -xf ../stack.zip &&
		sed -i -E 's/ignore_changes = \[db_tools_details\[[^]]*\]\.name(, db_tools_details\[[0-9]+\]\.name)*\]/ignore_changes = [db_tools_details]/' ./*.tf &&
		bsdtar -a -cf ../stack-patched.zip ./*.tf)
	oci resource-manager stack update --stack-id "$id" --config-source "$cfg/stack-patched.zip" --force >/dev/null
fi
save RM_STACK_ID "$id"
job=$(oci resource-manager job create-plan-job --stack-id "$id" --display-name "lab-plan-$(date -u +%Y%m%dT%H%M%SZ)" \
	--wait-for-state SUCCEEDED --wait-for-state FAILED --max-wait-seconds 1800 --query 'data.id' --raw-output)
oci resource-manager job get-job-logs-content --job-id "$job" --query data --raw-output >"$OCI_LAB_DIR/rm-plan.log"
oci resource-manager job get --job-id "$job" --query 'data."lifecycle-state"' --raw-output
grep -E 'Plan:|No changes' "$OCI_LAB_DIR/rm-plan.log" || tail -n 20 "$OCI_LAB_DIR/rm-plan.log"
