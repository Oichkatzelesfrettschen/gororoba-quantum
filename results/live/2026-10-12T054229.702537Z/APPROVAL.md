# Folded-QPE hardware authorization

The owner approves sending the folded-QPE circuits and metadata to IBM Quantum
and executing the bounded hardware case in this directory. After the account
rejects native mock validation because `mock_kingston` is unavailable, the owner
explicitly authorizes: "Run the approved hardware case" using the passing local
compilation and Aer checks plus the existing live submission guards.

The authorization binds record SHA-256
`b4774b596656865edf75ff9eae32cf0d2630a06477d2d1547f498d102bc66cef`
and QPY SHA-256
`fd1555a71ed6d6228b05f4003bc4d0a0df68316380af10120db6984091179277`.
The execution consists of 12 dynamic and 4 static PUBs on `ibm_kingston`,
8192 shots per PUB, a 60-second limit per job, a 120-second combined limit,
and a 60-second quota reserve. The runner retains its one-use authorization
marker and calibration, layout, dependency, circuit, and quota comparisons.

The generated `UNAPPROVED_CASE.md` remains the original proposal. This separate
authorization note records the subsequent owner decision without modifying the
approved record or circuit bytes.

The owner also requests analysis of measured results, future accuracy
improvements, and opportunities to reduce execution time. That analysis carries
authorization for local computation and result retrieval; additional QPU runs
require their own approval.
