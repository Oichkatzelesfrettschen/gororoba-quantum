"""Create the lab's two Always Free Autonomous Databases with OML notebooks.

Each database is 23ai, 1 OCPU and 20 GB (the Always Free shape, which the
service fixes), with a public endpoint restricted by an access-control list
to the operator's address and the lab edge, and mutual TLS required. The
ADMIN password is generated here into $OCI_LAB_DIR/adb-<name>.admin (mode
600) and reaches the service only in the request body. Reruns reuse an
existing database of the same display name.

Usage: $PYTHON scripts/oci_lab/adb_create.py OPERATOR_IP [OPERATOR_IP...]
"""

from __future__ import annotations

import os
import secrets
import string
import sys
from pathlib import Path

import oci

LAB_DIR = Path(os.environ.get("OCI_LAB_DIR", Path.home() / ".oci" / "lab"))
# Display name, database name (letters and digits, 30 at most), workload.
DATABASES = (("lab-adb-dw", "labdw", "DW"), ("lab-adb-oltp", "laboltp", "OLTP"))


def password() -> str:
    """Return a password the service accepts: 12-30 characters with an upper, lower and digit, no double quote."""
    alphabet = string.ascii_letters + string.digits + "#_-"
    while True:
        p = "".join(secrets.choice(alphabet) for _ in range(24))
        if any(c.isupper() for c in p) and any(c.islower() for c in p) and any(c.isdigit() for c in p):
            return p


def inventory_edge_ip() -> str:
    for line in (LAB_DIR / "inventory.env").read_text().splitlines():
        if line.startswith("EDGE_PUBLIC_IP="):
            return line.split("=", 1)[1]
    raise SystemExit("EDGE_PUBLIC_IP missing from inventory.env")


def main(operator_ips: list[str]) -> None:
    if not operator_ips:
        raise SystemExit(__doc__)
    config = oci.config.from_file()
    tenancy = config["tenancy"]
    db = oci.database.DatabaseClient(config)
    acl = sorted(set(operator_ips) | {inventory_edge_ip()})
    existing = {
        d.display_name: d
        for d in oci.pagination.list_call_get_all_results(db.list_autonomous_databases, tenancy).data
        if d.lifecycle_state not in ("TERMINATED", "TERMINATING")
    }
    for display, name, workload in DATABASES:
        if display in existing:
            print(f"{display}: exists, {existing[display].lifecycle_state}")
            continue
        secret = LAB_DIR / f"adb-{display}.admin"
        if not secret.exists():
            secret.touch(mode=0o600)
            secret.write_text(password())
        details = oci.database.models.CreateAutonomousDatabaseDetails(
            compartment_id=tenancy,
            display_name=display,
            db_name=name,
            db_workload=workload,
            db_version="23ai",
            is_free_tier=True,
            admin_password=secret.read_text().strip(),
            whitelisted_ips=acl,
            is_mtls_connection_required=True,
        )
        created = db.create_autonomous_database(details).data
        oci.wait_until(
            db, db.get_autonomous_database(created.id), "lifecycle_state", "AVAILABLE", max_wait_seconds=1800
        )
        with (LAB_DIR / "inventory.env").open("a") as inv:
            inv.write(f"ADB_{workload}_ID={created.id}\n")
        print(f"{display}: AVAILABLE")


if __name__ == "__main__":
    main(sys.argv[1:])
