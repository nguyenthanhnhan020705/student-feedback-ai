# CT3 — validation development comparison

No test inference. Serving models unchanged. Deltas are percentage points.

| Task | Variant | Accuracy | Macro F1 | Delta Accuracy vs original (pp) | Delta F1 vs original (pp) |
| --- | --- | ---: | ---: | ---: | ---: |
| sentiment | baseline | 91.4719% | 75.2966% | +0.0000 | +0.0000 |
| sentiment | ct2 | 91.2824% | 77.5003% | -0.1895 | +2.2037 |
| sentiment | char_0.5_none | 91.4719% | 76.5377% | +0.0000 | +1.2411 |
| sentiment | char_0.5_ct2 | 91.2192% | 77.3625% | -0.2527 | +2.0659 |
| sentiment | char_1_none | 91.4087% | 78.0481% | -0.0632 | +2.7515 |
| sentiment | char_1_ct2 | 90.9665% | 77.8145% | -0.5054 | +2.5179 |
| sentiment | char_2_none | 91.0929% | 78.9855% | -0.3790 | +3.6889 |
| sentiment | char_2_ct2 | 90.5875% | 77.3278% | -0.8844 | +2.0311 |
| topic | baseline | 87.9975% | 75.4173% | +0.0000 | +0.0000 |
| topic | ct2 | 87.8080% | 76.8397% | -0.1895 | +1.4224 |
| topic | char_0.5_none | 87.7448% | 75.8953% | -0.2527 | +0.4780 |
| topic | char_0.5_ct2 | 87.4289% | 76.8175% | -0.5685 | +1.4002 |
| topic | char_1_none | 87.4921% | 76.3488% | -0.5054 | +0.9315 |
| topic | char_1_ct2 | 86.6709% | 75.7781% | -1.3266 | +0.3608 |
| topic | char_2_none | 87.0499% | 76.0965% | -0.9476 | +0.6792 |
| topic | char_2_ct2 | 86.1023% | 74.6627% | -1.8951 | -0.7546 |

All-control selection: {'sentiment': 'char_2_none', 'topic': 'ct2'}
CT3-only selection: {'sentiment': 'char_2_none', 'topic': 'char_0.5_ct2'}

| Pair | Both correct | Joint accuracy | Delta vs original (pp) |
| --- | ---: | ---: | ---: |
| original | 1296/1583 | 81.8699% | +0.0000 |
| ct2 | 1294/1583 | 81.7435% | -0.1263 |
| ct3_only | 1286/1583 | 81.2382% | -0.6317 |
| research_selected | 1291/1583 | 81.5540% | -0.3159 |

Known-case labels remain provisional, assistant-authored and non-independent.
See results.json for per-class deltas, every regression and relative percentage changes.
This research result is not a serving deployment or independent final evaluation.
