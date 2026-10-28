# Final-result response projection replay

The [acquired-data review](../../archive/reviews/tuna-destination-one-acquired-review.md) accepted the
hardware result and identified a weaker ancillary observation: the final-result comparison recorded
Boolean equality claims without a retained response projection from which another reviewer could
derive them. The initial observations and summaries keep their bytes.

The [lossless projections](destination-final-result-projections.json) retain each response's `id`,
`job_id` and `created_on`, its exact four-field response schema and five-field payload schema, and
the compact sorted-key JSON hash observed during the first API audit. A second read of all six
existing endpoints returned those same object hashes. The remaining response values already live
in each case's retained result metadata, histogram and ordered binary raw list.

The [checked producer](../../../scripts/qi_tuna_final_result_receipt.py) reconstructs the entire
response object from that metadata and the existing acquisition files. It validates identities,
field sets, complete 4096-shot width-20 binary lists, histograms, numeric representations and source
bindings. It then compares the reconstructed object's hash with both the projection and the original
API observation, before deriving the equality flags. An unchanged histogram cannot conceal a
permutation of the raw shot order. The method avoids duplicating the binary lists while retaining
enough information to reconstruct every response value exactly.

The [checked receipt](destination-final-result-checked-receipt.json) binds all six responses and
33 input files. Normal and optimized replays agree:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" scripts/qi_tuna_final_result_receipt.py \
  docs/evidence/tuna-projector-geometry/destination-final-result-projections.json \
  --check docs/evidence/tuna-projector-geometry/destination-final-result-checked-receipt.json
```

The replay makes the six final-result equality observations independently checkable from retained
data. It does not authenticate the provider beyond the recorded API observations, establish analog
IQ availability, identify served acquisition settings, or change the frozen hardware endpoint.
The [upstream request](../../notes/quantum_inspire/destination-response-upstream-request.md) owns the
remaining acquisition-map, discriminator, schedule and IQ questions.
