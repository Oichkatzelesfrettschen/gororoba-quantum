> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/cvarvqe/04-job-estimator](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/cvarvqe/04-job-estimator)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/cvarvqe/04-job-estimator.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Job Estimator

## Goal of the estimator

The CVar VQE estimator guives you the **maximum number of shots possible** taking into account all user configuration.

It is computed this way:

`Shots_Number = number_of_basis_measurement x number_of_shots_per_iteration x maximum_iterations_number`

- `number_of_basis_measurement = 1`: Number of Pauli Basis (I,X,Y,Z) generated for the measurements.
- `number_of_shots_per_iteration = 1_000_000`: Number of detected event containing at least one photon.
- `maximum_iterations_number`: Maximum number of times we run the classical optimizer.

So we can simplify the problem with:

`Shots_Number = 1_000_000 x maximum_iterations_number`

## POST Request

The POST request for the estimator is working exactly the same way as the Job Creation Request: [CVaR VQE - Job Creation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/cvarvqe/03-job-creation)

Excepted the URL which has to be on this form:

- `https://api.cloud.quandela.com/qt/cvarvqe/estimate`

## GET request

To have the respond from the cloud please use the GET request: [CVaR VQE - Job Results](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/cvarvqe/05-job-results)
