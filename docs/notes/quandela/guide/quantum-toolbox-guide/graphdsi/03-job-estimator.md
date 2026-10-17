> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphdsi/03-job-estimator](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphdsi/03-job-estimator)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/graphdsi/03-job-estimator.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Job Estimator

## Goal of the estimator

The Graph DSI estimator guives you the number of shots in the order of **how much is required for a good approximation** and, as such, to find a satisfactory result.

It is computed this way:

`Shots_Number = 10 * largest singular value x 4 to the power of node_number`

> Be careful! If you enter a number of shot bigger than the estimation, you will exceed this reference value.

## POST Request

The POST request for the estimator is working exactly the same way as the Job Creation Request: [Graph DSI - Job Creation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphdsi/02-job-creation)

Excepted the URL which has to be on this form:

- `https://api.cloud.quandela.com/qt/graphDSI/estimate`

## GET request

To have the respond from the cloud please use the GET request: [Graph DSI - Job Results](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/graphdsi/04-job-results)
