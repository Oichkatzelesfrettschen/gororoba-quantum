"""Cross-check of common.load_pub against n21_exact_planning.retained_registers on four runs.

Every shot and every register is compared.
"""

import common
import numpy as np

import n21_exact_planning as n21  # noqa: E402  (common puts gororoba_quantum on sys.path)


class AllNames(set[str]):
    def __contains__(self, _name: object) -> bool:
        return True


def main() -> None:
    cat = common.catalog()
    result = {}
    for run in (
        "results/live/2026-10-27T204605.871056Z",
        "results/live/2026-10-29T191606.826758Z",
        "results/live/2026-10-12T055624.091217Z",
        "results/live/2026-10-13T201757.782152Z",
    ):
        reference = n21.retained_registers(common.ROOT / run, AllNames())
        matched = total = 0
        for job in cat["jobs"]:
            if job["run"] != run:
                continue
            for pub in job["pubs"]:
                mine = common.load_pub(pub["file"])
                for name, matrix in mine["regs"].items():
                    strings = reference[mine["name"]][name]
                    flat = np.frombuffer("".join(strings).encode(), dtype=np.uint8).reshape(len(strings), -1)
                    total += 1
                    matched += int(np.array_equal(flat[:, ::-1] - 48, matrix))
        result[run] = {"registers_compared": total, "identical_to_retained_registers": matched}
    common.write_json(common.OUT / "reader_crosscheck.json", result)
    print(result)


if __name__ == "__main__":
    main()
