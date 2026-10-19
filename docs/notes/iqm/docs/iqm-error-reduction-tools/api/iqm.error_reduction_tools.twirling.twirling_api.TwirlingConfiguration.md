> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dac64f7d16cbf162c078fe276892b5aea4217a7584ff676a8dd0293a95925674.

# iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration

*class* iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration(*readout_twirl_strategy='LOCAL'*, *seed=None*, *circuit_twirling=True*, *num_twirling_instances=20*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Configuration for circuit twirling.

Attributes

|  |  |
|----|----|
| [`circuit_twirling`](#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.circuit_twirling "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.circuit_twirling") | Whether to apply Pauli twirling to two-qubit gates ("Poor Man's Pauli Twirling"). |
| [`num_twirling_instances`](#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.num_twirling_instances "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.num_twirling_instances") | Total number of randomized variants per input circuit when `circuit_twirling=True`. |
| [`readout_twirl_strategy`](#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.readout_twirl_strategy "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.readout_twirl_strategy") | Readout-twirling strategy. |
| [`seed`](#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.seed "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.seed") | RNG seed for reproducibility. |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |

Parameters:  
- **readout_twirl_strategy** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['LOCAL',* *'MINIMAL',* *'HADAMARD',* *'NONE'\]*)

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **circuit_twirling** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **num_twirling_instances** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

readout_twirl_strategy*: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['LOCAL', 'MINIMAL', 'HADAMARD', 'NONE'\]* *= 'LOCAL'*  
Readout-twirling strategy.

Supported values are `"LOCAL"` (4 strings, requires topology), `"MINIMAL"` (2 strings), `"HADAMARD"` (up to \$2^n\$ strings), and `"NONE"` to disable readout twirling entirely. When `"NONE"` is combined with `circuit_twirling=True`, `num_twirling_instances` random circuit-twirled variants are generated instead.

seed*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
RNG seed for reproducibility. `None` means non-deterministic.

circuit_twirling*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
Whether to apply Pauli twirling to two-qubit gates (“Poor Man’s Pauli Twirling”).

When `False`, the inserted Pauli rotations on single-qubit gates are suppressed; readout twirling (if any) still works.

num_twirling_instances*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 20*  
Total number of randomized variants per input circuit when `circuit_twirling=True`.

This budget is split evenly across the readout-twirling rot-strings (whose count is fixed by `readout_twirl_strategy`) so that every rot-string receives the same number of independent Pauli randomizations.

Reconciliation rules (a warning is emitted whenever the effective count differs from the requested one):

- If `num_twirling_instances` is a multiple of the number of rot-strings, it is used as-is.

- If it is not a multiple, it is **rounded up** to the next multiple.

- If it is **smaller** than the number of rot-strings, the number of rot-strings is used (one Pauli randomization per rot-string).

When `circuit_twirling=False` this field is ignored: each rot-string is emitted exactly once. Default of 20 follows common Pauli-twirling practice (10–50 instances).
