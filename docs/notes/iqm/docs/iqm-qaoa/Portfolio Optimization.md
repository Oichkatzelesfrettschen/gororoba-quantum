> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/Portfolio%20Optimization.html](https://docs.iqm.tech/4.7/iqm-qaoa/Portfolio%20Optimization.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 31de8fc8625b81fe6c77ec0652e222e9a09370a9682e1fce75c249df847032c5.

# Portfolio Optimization

The purpose of this notebook is to showcase the QAOA library working from the problem definition all the way to execution on a real hardware.

In particular, here we use QAOA to solve a particular instance of portfolio optimization.

First, we describe the problem: we have `n_assets` assets, each with an `expected_return`. The variable containing the covariances and variances is called `cov_mat`. The goal is to choose a set of assets which maximize the yield, while minimizing the covariance, weighted by the investor’s `risk_aversion` (the higher, the more likely the investor is to avoid risk). The `budget` says how many assets we can buy.

```
import numpy as np

n_assets = 7
expected_return = [0.9, 1.1, 1.2, 0.7, 1.5, 1.8, 1.1]
rng = np.random.default_rng(seed=1)
A = rng.standard_normal((n_assets, n_assets))
cov_matrix = A @ A.T
risk_aversion = 2.0
budget = 3
```

Within the QAOA library, quadratic binary optimization problems are represented as objects of `BinaryQuadraticModel` or `ConstrainedQuadraticModel` from the `dimod` package ([read more about the models here](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#)).

In order to define a custom constrained problem in our QAOA library (`ConstrainedQuadraticInstance`), we need to create a custom object of `ConstrainedQuadraticModel`, by defining the objective and the constraint.

The objective is the expected return minus the variance of the portfolio weighted by the risk aversion.

The constraint has the identity matrix on the left-hand side (i.e., the number of selected assets) and the budget on the right-hand side.

```
from dimod import BinaryQuadraticModel, ConstrainedQuadraticModel

my_cqm = ConstrainedQuadraticModel()
objective = -np.diag(expected_return) + risk_aversion * cov_matrix
my_cqm.set_objective(BinaryQuadraticModel(objective, "BINARY"))
my_cqm.add_constraint_from_model(qm=BinaryQuadraticModel(np.eye(n_assets), "BINARY"), sense="==", rhs=budget)

from iqm.applications.qubo import ConstrainedQuadraticInstance

# The penalty magnitude here is chosen arbitrarily.
# There are rigorous way to find the "best" penalty, but we don't get into it here.
my_problem = ConstrainedQuadraticInstance(my_cqm, penalty=1)
```

In the following, we set up the connection to Resonance and define a simulator backend of the Garnet QPU.

Note: in general, you also need to specify the ‘usage mode’. For running on a real machine (in pay-as-you-go usage mode), the url would change to https://resonance.iqm.tech/garnet. For a specific timeslot the url would change to https://resonance.iqm.tech/garnet:timeslot

```
import os

SERVER_URL = "https://resonance.iqm.tech"
# If the token isn't saved in the environment, replace this by the token as a string.
API_TOKEN = os.environ.get("IQM_RESONANCE_API_TOKEN")

from iqm.qaoa.backends import SamplerResonance

backend = SamplerResonance(token=API_TOKEN, server_url=SERVER_URL, quantum_computer="garnet:mock", transpiler="HardwiredTranspiler")
```

Create the QUBO QAOA instance from the problem instance and train it. The `train` method has several possible parameters, but here the default setting is used (which uses analytical formulas since the QAOA has one layer).

```
from iqm.qaoa.qubo_qaoa import QUBOQAOA

my_qaoa = QUBOQAOA(problem=my_problem, num_layers=1, initial_angles=[0.1, 0.2])
my_qaoa.train()
```

Sample for a solution from the QAOA and post-process the result (removing the samples violating the constraint). The `sample` method of `my_qaoa` typically expects a number of shots. By omitting this parameter, it defaults to 20 000, the default maximum number on Resonance. The format of the samples is a dictionary whose keys are bitstrings (the individual samples that were taken) and whose values are integers (the number of times each sample was taken).

```
my_samples = my_qaoa.sample(sampler=backend)
my_samples_filtered = my_problem.satisfy_constraints(my_samples)
print("Number of satisfying samples:", sum(my_samples_filtered.values()))
```

We may now examine the found solutions.

```
# Calculate the objective function of all found solutions
samples_objective = {sample: my_problem.quality(sample) for sample in my_samples_filtered}

# Find the sample with the best quality
best_sample = max(samples_objective, key=lambda x: samples_objective[x])

# Find the best quality
best_quality = samples_objective[best_sample]

# Compute the weighted average quality
average_quality = my_problem.average_quality_counts(my_samples_filtered)

print("Best found sample:", best_sample)
print("Best sample quality:", best_quality)
print("Average feasible sample quality:", average_quality)
```
