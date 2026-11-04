# CT5 offline development — no policy recommended

Both partitions are exposed validation; margin is not probability. Rejected inputs are not correct.

| Pair / policy (same policy-audit IDs) | N | A | C | E | Coverage | Accepted accuracy | Risk | C/N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| original/always_answer | 791 | 791 | 653 | 138 | 100.0000% | 82.5537% | 17.4463% | 82.5537% |
| original/zero_features | 791 | 789 | 653 | 136 | 99.7472% | 82.7630% | 17.2370% | 82.5537% |
| original/zero_plus_margin_q05 | 791 | 704 | 613 | 91 | 89.0013% | 87.0739% | 12.9261% | 77.4968% |
| original/zero_plus_margin_q10 | 791 | 635 | 571 | 64 | 80.2781% | 89.9213% | 10.0787% | 72.1871% |
| original/zero_plus_margin_q20 | 791 | 520 | 490 | 30 | 65.7396% | 94.2308% | 5.7692% | 61.9469% |
| ct4/always_answer | 791 | 791 | 649 | 142 | 100.0000% | 82.0480% | 17.9520% | 82.0480% |
| ct4/zero_features | 791 | 789 | 648 | 141 | 99.7472% | 82.1293% | 17.8707% | 81.9216% |
| ct4/zero_plus_margin_q05 | 791 | 702 | 605 | 97 | 88.7484% | 86.1823% | 13.8177% | 76.4855% |
| ct4/zero_plus_margin_q10 | 791 | 646 | 574 | 72 | 81.6688% | 88.8545% | 11.1455% | 72.5664% |
| ct4/zero_plus_margin_q20 | 791 | 531 | 494 | 37 | 67.1302% | 93.0320% | 6.9680% | 62.4526% |

Status: engineering_complete_independent_evaluation_pending.
Decision: needs_coverage_risk_decision; recommended_policy=null; not_deployed.
