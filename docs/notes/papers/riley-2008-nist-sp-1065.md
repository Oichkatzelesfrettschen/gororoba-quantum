# Riley 2008 -- Handbook of Frequency Stability Analysis (NIST Special Publication 1065)

## Source copy and license

The [DOI link](https://doi.org/10.6028/NIST.SP.1065) resolves to the NIST-hosted PDF
https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication1065.pdf. The title page reads
"W.J. Riley, Under contract with: Time and Frequency Division, Physics Laboratory, National Institute
of Standards and Technology". The NIST
[publication page](https://www.nist.gov/publications/handbook-frequency-stability-analysis) says
nothing about the rights of this report, and NIST's
[statement on its technical series](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications)
limits the absence of United States copyright to "works authored by NIST employees" and adds that NIST
"may also obtain and hold copyright in data/works created by non-NIST employees (e.g., NIST
contractors) when copyright is assigned to NIST". Neither page establishes the status of a contractor
report, and the report states no license, so the registry records the rights as unasserted and the PDF
stays external: its optional personal reading copy is
`docs/local_source_cache/riley-2008-nist-sp-1065.pdf`, and [SOURCES.json](../../SOURCES.json) records
the SHA-256 of the bytes read and the reading scope. The statements transcribed below are the
definitions and the noise-type separations the repository cites.

Tag convention: [P] marks paper statements; [I] marks repository interpretation.

## Citation and provenance

- Author: William J. Riley (Hamilton Technical Services, Beaufort, South Carolina). The title page
  names Riley alone, the NIST publication page lists William Riley and David A. Howe, and the Crossref
  record lists Riley twice; the front matter thanks Howe and the NIST Time and Frequency Division.
- Publication: NIST Special Publication 1065, July 2008, 136 pages, DOI 10.6028/nist.sp.1065
  (Crossref receipt below).
- PDF read: the file the DOI redirect served, 9,691,994 bytes. The tf.nist.gov copy
  (https://tf.nist.gov/general/pdf/2220.pdf) is a different file of 4,106,808 bytes and was not read.
- SHA-256: `ee6bb84554683d718638717651c75f7d487af9e04c168880760ae41a485eb52f`
- Page convention: the PDF is a scanned report with a recognized text layer whose equation text is
  unreliable, so equations below were read from rendered pages. The printed page number equals the PDF
  page minus 10 (printed p. 14 is PDF p. 24).
- Reading scope: front matter (PDF p. 3), Section 3.2 on power-law noise (PDF pp. 15-16), Section 5.1
  (PDF p. 19), Sections 5.2.2, 5.2.4 and 5.2.5 (PDF pp. 24-27), and Sections 5.5.1, 5.5.2 and 5.5.5 on
  noise identification (PDF pp. 53-56). The Hadamard, total and Theo1 variances, bias functions,
  confidence-interval tables, the simulation chapter and the test data unread.
- Poppler reports no error on the file; the recognized text layer carries character errors (for
  example "Theol" for Theo1), and the original bytes are unmodified.

| Source | URL | SHA-256 of retrieved bytes | Read for |
|---|---|---|---|
| Crossref record | https://api.crossref.org/works/10.6028/nist.sp.1065 | `40b281ac65c13b68db89ea98cf56b444edd5613bb8ec631b257edc883a4724ec` | Bibliographic identity and author listing |
| NIST publication page | https://www.nist.gov/publications/handbook-frequency-stability-analysis | `5fd31aa69f785c66292b015cab7412b6cfa84caf26983d25d1793d2ad3d77b70` | Author listing and PDF route |
| NIST statement on technical series | https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications | `b35c0f091ab540ca0869a299d4d6b20f3c05c0032b4e783f81678b956c1f27f7` | Rights limits |

## Transcribed statements

- [P] Power-law noise (Section 3.2, PDF p. 15): the instability of most sources "can be modeled by a
  combination of power-law noises having a spectral density of their fractional frequency
  fluctuations of the form S_y(f) proportional to f^alpha", with alpha = 2 for white phase modulation
  (W PM), 1 flicker PM (F PM), 0 white frequency modulation (W FM), -1 flicker FM (F FM), -2 random
  walk FM (RW FM), -3 flicker walk FM and -4 random run FM (PDF pp. 15-16).
- [P] Sigma-tau slopes (Section 5.1, PDF p. 19, printed p. 9): the table pairs alpha with the
  log-log slope mu of the stability plot as W PM (2, -2), F PM (1, about -2), W FM (0, -1), F FM
  (-1, 0) and RW FM (-2, 1). "The log sigma versus log tau slopes are the same for the two PM noise
  types, but are different on a Mod sigma plot, which is often used to distinguish between them."
- [P] Original Allan variance, Eq. 6 (Section 5.2.2, PDF p. 24): for M fractional-frequency values y_i
  averaged over interval tau, sigma_y^2(tau) = [1 / (2 (M - 1))] times the sum over i = 1 to M - 1 of
  (y_{i+1} - y_i)^2. The paper says the Allan variance "has the advantage, for more divergent noise
  types such as flicker noise, of converging to a value that is independent on the number of
  samples", equals the ordinary variance for white FM noise, and "the original Allan variance has been
  largely superseded by its overlapping version".
- [P] Overlapping Allan variance, Eqs. 10 and 11 (Section 5.2.4, PDF p. 26): for averaging time
  tau = m tau_0 from M frequency values, sigma_y^2(tau) = [1 / (2 m^2 (M - 2m + 1))] times the sum
  over j = 1 to M - 2m + 1 of the square of the sum over i = j to j + m - 1 of (y_{i+m} - y_i); from
  N = M + 1 phase values, sigma_y^2(tau) = [1 / (2 (N - 2m) tau^2)] times the sum over i = 1 to N - 2m
  of (x_{i+2m} - 2 x_{i+m} + x_i)^2. The deviation ADEV is the square root. "The overlapped Allan
  deviation is the most common measure of time-domain frequency stability."
- [P] Modified Allan variance, Eqs. 13 and 14 (Section 5.2.5, PDF p. 27): Mod sigma_y^2(tau) =
  [1 / (2 m^4 (M - 3m + 2))] times the sum over j = 1 to M - 3m + 2 of the square of the double sum
  over i = j to j + m - 1 and k = i to i + m - 1 of (y_{k+m} - y_k); in phase data
  [1 / (2 m^2 tau^2 (N - 3m + 1))] times the sum over j = 1 to N - 3m + 1 of the square of the sum over
  i = j to j + m - 1 of (x_{i+2m} - 2 x_{i+m} + x_i). The modified variance "is the same as the normal
  Allan variance for m = 1. It includes an additional phase averaging operation, and has the advantage
  of being able to distinguish between white and flicker PM noise."
- [P] Noise identification (Section 5.5.2, PDF p. 54): the Barnes B1 function is "the ratio of the
  N-sample (standard) variance to the two-sample (Allan) variance", its dependence on mu identifies
  the power-law type for -2 <= mu <= 2 (W and F PM to flicker walk FM), and the W PM versus F PM
  ambiguity at mu = -2 is resolved by R(n), "the ratio of the modified Allan to the normal Allan
  variances"; the method "cannot distinguish between W and F PM at unity averaging factor".
- [P] Lag-1 autocorrelation (Section 5.5.5, PDF p. 55): "For frequency data, white PM noise has
  rho_1 = -1/2, flicker PM noise has rho_1 = -1/3, and white FM noise has rho_1 = 0."
- [P] Noise-type consequence (Section 5.5.1, PDF p. 53): knowledge of the dominant noise type is
  "necessary to determine the equivalent number of chi-squared degrees of freedom (edf) for setting
  confidence intervals and error bars".

## Mapping to this repository

- [I] Drift series ([bdsc_drift_series.py](../../../scripts/bdsc_drift_series.py)). The series' primary
  statistic is the von Neumann ratio eta = sum (x[t+1] - x[t])^2 / sum (x[t] - mean x)^2 over the runs of
  one setting. With Eq. 6 and the ordinary variance of M values it follows that
  B1 = (standard variance)/(Allan variance) = 2 / eta, derived here and checkable by substitution, so
  eta = 2 reads as W FM (mu = -1, white run-to-run jitter), eta below 2 as a persisting drift (mu above
  -1) and the series' exact permutation null replaces the tabulated expected B1 values of Section 5.5.2
  with a finite-sample reference at a single averaging factor. Seven runs give 6 successive differences at m = 1,
  M - 2m + 1 = 4 overlapping sums at m = 2 and 2 at m = 3 in Eq. 10, so the separation of F FM
  (mu = 0) from RW FM (mu = 1) by slope is out of reach and the series reports ordering statistics
  instead of a sigma-tau slope.
- [I] The handbook assumes evenly spaced averaged readings without dead time at the basic interval;
  the series' readings are separate jobs two hours apart, so Allan statistics of them describe
  between-run variation and treat each job as a sample, not as an average over the interval.
- [I] Photonic characterization notes ([2306.00874](2306.00874.md), [2606.18408](2606.18408.md)). Neither
  paper reports an Allan statistic; the handbook supplies the noise-type vocabulary for stating a
  drift model for the series.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: low (a standard statistic for drift of a
  calibration parameter).
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] The equation text layer is unreliable and the equations above were checked against rendered pages
for Eqs. 6, 10, 11, 13 and 14 only; B1's own formula (Section 5.5.2) was not transcribed. The
statements on the Hadamard and total variances, bias corrections and confidence intervals rest on
unread sections.
