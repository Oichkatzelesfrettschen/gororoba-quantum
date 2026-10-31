"""Run a shell command on a lab instance through the OCI Run Command REST API.

The Oracle Cloud Agent's Run Command plugin polls the service, so this path
works when SSH and WireGuard are down, as long as the instance reaches OCI.
The lab-instances dynamic group and the lab-instance-agent policy grant the
agent use of instance-agent-command-execution-family. Output returns inline
(TEXT), capped by the service at 1 MB.

Usage: $PYTHON scripts/oci_lab/run_command.py INSTANCE_DISPLAY_NAME 'COMMAND' [TIMEOUT_SECONDS]
"""

from __future__ import annotations

import sys
import time

import oci


def main(name: str, command: str, timeout: int = 300) -> int:
    config = oci.config.from_file()
    tenancy = config["tenancy"]
    compute = oci.core.ComputeClient(config)
    instances = [i for i in compute.list_instances(tenancy, display_name=name).data if i.lifecycle_state == "RUNNING"]
    if not instances:
        raise SystemExit(f"no RUNNING instance named {name}")
    agent = oci.compute_instance_agent.ComputeInstanceAgentClient(config)
    models = oci.compute_instance_agent.models
    cmd = agent.create_instance_agent_command(
        models.CreateInstanceAgentCommandDetails(
            compartment_id=tenancy,
            display_name=f"lab-{int(time.time())}",
            execution_time_out_in_seconds=timeout,
            target=models.InstanceAgentCommandTarget(instance_id=instances[0].id),
            content=models.InstanceAgentCommandContent(
                source=models.InstanceAgentCommandSourceViaTextDetails(source_type="TEXT", text=command),
                output=models.InstanceAgentCommandOutputViaTextDetails(output_type="TEXT"),
            ),
        )
    ).data
    deadline = time.monotonic() + timeout + 120
    while time.monotonic() < deadline:
        ex = agent.get_instance_agent_command_execution(cmd.id, instances[0].id).data
        if ex.lifecycle_state in ("SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELED"):
            out = ex.content
            print(getattr(out, "text", "") or "", end="")
            print(f"[run-command {ex.lifecycle_state} exit={getattr(out, 'exit_code', None)}]", file=sys.stderr)
            return int(getattr(out, "exit_code", 1) or 0) if ex.lifecycle_state == "SUCCEEDED" else 1
        time.sleep(10)
    print("[run-command not picked up before the deadline]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 300))
