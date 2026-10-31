"""Create the lab's Always Free MySQL HeatWave DB system and its HeatWave cluster.

The DB system takes the MySQL.Free shape with 50 GB of storage on the
private subnet (10.42.1.40), so only the VCN and WireGuard peers reach port
3306; the HeatWave cluster takes the HeatWave.Free shape with one node. The
admin password is generated into $OCI_LAB_DIR/mysql-lab-mysql.admin (mode
600) and reaches the service only in the request body. Reruns reuse an
existing DB system of the same display name.

Usage: $PYTHON scripts/oci_lab/mysql_create.py
"""

from __future__ import annotations

import oci
from adb_create import LAB_DIR, password

NAME = "lab-mysql"
PRIVATE_IP = "10.42.1.40"


def inventory(key: str) -> str:
    for line in (LAB_DIR / "inventory.env").read_text().splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1]
    raise SystemExit(f"{key} missing from inventory.env")


def main() -> None:
    config = oci.config.from_file()
    tenancy = config["tenancy"]
    ad = oci.identity.IdentityClient(config).list_availability_domains(tenancy).data[0].name
    mysql = oci.mysql.DbSystemClient(config)
    existing = [
        d
        for d in mysql.list_db_systems(tenancy, display_name=NAME).data
        if d.lifecycle_state not in ("DELETED", "DELETING")
    ]
    if existing:
        db = mysql.get_db_system(existing[0].id).data
    else:
        secret = LAB_DIR / f"mysql-{NAME}.admin"
        if not secret.exists():
            secret.touch(mode=0o600)
            # MySQL requires a special character; password() supplies letters, digits and #_-.
            secret.write_text(password() + "#9a")
        db = mysql.create_db_system(
            oci.mysql.models.CreateDbSystemDetails(
                compartment_id=tenancy,
                display_name=NAME,
                availability_domain=ad,
                shape_name="MySQL.Free",
                subnet_id=inventory("SUBNET_PRIVATE_ID"),
                ip_address=PRIVATE_IP,
                admin_username="labadmin",
                admin_password=secret.read_text().strip(),
                data_storage_size_in_gbs=50,
                is_highly_available=False,
            )
        ).data
    db = oci.wait_until(
        mysql, mysql.get_db_system(db.id), "lifecycle_state", "ACTIVE", max_wait_seconds=3600, max_interval_seconds=60
    ).data
    print(NAME, db.lifecycle_state, db.mysql_version, db.shape_name)
    if not db.is_heat_wave_cluster_attached:
        mysql.add_heat_wave_cluster(
            db.id, oci.mysql.models.AddHeatWaveClusterDetails(shape_name="HeatWave.Free", cluster_size=1)
        )
        db = oci.wait_until(
            mysql,
            mysql.get_db_system(db.id),
            "is_heat_wave_cluster_attached",
            True,
            max_wait_seconds=3600,
            max_interval_seconds=60,
        ).data
    cluster = mysql.get_heat_wave_cluster(db.id).data
    print("heatwave", cluster.lifecycle_state, cluster.shape_name, cluster.cluster_size)
    with (LAB_DIR / "inventory.env").open("a") as inv:
        inv.write(f"MYSQL_ID={db.id}\n")


if __name__ == "__main__":
    main()
