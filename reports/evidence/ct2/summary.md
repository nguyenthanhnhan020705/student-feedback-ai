# CT2 — validation development results

Class weighting only; historical test not evaluated. Serving models unchanged.

| Task | Variant | Accuracy | Macro F1 | Delta Accuracy (pp) | Delta F1 (pp) |
| --- | --- | ---: | ---: | ---: | ---: |
| sentiment | baseline | 91.4719% | 75.2966% | +0.0000 | +0.0000 |
| sentiment | sqrt_balanced | 91.3455% | 75.9336% | -0.1263 | +0.6370 |
| sentiment | balanced | 91.2824% | 77.5003% | -0.1895 | +2.2037 |
| sentiment | minority_x2 | 91.2824% | 74.9305% | -0.1895 | -0.3661 |
| topic | baseline | 87.9975% | 75.4173% | +0.0000 | +0.0000 |
| topic | sqrt_balanced | 87.8080% | 76.8397% | -0.1895 | +1.4224 |
| topic | balanced | 86.7340% | 76.2587% | -1.2634 | +0.8414 |
| topic | minority_x2 | 87.9975% | 76.0656% | +0.0000 | +0.6483 |

Validation rank leaders (research only): {'sentiment': 'balanced', 'topic': 'sqrt_balanced'}

Full per-class deltas and every changed/regressed ID: results.json.
Known-case labels are assistant-proposed, not human-reviewed; null remains unscored.
No independent final dataset; no deployment or broad quality claim.
