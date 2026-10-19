> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.hubo.HUBOInstance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.hubo.HUBOInstance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 19a24c66ba6c7908da5a28f1b5dc93480dcee80700c81110a746da8a7c9ca05c.

# HUBOInstance

Module: [`iqm.applications.hubo`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.hubo.html#module-iqm.applications.hubo "iqm.applications.hubo")

*class* iqm.applications.hubo.HUBOInstance(*bp*, *vartype='BINARY'*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/hubo.py#L31-L136)  
Bases: [`ProblemInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance "iqm.applications.applications.ProblemInstance")

A problem instance class for generic HUBO problems.

Internally, the HUBO instance is stored as a `BinaryPolynomial` object. This object stores the problem as a collection of terms and their coefficients. Each term is a [`frozenset`](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)") of variables whose product makes up the term in the polynomial. For example, the polynomial:

\\1.3 x y - 3.7 x\\

is represented as:

``` python
{frozenset({'x', 'y'}): 1.3, frozenset({'x'}): -3.7}
```

Parameters:  
- **bp** ([*BinaryPolynomial*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)") *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Hashable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Hashable "(in Python v3.11)")*,* *...\]* *\|* [*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*Hashable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Hashable "(in Python v3.11)")*\],* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) –

  The input data for creating the instance. It can be one of the following:

  - A `BinaryPolynomial` object.

  - A dictionary mapping tuples/frozensets of variable names to coefficients. For the dictionary:

    - Keys must always be tuples or frozensets, even for single-variable terms. For example, `("var",): 0.5` represents a single-variable term, while `"var": 0.5` would be incorrectly interpreted as a cubic term with variables `"v"`, `"a"`, `"r"`.

    - Repeated variables in a tuple are treated based on `vartype` (consistent with the math: \\x^2 = x\\ for \\x \in \\0, 1\\\\ and \\x^2 = 1\\ for \\x \in \\-1, 1\\\\).

    - Values are the coefficients of the corresponding terms.

- **vartype** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\[Vartype.SPIN,* *'SPIN',* *Vartype.BINARY,* *'BINARY',* *Vartype.INTEGER,* *'INTEGER',* *Vartype.REAL,* *'REAL'\]*) – Optional variable type for interpreting the dictionary input. Defaults to `'BINARY'`.

Raises:  
- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the variable labels of the input are not sortable (e.g., mixing integers and strings).

- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the input `bp` is a dictionary and the keys aren’t tuples or frozensets.

Attributes

|  |  |
|----|----|
| [`average_quality`](#iqm.applications.hubo.HUBOInstance.average_quality "iqm.applications.hubo.HUBOInstance.average_quality") | The average quality value over all possible bitstrings. |
| [`dim`](#iqm.applications.hubo.HUBOInstance.dim "iqm.applications.hubo.HUBOInstance.dim") | The dimension of the problem, i.e., the number of variables in the polynomial. |

Methods

|  |  |
|----|----|
| [`quality`](#iqm.applications.hubo.HUBOInstance.quality "iqm.applications.hubo.HUBOInstance.quality") | The 'quality' of the input bitstring. |

*property* dim*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
The dimension of the problem, i.e., the number of variables in the polynomial.

*property* average_quality*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The average quality value over all possible bitstrings.

For HUBO problems, this is equal to the constant term in the spin/Hamiltonian formulation of the cost function.

quality(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/hubo.py#L116-L136)  
The ‘quality’ of the input bitstring.

Calculates the value of the polynomial when the bit values from the bitstring are plugged in for the variables. The values in the bitstring correspond to the variables at their corresponding location in `self.sorted_vars`.

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The bitstring representing the values to be plugged in for the variables.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the length of the input bitstring does not match the number of variables of the problem.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.applications.hubo.HUBOInstance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-09309fc2c0a7f35ec444da71930089e73d9219d4.png)
