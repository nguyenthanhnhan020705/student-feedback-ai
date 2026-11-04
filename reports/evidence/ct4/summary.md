# CT4 validation research results

| Pair | Sentiment Accuracy | Sentiment Macro F1 | Topic Accuracy | Topic Macro F1 | Joint |
| --- | ---: | ---: | ---: | ---: | ---: |
| original | 91.4719% | 75.2966% | 87.9975% | 75.4173% | 1296/1583 (81.8699%) |
| ct2 | 91.2824% | 77.5003% | 87.8080% | 76.8397% | 1294/1583 (81.7435%) |
| ct3 | 91.0929% | 78.9855% | 87.8080% | 76.8397% | 1291/1583 (81.5540%) |
| original_aug25 | 91.3455% | 75.3208% | 87.8080% | 75.3023% | 1290/1583 (81.4908%) |
| original_aug50 | 91.4087% | 75.3630% | 87.8711% | 75.3764% | 1292/1583 (81.6172%) |
| original_aug100 | 91.5982% | 75.6109% | 87.9343% | 75.6978% | 1294/1583 (81.7435%) |
| ct3parent_aug25 | 91.2824% | 79.7354% | 87.8711% | 76.9484% | 1292/1583 (81.6172%) |
| ct3parent_aug50 | 91.1560% | 78.8858% | 87.6816% | 76.7727% | 1285/1583 (81.1750%) |
| ct3parent_aug100 | 91.2824% | 79.7398% | 87.5553% | 76.6436% | 1288/1583 (81.3645%) |
| ct4_selected | 91.2824% | 79.7398% | 87.8711% | 76.9484% | 1292/1583 (81.6172%) |
| research_selected | 91.2824% | 79.7398% | 87.8711% | 76.9484% | 1292/1583 (81.6172%) |

All-control selection: {'sentiment': 'ct3parent_aug100', 'topic': 'ct3parent_aug25'}
CT4-only selection: {'sentiment': 'ct3parent_aug100', 'topic': 'ct3parent_aug25'}

Selection uses original validation Macro F1; stress/known cases are separate diagnostics.
No serving model replacement; validation is repeatedly exposed, not an independent final test.
