# Ascella transition mesh and output-port findings

Six Ascella jobs completed 132 settings with 8,650,752 accepted events in 407 provider seconds. The [analysis](../../../results/quandela/ascella-transition-mesh-port-analysis.json) binds every result, request, returned mesh and input. Each of the fifteen setting and output-map groups contains eight distinct returned new meshes with no within-group or prior-mesh collisions. All twelve matched anchors have the same returned mesh and input serialization as their respective singleton references.

| Setting | Original map leakage | Logical swap leakage | Outer swap leakage |
|---|---:|---:|---:|
| Identity input 2 | 1.76% | 1.81% | 0.72% |
| Identity input 5 | 2.44% | 0.22% | 0.48% |
| Fourier-to-chirped input 4 | 0.94% | 2.25% | 0.93% |
| Identity input 0 | 0.46% | 0.73% | 0.50% |
| Fourier-to-chirped input 0 | 0.70% | 1.76% | 1.50% |

Each entry is the mean over eight distinct returned meshes in the finite cohort, with 65,536 accepted events per mesh. The [written case](README.md) defines the output mappings and freezes simultaneous 95% intervals across 1,876 endpoints, assuming IID accepted events within each observation. The analysis retains individual counts, invalid-event categories, intervals and all twelve ports. Incident pulses and undetected loss remain unknown.

For identity input 5, changing the output map coincided with lower mean leakage. The map also changes the compiled operator, so the result cannot isolate a physical detector or port as the cause. Matched identity-input-0 anchors differ from their singleton reference: four of six total-variation intervals have positive lower bounds, with point estimates from 1.22% to 4.64%. Identity-input-2 anchor intervals all include zero. Returned serialization establishes a digital match, while applied analog settings and calibration can differ. Time, output mapping and mesh therefore remain potential confounders.

The selected settings came from an earlier screening pilot. The cohort diagnoses those settings; it does not qualify the 54-setting campaign or prove a bound on mutually unbiased bases. A time-separated matched-mesh repeat and a fresh, prospectively specified qualification cohort remain necessary for those separate questions.
