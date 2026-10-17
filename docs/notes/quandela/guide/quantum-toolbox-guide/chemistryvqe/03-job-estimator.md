> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/03-job-estimator](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/03-job-estimator)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/chemistryvqe/03-job-estimator.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Job Estimator

## Goal of the estimator

The Chemistry VQE estimator guives you the **maximum number of shots possible** taking into account all user configuration.

It is computed this way:

`Shots_Number = number_of_basis_measurement x number_of_shots_per_iteration x maximum_iterations_number`

For 'LiH' molecule:

- `number_of_basis_measurement = 25` : Number of Pauli Basis (I,X,Y,Z) generated for the measurements.
- `number_of_shots_per_iteration = 100_000` : Number of detected event containing at least one photon.
- `=> Shots_Number = 2_500_000 x maximum_iterations_number`

For 'BeH2' molecule:

- `number_of_basis_measurement = 54`
- `number_of_shots_per_iteration = 700_000`
- `=> Shots_Number = 37_800_000 x maximum_iterations_number`

Be careful! This estimator can only be used for 'LiH' and 'BeH2'!

## POST Request

The POST request for the estimator is working exactly the same way as the Job Creation Request: [Chemistry VQE - Job Creation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/02-job-creation)

Excepted the URL which has to be on this form:

- `https://api.cloud.quandela.com/qt/chemistryvqe/estimate`

## GET request

To have the respond from the cloud please use the GET request: [Chemistry VQE - Job Results](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/chemistryvqe/04-job-results)
