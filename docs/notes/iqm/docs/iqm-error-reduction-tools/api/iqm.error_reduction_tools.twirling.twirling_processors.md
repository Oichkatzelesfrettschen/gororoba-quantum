> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a4217f584c8d03fde3dc6b599a99b8686d8bc05abced9255cfc7a32d0eff111e.

# iqm.error_reduction_tools.twirling.twirling_processors

Shared utility functions for processing measurement counts.

These primitives are used by both readout_characterization and error_reduction_tools for merging and un-twirling measurement count dictionaries.

Functions

|  |  |
|----|----|
| [`sum_counts`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.sum_counts.html#iqm.error_reduction_tools.twirling.twirling_processors.sum_counts "iqm.error_reduction_tools.twirling.twirling_processors.sum_counts")(list_counts) | Sum a list of measurement counts dictionaries. |
| [`untwirl_and_sum_counts`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts.html#iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts "iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts")(raw_counts_list, ...) | Untwirl and sum measurement counts from multiple circuits. |
| [`untwirl_counts`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.untwirl_counts.html#iqm.error_reduction_tools.twirling.twirling_processors.untwirl_counts "iqm.error_reduction_tools.twirling.twirling_processors.untwirl_counts")(counts, rot_string) | Apply untwirling to measurement counts. |
