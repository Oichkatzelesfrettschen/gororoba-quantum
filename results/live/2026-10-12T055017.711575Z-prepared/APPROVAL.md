# Refreshed folded-QPE hardware authorization

The owner explicitly approves the refreshed hardware case after reviewing the
calibration update and replacement of physical qubit 91 with 73.

The authorization binds record SHA-256
`2f87de38661a484bb0e09625b25e363acdc1eed1aba408ef5c2bea1bd6a1092a`
and QPY SHA-256
`84b5c3c7703db74fdbd6eb477d131f5353a14d63befb7d3f5375c63a85acf6a1`.
The plan uses 12 dynamic and 4 static PUBs at 8192 shots each on
`ibm_kingston`, with two 60-second execution ceilings, a 120-second combined
ceiling, and a 60-second quota reserve. The modeled nominal and stress
charges remain 39.632399872 and 45.543119872 seconds.

The owner also authorizes the IBM circuit-data transfer and explicitly permits
hardware execution using the local checks and live admission guards after
native mock validation reports unavailable `mock_kingston` access. The
submission retains source, calibration, layout, QPY, quota, and single-use
approval checks. Additional QPU jobs require their own approval.

`checkpoint-provenance.json` records the preparation checkpoint's origin.
The generated `UNAPPROVED_CASE.md` remains the unchanged proposal; this note
records the subsequent authorization.
