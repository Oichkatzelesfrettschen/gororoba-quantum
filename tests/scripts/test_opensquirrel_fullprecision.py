"""Bound the precision exporter to supported IR and binary64 round trips."""

import math
import sys

import pytest
from opensquirrel_fullprecision import float_literal

from qi_stack import probe, run


@pytest.mark.parametrize(
    "value", [0.0, -0.0, math.pi, -math.pi / 2, math.nextafter(1.0, 2.0), sys.float_info.max, 5e-324]
)
def test_binary64_float_literal_round_trips(value: float) -> None:
    if float(float_literal(value)).hex() != value.hex():
        raise RuntimeError("cQASM angle serialization must round-trip binary64")


@pytest.mark.parametrize("value", [math.inf, -math.inf, math.nan])
def test_nonfinite_angle_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        float_literal(value)


def test_public_ir_export_rejects_unsupported_statement() -> None:
    if not probe().available:
        pytest.skip("pinned Quantum Inspire stack unavailable")
    output = run(
        [
            "-c",
            "import sys; sys.path.insert(0, 'scripts')\n"
            "from opensquirrel import Circuit\n"
            "from opensquirrel_fullprecision import export_circuit\n"
            "circuit = Circuit.from_string('version 3.0\\nqubit[1] q\\nbit[1] b\\nH q[0]')\n"
            "try:\n"
            " export_circuit(circuit)\n"
            "except ValueError as error:\n"
            " print(error)\n"
            "else:\n"
            " raise RuntimeError('unsupported H silently exported')\n",
        ]
    )
    if "unsupported IR statement: H" not in output:
        raise RuntimeError(f"unsupported IR must fail closed: {output}")


def test_ir_float_export_round_trip_and_measurement_mapping() -> None:
    if not probe().available:
        pytest.skip("pinned Quantum Inspire stack unavailable")
    output = run(
        [
            "-c",
            "import sys; sys.path.insert(0, 'scripts')\n"
            "from opensquirrel import Circuit\n"
            "from opensquirrel_fullprecision import export_circuit\n"
            "text = 'version 3.0\\nqubit[2] q\\nbit[2] b\\nRy(-1.5707963267948966) q[0]\\nb[1] = measure q[0]'\n"
            "source = Circuit.from_string(text)\n"
            "serialized = export_circuit(source)\n"
            "parsed = Circuit.from_string(serialized)\n"
            "if source.ir.statements[0].bsr.theta.value.hex() != parsed.ir.statements[0].bsr.theta.value.hex():\n"
            " raise RuntimeError('IR Float failed binary64 round trip')\n"
            "if 'b[1] = measure q[0]' not in serialized:\n"
            " raise RuntimeError('measurement mapping changed')\n"
            "print('round-trip and mapping preserved')\n",
        ]
    )
    if "round-trip and mapping preserved" not in output:
        raise RuntimeError(output)
