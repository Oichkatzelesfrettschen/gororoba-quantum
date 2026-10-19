> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2fe5a63dccca5ba547feb56f2b322e1920fa799371736623b94a7b2ea17d6c0a.

# ProblemInstance

Module: [`iqm.applications.applications`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.html#module-iqm.applications.applications "iqm.applications.applications")

*class* iqm.applications.applications.ProblemInstance[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L52-L523)  
Bases: [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)")

The abstract base class for defining problem instances.

Currently, only problems with binary variables are supported. Any possible candidate solution is therefore represented by a bitstring (a string of 1’s and 0’s).

The abstract methods [`dim()`](#iqm.applications.applications.ProblemInstance.dim "iqm.applications.applications.ProblemInstance.dim") and [`quality()`](#iqm.applications.applications.ProblemInstance.quality "iqm.applications.applications.ProblemInstance.quality") are meant to be overridden by children classes, depending on how the dimension of the problem and the quality of the solution are understood.

The attributes upper/lower bound, average/best quality and the corresponding bitstrings start as `None`. The first time one of them is called, it calls the method [`initialize_properties()`](#iqm.applications.applications.ProblemInstance.initialize_properties "iqm.applications.applications.ProblemInstance.initialize_properties"), which calculates all of them by brute-forcing over all bitstrings representing solution candidates.

Attributes

|  |  |
|----|----|
| [`average_quality`](#iqm.applications.applications.ProblemInstance.average_quality "iqm.applications.applications.ProblemInstance.average_quality") | The average quality value over all possible bitstrings. |
| [`best_quality`](#iqm.applications.applications.ProblemInstance.best_quality "iqm.applications.applications.ProblemInstance.best_quality") | The *best* quality value over all possible bitstrings. |
| [`dim`](#iqm.applications.applications.ProblemInstance.dim "iqm.applications.applications.ProblemInstance.dim") | The dimension of the problem (e.g., the number of nodes in a problem graph). |
| [`highest_quality_bitstrings`](#iqm.applications.applications.ProblemInstance.highest_quality_bitstrings "iqm.applications.applications.ProblemInstance.highest_quality_bitstrings") | The set of the highest quality bitstrings, i.e., the worst possible "solutions" to the problem. |
| [`lower_bound`](#iqm.applications.applications.ProblemInstance.lower_bound "iqm.applications.applications.ProblemInstance.lower_bound") | The lowest quality value among all possible bitstrings. |
| [`lowest_quality_bitstrings`](#iqm.applications.applications.ProblemInstance.lowest_quality_bitstrings "iqm.applications.applications.ProblemInstance.lowest_quality_bitstrings") | The set of the lowest quality bitstrings, i.e., the solutions to the problem. |
| [`original_variables`](#iqm.applications.applications.ProblemInstance.original_variables "iqm.applications.applications.ProblemInstance.original_variables") | The tuple of the original variable labels of the problem. |
| [`upper_bound`](#iqm.applications.applications.ProblemInstance.upper_bound "iqm.applications.applications.ProblemInstance.upper_bound") | The highest quality value among all possible bitstrings. |
| [`variables`](#iqm.applications.applications.ProblemInstance.variables "iqm.applications.applications.ProblemInstance.variables") | The sequence of the variable labels of the problem. |

Methods

|  |  |
|----|----|
| [`average_quality_counts`](#iqm.applications.applications.ProblemInstance.average_quality_counts "iqm.applications.applications.ProblemInstance.average_quality_counts") | Accepts a dictionary and returns the average quality of the keys weighted by their values. |
| [`average_quality_renormalized`](#iqm.applications.applications.ProblemInstance.average_quality_renormalized "iqm.applications.applications.ProblemInstance.average_quality_renormalized") | Accepts a dictionary and returns the renormalized quality of the keys weighted by their values. |
| [`cvar`](#iqm.applications.applications.ProblemInstance.cvar "iqm.applications.applications.ProblemInstance.cvar") | Calculates the Conditional Value at Risk (CVaR) of the given dictionary of counts at the given quantile. |
| [`fix_variables`](#iqm.applications.applications.ProblemInstance.fix_variables "iqm.applications.applications.ProblemInstance.fix_variables") | Fixes (assigns) some of the problem variables. |
| [`initialize_properties`](#iqm.applications.applications.ProblemInstance.initialize_properties "iqm.applications.applications.ProblemInstance.initialize_properties") | Finds the upper/lower bound of the cost function, its average/best value and the corresponding bitstrings. |
| [`local_bitflip_bitstring`](#iqm.applications.applications.ProblemInstance.local_bitflip_bitstring "iqm.applications.applications.ProblemInstance.local_bitflip_bitstring") | Take a bitstring and replace it with its lowest-energy unit-Hamming-distance neighbor. |
| [`local_bitflip_postprocessing`](#iqm.applications.applications.ProblemInstance.local_bitflip_postprocessing "iqm.applications.applications.ProblemInstance.local_bitflip_postprocessing") | Postprocessing method for checking a unit Hamming distance neighborhood of the dictionary of counts. |
| [`percentile_counts`](#iqm.applications.applications.ProblemInstance.percentile_counts "iqm.applications.applications.ProblemInstance.percentile_counts") | A method that selects only the best / worst `quantile` of given `counts`, measured by [`quality()`](#iqm.applications.applications.ProblemInstance.quality "iqm.applications.applications.ProblemInstance.quality"). |
| [`quality`](#iqm.applications.applications.ProblemInstance.quality "iqm.applications.applications.ProblemInstance.quality") | Accepts a bitstring and returns its quality / energy (the smaller the better). |
| [`quality_renormalized`](#iqm.applications.applications.ProblemInstance.quality_renormalized "iqm.applications.applications.ProblemInstance.quality_renormalized") | Accepts a bitstring and returns renormalized quality of that bitstring. |
| [`restore_fixed_variables`](#iqm.applications.applications.ProblemInstance.restore_fixed_variables "iqm.applications.applications.ProblemInstance.restore_fixed_variables") | Postprocessing method for restoring fixed variables to the measurement bitstrings. |
| [`restore_fixed_variables_bitstring`](#iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring "iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring") | Amend a measurement bitstring by inserting bits corresponding to variables with fixed values. |

&nbsp;

*abstract property* dim*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
The dimension of the problem (e.g., the number of nodes in a problem graph).

&nbsp;

*abstractmethod* quality(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L85-L93)  
Accepts a bitstring and returns its quality / energy (the smaller the better).

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The bitstring representing a solution candidate.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

&nbsp;

fix_variables(*variables*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L95-L105)  
Fixes (assigns) some of the problem variables.

Parameters:  
**variables** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Either an iterable of variables (which get all fixed to the value 1) or a dictionary with keys equal to the variables to fix and whose values are equal to the values to fix them to (either 1 or 0).

Return type:  
None

&nbsp;

initialize_properties(*max_size=30*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L107-L156)  
Finds the upper/lower bound of the cost function, its average/best value and the corresponding bitstrings.

The quantities are calculated by brute force (scaling exponentially). By default, using this with problem sizes larger than `max_size` (default 30) will raise ValueError. This can be bypassed by making `max_size` larger or setting it to `None`.

Parameters:  
**max_size** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The maximum size of problems for which the properties may be calculated.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If [`initialize_properties()`](#iqm.applications.applications.ProblemInstance.initialize_properties "iqm.applications.applications.ProblemInstance.initialize_properties") was called on a [`ProblemInstance`](#iqm.applications.applications.ProblemInstance "iqm.applications.applications.ProblemInstance") object with dimension larger than `max_size`.

Return type:  
None

&nbsp;

*property* upper_bound*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The highest quality value among all possible bitstrings.

Can be calculated together with other bounds using the brute-force [`initialize_properties()`](#iqm.applications.applications.ProblemInstance.initialize_properties "iqm.applications.applications.ProblemInstance.initialize_properties"). Shouldn’t be modified by a user.

&nbsp;

*property* lower_bound*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The lowest quality value among all possible bitstrings.

Can be calculated together with other bounds using the brute-force [`initialize_properties()`](#iqm.applications.applications.ProblemInstance.initialize_properties "iqm.applications.applications.ProblemInstance.initialize_properties"). Shouldn’t be modified by a user.

&nbsp;

*property* average_quality*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The average quality value over all possible bitstrings.

Can be calculated together with bounds using the brute-force [`initialize_properties()`](#iqm.applications.applications.ProblemInstance.initialize_properties "iqm.applications.applications.ProblemInstance.initialize_properties"). Shouldn’t be modified by a user. Meant to be used in comparison with QAOA results to see how much (if at all) the optimization improves over uniformly random guessing.

&nbsp;

*property* variables*: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
The sequence of the variable labels of the problem.

This is used to convert the variable labels to integers whenever needed (e.g., when a solution is represented by a bitstring). This may be modified when e.g., some variables are fixed using [`fix_variables()`](#iqm.applications.applications.ProblemInstance.fix_variables "iqm.applications.applications.ProblemInstance.fix_variables").

&nbsp;

*property* original_variables*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), ...\]*  
The tuple of the original variable labels of the problem.

This is used to convert the original variable labels to integers whenever needed. This is saved on instantiation and never modified. This becomes relevant when some of the variables of the problem are fixed using [`fix_variables()`](#iqm.applications.applications.ProblemInstance.fix_variables "iqm.applications.applications.ProblemInstance.fix_variables"), which effectively removes them from the problem.

&nbsp;

*property* best_quality*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The *best* quality value over all possible bitstrings.

For minimization problems, this is equal to [`lower_bound`](#iqm.applications.applications.ProblemInstance.lower_bound "iqm.applications.applications.ProblemInstance.lower_bound"). Like similar properties, it can be calculated using the brute-force [`initialize_properties()`](#iqm.applications.applications.ProblemInstance.initialize_properties "iqm.applications.applications.ProblemInstance.initialize_properties"). Shouldn’t be modified by a user. Meant to be used in comparison with QAOA results to see how close the optimization gets to the ideal best solution.

&nbsp;

*property* lowest_quality_bitstrings*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
The set of the lowest quality bitstrings, i.e., the solutions to the problem.

Can be calculated together with quality bounds using the brute-force [`initialize_properties()`](#iqm.applications.applications.ProblemInstance.initialize_properties "iqm.applications.applications.ProblemInstance.initialize_properties"). Shouldn’t be modified by a user. If the solution is unique, the set has just one element.

&nbsp;

*property* highest_quality_bitstrings*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
The set of the highest quality bitstrings, i.e., the worst possible “solutions” to the problem.

Can be calculated together with quality bounds using the brute-force [`initialize_properties()`](#iqm.applications.applications.ProblemInstance.initialize_properties "iqm.applications.applications.ProblemInstance.initialize_properties"). Shouldn’t be modified by a user. If the solution is unique, the set has just one element.

&nbsp;

quality_renormalized(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L257-L273)  
Accepts a bitstring and returns renormalized quality of that bitstring.

The quality is renormalized using [`best_quality`](#iqm.applications.applications.ProblemInstance.best_quality "iqm.applications.applications.ProblemInstance.best_quality") and [`average_quality`](#iqm.applications.applications.ProblemInstance.average_quality "iqm.applications.applications.ProblemInstance.average_quality").

- A value of 1 corresponds to the best solution.

- A value of 0 corresponds to average quality.

- A value above/under 0 corresponds to better/worse than average quality.

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The bitstring representing a solution.

Returns:  
The renormalized quality of the solution as a float.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

&nbsp;

average_quality_counts(*counts*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L275-L304)  
Accepts a dictionary and returns the average quality of the keys weighted by their values.

The keys of the input dictionary are bitstrings (representing possible solutions) and the values are their respective counts, i.e., the number of times that the particular string was sampled from a QAOA run. The quality is calculated by [`quality()`](#iqm.applications.applications.ProblemInstance.quality "iqm.applications.applications.ProblemInstance.quality").

Warning

The bitstrings in the `counts` need to be ordered the same way as the variables of the problem. If you’re using a dictionary of counts obtained directly from a Qiskit experiment, you need to reverse the order of the bitstrings (keys of the `counts` dictionary) first.

Parameters:  
**counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A dictionary whose keys are solution bitstrings and whose values are the respective counts.

Returns:  
Average quality of the bitstrings, weighted by their counts.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the number of measurements in `counts` is 0 (e.g., if it’s an empty dictionary).

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

&nbsp;

average_quality_renormalized(*counts*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L306-L328)  
Accepts a dictionary and returns the renormalized quality of the keys weighted by their values.

Calculates the average weighted quality using [`average_quality_counts()`](#iqm.applications.applications.ProblemInstance.average_quality_counts "iqm.applications.applications.ProblemInstance.average_quality_counts") and renormalizes it using [`best_quality`](#iqm.applications.applications.ProblemInstance.best_quality "iqm.applications.applications.ProblemInstance.best_quality") and [`average_quality`](#iqm.applications.applications.ProblemInstance.average_quality "iqm.applications.applications.ProblemInstance.average_quality").

- A value of 1 corresponds to the best solution.

- A value of 0 corresponds to average quality.

- A value above/under 0 corresponds to better/worse than average quality.

Warning

The bitstrings in the `counts` need to be ordered the same way as the variables of the problem. If you’re using a dictionary of counts obtained directly from a Qiskit experiment, you need to reverse the order of the bitstrings (keys of the `counts` dictionary) first.

Parameters:  
**counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A dictionary whose keys are solution bitstrings and whose values are the respective counts.

Returns:  
Average quality of the bitstrings, weighted by their counts and renormalized.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

&nbsp;

restore_fixed_variables_bitstring(*bitstring*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L330-L361)  
Amend a measurement bitstring by inserting bits corresponding to variables with fixed values.

When variables are fixed, the number of variables of the (remaining) problem is reduced. When the problem is solved (e.g., by a quantum computer), the solution doesn’t include the fixed variables. This method takes a single solution bitstring and modifies it by inserting the fixed variables.

Warning

Fixing variables effectively removes them from the problem. This might lead to the internal ordering of the variables being changed. The input `bitstring` is expected to respect the ordering of `self.variables` and the output bitstring respects the ordering of `self.original_variables`.

Warning

The input bitstring needs to be ordered the same way as the variables of the problem. If you’re using the output from a Qiskit experiment, you need to reverse the order of the bitstring first.

Parameters:  
**bitstring** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A representation of a solution as a string.

Returns:  
`bitstring` amended by inserting the fixed variable bits to their places.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

&nbsp;

restore_fixed_variables(*counts*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L363-L395)  
Postprocessing method for restoring fixed variables to the measurement bitstrings.

When variables are fixed, the number of variables of the (remaining) problem is reduced. When the problem is solved (e.g., by a quantum computer), the solution doesn’t include the fixed variables. This method takes a dictionary of solutions (e.g., the counts from a quantum computer) and modifies the keys (bitstrings) by inserting the fixed variables.

Warning

Fixing variables effectively removes them from the problem. This might lead to the internal ordering of the variables being changed. The input `counts` is expected to respect the ordering of `self.variables` and the output counts respect the ordering of `self.original_variables`.

Warning

The bitstrings in the `counts` need to be ordered the same way as the variables of the problem. If you’re using a dictionary of counts obtained directly from a Qiskit experiment, you need to reverse the order of the bitstrings (keys of the `counts` dictionary) first.

Parameters:  
**counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A dictionary whose keys are bitstrings (solutions) and whose values are integers (their respective frequencies)

Returns:  
The input dictionary corrected by inserting the fixed variables into the keys, where they belong.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

&nbsp;

local_bitflip_bitstring(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L397-L424)  
Take a bitstring and replace it with its lowest-energy unit-Hamming-distance neighbor.

Takes the solution bitstring and then iteratively swaps each bit in it. The function returns the lowest-energy bitstring from all of these bitstrings (including the original bitstring).

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The bitstring to be replaced by its lowest-energy unit Hamming distance neighbor.

Returns:  
The replaced bitstring.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

&nbsp;

local_bitflip_postprocessing(*counts*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L426-L453)  
Postprocessing method for checking a unit Hamming distance neighborhood of the dictionary of counts.

When implemented naively, the time complexity of this scales cubically \\\mathcal{O}(n^3)\\ in the number of variables (linear from iterating over them and quadratic from calculating the energy), but some computation might be saved in the calculation of the energy because it’s repeatedly calculated for very similar bitstrings.

Warning

The bitstrings in the `counts` need to be ordered the same way as the variables of the problem. If you’re using a dictionary of counts obtained directly from a Qiskit experiment, you need to reverse the order of the bitstrings (keys of the `counts` dictionary) first.

Parameters:  
**counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A dictionary whose keys are bitstrings (solutions) and whose values are integers (their respective frequencies)

Returns:  
The input dictionary modified by replacing each bitstring by its lowest-energy neigbor.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

&nbsp;

percentile_counts(*counts*, *quantile*, *best_percentile=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L455-L501)  
A method that selects only the best / worst `quantile` of given `counts`, measured by [`quality()`](#iqm.applications.applications.ProblemInstance.quality "iqm.applications.applications.ProblemInstance.quality").

The quantile is weighted by the frequencies (counts) of the bitstrings. If multiple bitstrings around the `quantile` have the same quality, the order is selected arbitrarily (or rather, based on how the built-in `sorted` function sorts them). If a bitstring has counts that cross the `quantile`, its counts in the output are adjusted to match the `quantile` exactly (at least rounded to the nearest integer).

Warning

The bitstrings in the `counts` need to be ordered the same way as the variables of the problem. If you’re using a dictionary of counts obtained directly from a Qiskit experiment, you need to reverse the order of the bitstrings (keys of the `counts` dictionary) first.

Parameters:  
- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The input dictionary of counts.

- **quantile** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The quantile of counts to be selected.

- **best_percentile** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Boolean saying whether the “best” (lowest quality) or the “worst” (highest) bitstrings should be selected.

Returns:  
A dictionary of counts, with only the best / worse bitstrings selected.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the quantile is not between 0 and 1 (included).

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

&nbsp;

cvar(*counts*, *quantile=0.05*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/applications.py#L503-L523)  
Calculates the Conditional Value at Risk (CVaR) of the given dictionary of counts at the given quantile.

The CVaR is the average of the worst-case `quantile` of the data. In the case of training QAOA, it’s often used to calculate the average of the best `quantile` of samples.

Warning

The bitstrings in the `counts` need to be ordered the same way as the variables of the problem. If you’re using a dictionary of counts obtained directly from a Qiskit experiment, you need to reverse the order of the bitstrings (keys of the `counts` dictionary) first.

Parameters:  
- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The given dictionary of counts.

- **quantile** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The given quantile. Since it’s common to calculate the CVaR at 5%, that’s the default value for this variable

Returns:  
The CVaR of the counts.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.applications.applications.ProblemInstance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-4ca4550387b121268fe1d1da55981f772fae5ccd.png)
