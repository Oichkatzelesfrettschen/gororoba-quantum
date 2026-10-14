# Hoeffding 1963 -- Probability inequalities for sums of bounded random variables

Tag convention: [P] marks paper statements; [I] marks repository interpretation.

## Citation and provenance

- Wassily Hoeffding. Journal of the American Statistical Association 58(301), 13-30 (1963), [DOI](https://doi.org/10.1080/01621459.1963.10500830).
- Reading scope: the citation and the inequality as applied in experiment_optimizer.py; the publisher full text is outside the retained library and received no reading in this note.

## Main claims and evidence

- [P] For independent observations bounded in [a, b], the probability that the sample mean deviates from its expectation by t or more is at most 2 exp(-2 n t^2 / (b - a)^2).

## Mapping to this repository

- [I] experiment_optimizer.py bounds each contributing PUB separately with this inequality, splits the endpoint's error probability across them, and adds their radii, assuming independent stationary repetitions within a PUB and arbitrary dependence among components of a shot and between PUBs.
- [I] For an orbit gain over four 4,096-shot PUBs with endpoint error 0.005 split four ways, the summed two-sided radius is 4 x 2 sqrt(log(8/0.005) / (2 x 4096)) = 0.240, the patch-window orbit half-width.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: high, as the admission baseline.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] The bound needs no variance knowledge and stays valid at any outcome distribution; that robustness costs width relative to variance-adaptive and normal-approximation intervals.
