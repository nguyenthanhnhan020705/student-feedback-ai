# CT4 demo with independent task decisions — selected user scope

User requested implementation of independent sentiment/topic decisions and applying
CT4 to the demo; negation is explicitly deferred. This authorizes a new demo/API
behavior beyond milestone A; no classifier training, Phase6, Git integration or
publication requested. Unknown information must not become a false neutral/other label.

## Approach and choices

Selected: CT4 research-selected frozen pair, CT5 q10 zero-feature/margin thresholds,
decide each task independently, nullable label with explicit per-task status.
q10 is the implementer's provisional demo setting, not an independently validated
production policy. The user's selected purpose supplies implementation approval;
no repeat permission gate. No per-example keyword fixes or threshold tuning.

Alternative automatic neutral/other fallback masks uncertainty and is not selected.
Overwriting v1 files/artifacts breaks frozen CT1–CT5 source inventories; use a new
demo_v2 package and frontend on port8001. Existing baseline8000 and all controls
remain unchanged and reproducible. No aspect splitting or new negation rule.

## API and behavior

POST /api/v2/predict accepts raw strict text (nonblank, <=5000 Unicode code points,
no lone surrogates, no extra fields). HTTP200 even when one/both tasks abstain.
Each task returns status=answered/insufficient_information, canonical label or null,
and user message for insufficient. Overall status=complete/partial/insufficient.
No half result on model/inference error; those remain503/500. Input error422.
All envelopes contract_version2.0. GET /api/health reports CT4 readiness.
No new response schema at v1; original app is unchanged on8000.

Model and threshold sources bind to CT5 receipt/config hashes, CT4 receipt/hash and
actual model+metadata/runtime, read only. Invalid/missing files leave service not ready.
Policy requires complete feature-vector nnz>0 and finite gap>=own task q10 threshold.
Char-only signals are valid. Model errors/nonfinite scores/gaps remain errors.
Public response never exposes raw withheld labels, scores or confidence percentages.

UI renders each part independently and shows missing information explicitly;
keeps input, clears stale output, disables duplicate submit,10s deadline covers
body. No mock fallback or unsafe HTML. Small note identifies CT4 trial and retained
limits for negation/multiple subjects. Layout inherits existing plain HTML/CSS style.

## Verification and limits

Test first: unit task gate boundary/finite errors; API fixtures and actual CT4;
tampered/missing models/thresholds;5000/5001/blank/Unicode; browser partial/full/
insufficient and failures on Chrome/Edge. Record actual sample predictions and
validation coverage/conditional metrics with unchanged denominators, no new final claim.
Fresh frozen-chain no-fit replay, full regression, preexisting hashes and independent
review. New demo handles task uncertainty heuristically; q10 is not a semantic/OOD
detector and may retain wrong labels, including negation and mixed subjects.
