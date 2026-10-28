# Ascella transition context findings

Seven Ascella jobs completed the five singleton, forward-packed and reverse-packed settings: **983,040 accepted events**, 50 provider execution seconds and 7.589824 consumed credits. Every job reached its full sample target. The [inventory](acquisition-inventory.json) binds the raw results and accounting; the [analysis](../../../results/quandela/ascella-transition-context-analysis.json) binds the complete input, body and raw-result hashes.

All 20 comparisons, including each setting's prior-pilot baseline, have matching returned `computed_circuit` and `computed_input` digests. Each percentage below uses all 65,536 accepted events, including invalid-photon categories, and counts leakage outside the corresponding active logical ports. The prior pilot was one twelve-entry job; forward and reverse each use a five-entry iterator.

| Setting | Prior pilot leakage | Singleton leakage | Forward leakage | Reverse leakage |
|---|---:|---:|---:|---:|
| identity-2 | 6.2149% | 0.2304% | 0.2289% | 0.2151% |
| identity-5 | 4.8462% | 0.1419% | 1.9409% | 6.3461% |
| cross-4 | 6.1691% | 0.4425% | 0.1984% | 0.1785% |
| identity-0 | 0.2426% | 2.8259% | 0.2335% | 0.5630% |
| cross-0 | 0.1434% | 0.1816% | 3.2135% | 0.3754% |

Identity input 2 fell from about 6.21% leakage in the prior pilot to about 0.23% across all three new contexts. Identity input 5 rose from about 0.14% in its singleton to 1.94% in the forward job and 6.35% in the reverse job. The passing identity input 0 also changed, from 2.83% leakage in its singleton to 0.23% and 0.56% in the packed jobs. These changes are not explained by differences in the returned mesh and input serializations.

The requested-order contrast for identity input 5 has observed total variation 0.0462 and a simultaneous interval [0.0362, 0.0578]; the singleton-versus-reverse contrast has observed total variation 0.0654 and interval [0.0568, 0.0747]. Those intervals describe differences in output distributions under the frozen IID model. Different jobs ran at different times, and packed iteration timestamps are unavailable, so the acquisition cannot assign the differences to physical order, request packing, calibration or drift.

The [parallel analysis successor](../../../results/quandela/ascella-transition-context-parallel-analysis.json)
reconstructs independent entries and comparisons through the repository's ordered process pool. Every
reported value matches the first retained analysis. The [original producer bytes](analysis-sources/context-before-parallel.py)
and original analysis retain their recorded hashes.

The [written case](README.md) freezes 280 endpoints: twenty observations times thirteen output/invalid categories plus one leakage aggregate. Simultaneous 95% Clopper-Pearson coverage is conditional on IID events within each observation. Matching returned mesh metadata does not establish that the hardware applied identical analog controls. Incident pulses and undetected-photon loss remain unmeasured.

The next scoped study varies independent compilation identifiers and physical output permutations beside repeated matched-mesh anchors. Those interventions test whether the observed response follows the setting, returned mesh or physical port across this finite cohort; the measurements alone do not establish a unique physical cause. The original 54-setting expansion remains blocked by the original pilot decision.
