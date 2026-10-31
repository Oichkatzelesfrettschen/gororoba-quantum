"""Report whether the home availability domain can place a VM.Standard.A1.Flex shape.

CreateComputeCapacityReport is a read-only placement query that creates no
resource and carries no charge, so it can poll far more often than a launch.
Exit status 0 means some fault domain reports AVAILABLE for the requested
shape, 75 (EX_TEMPFAIL) means none does.

Usage: $PYTHON scripts/oci_lab/a1_capacity.py OCPUS MEMORY_GB
"""

from __future__ import annotations

import sys

import oci


def main(ocpus: float, memory_gb: float) -> int:
    config = oci.config.from_file()
    tenancy = config["tenancy"]
    ad = oci.identity.IdentityClient(config).list_availability_domains(tenancy).data[0].name
    compute = oci.core.ComputeClient(config)
    m = oci.core.models
    shape = m.CapacityReportInstanceShapeConfig(ocpus=ocpus, memory_in_gbs=memory_gb)
    rc = 75
    for fd in ("FAULT-DOMAIN-1", "FAULT-DOMAIN-2", "FAULT-DOMAIN-3"):
        report = compute.create_compute_capacity_report(
            m.CreateComputeCapacityReportDetails(
                compartment_id=tenancy,
                availability_domain=ad,
                shape_availabilities=[
                    m.CreateCapacityReportShapeAvailabilityDetails(
                        instance_shape="VM.Standard.A1.Flex", fault_domain=fd, instance_shape_config=shape
                    )
                ],
            )
        ).data
        status = report.shape_availabilities[0].availability_status
        print(fd, status)
        if status == "AVAILABLE":
            rc = 0
    return rc


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    sys.exit(main(float(sys.argv[1]), float(sys.argv[2])))
