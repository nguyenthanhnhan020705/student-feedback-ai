# Bàn giao CT5 — Nhận trả lời hoặc tạm không kết luận

**Ngày:** 2026-11-01.
**Trạng thái:** Hướng dẫn đề xuất để người dùng chuyển cho agent; chưa triển khai CT5.
Mục tiêu coverage/chất lượng/từ chối đã có ở protocol CT1. Các cấu hình và ranh
giới triển khai dưới đây là đề xuất cụ thể mới, không phải quyết định lịch sử đã duyệt.
Khi người dùng gửi prompt ở cuối file, triển khai mốc A đúng phạm vi; mốc B cần
duyệt riêng vì thay hợp đồng API/UI.

## 1. CT5 giải quyết việc gì?

Mô hình hiện buộc chọn một sentiment và một topic cho mọi input hợp lệ. Câu
vô nghĩa, không có đặc trưng hoặc thiếu đối tượng có thể nhận nhãn trông chắc
chắn dù hệ thống chưa có đủ bằng chứng. CT5 khảo sát **selective prediction**:
nhận trả lời khi có đủ tín hiệu theo một chính sách đã đóng băng; còn lại tạm
không kết luận và đề nghị người dùng diễn đạt rõ hơn.

Đây là cơ chế quản lý rủi ro trả lời, không phải một lần train mới. Không gọi
`neutral` là không chắc chắn, không gọi `other` là ngoài miền. Không chuyển câu
vô nghĩa thành nhãn mẫu. Không diễn đạt SVM margin thành xác suất confidence.
Gate có thể vẫn chấp nhận câu ngoài miền với margin cao; phải đo và công bố lỗi
này. Không tuyên bố đã có bộ phát hiện ngoài miền chỉ vì có margin threshold.

**Từ chối không phải dự đoán đúng.** Accuracy trên phần được nhận có thể tăng
chỉ vì trả lời ít câu hơn. Phải báo đồng thời coverage, lỗi còn lọt và số câu
trả đúng trên toàn bộ đầu vào, không quảng cáo tăng “độ chính xác toàn hệ thống”.

## 2. Vào đúng workspace và đọc đúng tiến độ

Thư mục triển khai:
`D:\N.ThanhNhan\Project_AI\student-feedback-ai\.local-tools\integration-p0`

Đây là linked worktree `feature/integration-p0`, khác checkout ngoài đang ở
`feature/data-preprocessing` và thư mục clone lồng `student-feedback-ai/`.
Giữ toàn bộ dirty work. Không reset/clean, đổi nhánh, tạo lại project hoặc commit
gom công việc của người khác. README integration hiện vẫn ghi CT4 chưa làm;
đây là nội dung cũ được giữ để bảo toàn hash, không phải tiến độ mới nhất.

Đọc trước khi sửa:

1. Hướng dẫn AGENTS/phiên hiện hành và skill using-superpowers.
2. `docs/quality/ct1-protocol.md` và `docs/specs/{mvp,api-contract,data-contract}.md`.
3. `docs/quality/ct2-report.md`, `ct3-report.md`, **`ct4-report.md`**.
4. `reports/evidence/ct4/{README,review}.md`, `full-suite.txt`, `receipt.json`.
   Ledger `ct4-progress.md` còn dòng pending lịch sử; review có mục kết luận cuối.
5. `reports/ct_evaluation.py`, `ct2_class_weights.py`, `ct3_word_char.py`,
   `ct4_augmentation.py` và tests tương ứng.
6. `backend/model_service.py`, `backend/schemas.py`, `frontend/api.js` để hiểu
   giới hạn nhãn hợp lệ/timeout và tránh đổi API 1.0 ngoài phạm vi.

## 3. Các mốc đang có — phải tự kiểm lại trên máy thực thi

- CT1: `reports/evidence/ct1/baseline-v2/` và `.local-tools/ct1-baseline-v2/`.
- CT2 chính thức: `.local-tools/ct2-class-weights/run-2/`.
- CT3 chính thức: `.local-tools/ct3-word-char/run-1/`.
- CT4 chính thức: `.local-tools/ct4-augmentation/run-1/`.
  Research pair: sentiment `ct3parent_aug100`, topic `ct3parent_aug25`, bộ ghép
  được lưu tại `research-selected/`. Không nhầm với hai model demo gốc.
- **Model demo vẫn baseline trong models/**, chưa promote CT2/CT3/CT4.
- Suite CT4 lưu cuối: **306 passed, 0 skipped, 14 known warnings**, 227,62s;
  fresh replay và review cuối đạt, 335/335 preexisting hashes giữ nguyên theo review.
  Đây là bằng chứng cũ, không phải lời khẳng định suite CT5 đã chạy.

Trên validation nguyên bản 1583 câu, các mốc tham khảo:

| Mốc | Sentiment Accuracy / Macro F1 | Topic Accuracy / Macro F1 | Cả hai nhãn đúng |
| --- | --- | --- | --- |
| Original | 91,4719% / 75,2966% | 87,9975% / 75,4173% | 1296/1583 = 81,8699% |
| CT2 | 91,2824% / 77,5003% | 87,8080% / 76,8397% | 1294/1583 = 81,7435% |
| Best through CT3 | 91,0929% / 78,9855% | 87,8080% / 76,8397% | 1291/1583 = 81,5540% |
| Best through CT4 | 91,2824% / 79,7398% | 87,8711% / 76,9484% | 1292/1583 = 81,6172% |

CT4 có stress không dấu tăng mạnh, nhưng stress dùng source validation và nhãn
kế thừa; có sáu overlap sau bỏ dấu với train. Không phải tập độc lập và không
dùng điểm stress để chọn gate. Không trộn điểm test lịch sử vào bảng validation.

## 4. Hai mốc CT5 và quyền triển khai

### Mốc A — Công cụ offline, replay và báo cáo (phạm vi prompt này)

Thêm policy/evaluator nghiên cứu, giữ nguyên classifier và mọi pipeline. Chạy
trên original pair và CT4 research pair, báo đủ các đường trade-off; không tự
chọn bản “để deploy”. Chuẩn bị kết quả và đề xuất hành vi để người dùng review.

Không sửa API/UI đang chạy, không đổi SFAI_MODEL_DIR, không ghi models/. Không
cần dữ liệu gán nhãn mới để bắt đầu viết tests, scoring, policy và đánh giá
development. Thiếu tập độc lập phải ghi rõ phần chưa thể nghiệm thu.

### Mốc B — Tích hợp API/UI (chưa được prompt này cho phép)

API 1.0 bắt buộc trả hai nhãn chuỗi và UI chỉ nhận allowlist; null/abstain/new
label không tương thích. Agent phải chuẩn bị đề xuất version/schema, ví dụ
minh họa có gắn nhãn rõ, thông báo tiếng Việt và kế hoạch migration/tests để
người dùng duyệt riêng trước khi sửa production. Không tự thêm 422/503 cho câu
hợp lệ nhưng gate từ chối: đó là quyết định phân tích, không phải lỗi input/model.
Không nới allowlist hoặc đổi nhãn chuẩn để lách hợp đồng.

## 5. Chính sách offline hữu hạn — đóng băng trước đo

Giữ hai parent pairs **original** và **CT4 research-selected**. Không train,
calibrate classifier, thêm dữ liệu, grid search, ensemble hoặc thêm dependency.
So sánh 5 policies cho mỗi pair:

1. `always_answer`: control, giữ hành vi phân loại cũ cho input hợp lệ.
2. `zero_features`: từ chối cả cặp nếu một task có vector đầu vào hoàn toàn 0.
3. `zero_plus_margin_q05`.
4. `zero_plus_margin_q10`.
5. `zero_plus_margin_q20`.

Với ba policy cuối, lấy điểm decision_function theo classes_ thật, tính
`gap = top1_score - top2_score` riêng mỗi task. Ngưỡng là quantile
0.05/0.10/0.20 của gap trên **threshold-development subset**, theo từng model/task,
dùng NumPy method='linear'. Chỉ dùng rows có vector khác 0 ở task đó; nếu không
có row hợp lệ thì báo không thể tạo threshold, không chế ngưỡng mặc định.
Nhận task khi gap >= threshold và vector khác 0. Nhận cả cặp khi cả hai task nhận.
Không lấy min hai gap thô rồi dùng một ngưỡng chung: thang điểm hai task/model
khác nhau. Không diễn giải quantile 10% thành cam kết joint coverage 90%.

Pipeline word-only và FeatureUnion phải được xử lý đúng: lấy bước biến đổi trước
classifier, kiểm nnz của **vector hoàn chỉnh**. Ghi cả nnz từng nhánh để chẩn
đoán, nhưng không tự reject chỉ vì nhánh word rỗng khi char còn tín hiệu.
Đối chiếu thứ tự classes_ với score columns, shape, finite values và predicted
label. Nonfinite/sai shape/model lỗi là **error cần phát hiện**, không ngụy trang
thành abstention để làm đẹp tỷ lệ trả lời.

Ngưỡng margin chỉ là proxy về độ phân tách. Tốt./emoji/câu ngoài miền có thể
lọt gate; không bổ sung whitelist/blacklist riêng sau khi xem known cases.

### Threshold-development và policy-audit

Không thay official train/validation/test. Chia **nội bộ validation** thành hai
tập vai trò theo nhóm để tránh đo gate trên chính dữ liệu chọn threshold:

- group_key = normalize_text(unaccent(text)), dùng hàm unaccent CT4 đã đóng băng;
- digest = SHA256('ct5-v1|42|' + group_key);
- byte đầu digest < 128 vào threshold-development; còn lại vào policy-audit.

Mọi câu cùng group_key phải cùng phía. Lưu ID/group/hash/số lớp và kiểm giao nhau.
Nếu một phía rỗng hoặc không đủ dữ liệu để tính metric, báo thiếu và giữ công cụ
có thể kiểm thử; không đổi seed/chia lại sau xem điểm. Ghi rõ **cả hai vẫn là
validation đã lộ từ CT1–CT4**, không gọi policy-audit là holdout độc lập mới.
Ghi riêng những group có nhiều nhãn và overlap train/CT4 augmentation; không tự
đổi nhãn, lọc theo lỗi model hoặc tuyên bố hết near-duplicates.

Tính threshold chỉ từ threshold-development, không từ policy-audit/stress/known/
test/final độc lập. Trên policy-audit so always_answer và gated **cùng IDs**.
Replay ungated full validation để đối chiếu các số 1583 dòng lịch sử trong bảng
riêng; không so gate trên n≈800 với ungated 1583 như cùng mẫu số.

Không chọn policy bằng cách maximize accepted accuracy (có thể chỉ còn vài câu).
Xuất đầy đủ coverage–risk table cho cả 5 policies. Chưa có quyết định nghiệp vụ
về mức từ chối chấp nhận được: `recommended_policy = null`, trạng thái
`needs_coverage_risk_decision`, không tự đặt mục tiêu hoặc promote. Người dùng
có thể quyết định trade-off sau khi thấy bảng đo.

## 6. Đầu ra offline và thông báo minh họa

Mỗi row nghiên cứu giữ id/source_group, raw_prediction của cả hai task,
nnz/gap/threshold, accepted từng task, accepted_pair, reasons và labels_for_display.
Khi accepted_pair=false thì labels_for_display=null cho **cả hai**, giữ nguyên
raw_prediction nội bộ cho audit; không trả nhãn nửa chừng. Không sửa hoặc ghi
đè labels_for_display trong response API 1.0 đang chạy.

Reason kỹ thuật: `zero_features_sentiment`, `zero_features_topic`,
`low_margin_sentiment`, `low_margin_topic`. Không đổi thành thông báo chắc chắn
“câu này ngoài miền” hay “câu vô nghĩa” nếu chưa có bằng chứng tương ứng.

Ví dụ thông báo đề xuất cho mốc B: “Hệ thống chưa đủ cơ sở để kết luận cả cảm
xúc và chủ đề. Bạn có thể nêu rõ nội dung và đối tượng được nhận xét hơn.”
Không quảng cáo cơ chế hiểu đúng câu ngoài miền, không ép người dùng viết câu
theo mẫu để đạt nhãn mong muốn.

## 7. Metrics bắt buộc — không đánh tráo mẫu số

Trên cùng tập có nhãn hai task, đặt N=tổng input, A=số nhận cả cặp,
C=số nhận và cả hai nhãn đúng, E=A−C, R=N−A:

- pair coverage = A/N; abstention rate = R/N.
- accepted joint accuracy = C/A; selective risk = E/A; A=0 thì null.
- **correct-and-answered rate = C/N**; answered-wrong rate = E/N.
- rejected-but-originally-correct count/rate: những câu nếu trả nhãn thô thì
  đúng cả hai nhưng bị từ chối; rejected-originally-wrong riêng.
- N = C + E + rejected-but-correct + rejected-but-wrong phải đúng.
- Per-task coverage/accepted Accuracy, Macro F1, per-class P/R/F1/support;
  thêm per-task metrics trên pair-accepted subset, ghi rõ mẫu số và label order.
- Ungated original/CT4 metrics trên **cùng IDs**; raw predictions không thay khi
  chỉ đổi policy. Cùng một frozen model, C/N không thể cao hơn ungated correct/N:
  gate chỉ bỏ bớt câu, không sửa nhãn. Nếu báo tăng phải điều tra tính toán.
- Model change và gating effect tách riêng: original→CT4 ungated là một phép
  so sánh; CT4 ungated→CT4 gated là phép khác, không gộp thành công lao của gate.

Ví dụ tính toán, **không phải kết quả CT5**: 100 câu, nhận 80, đúng 72 → coverage
80%, accepted accuracy 90%, correct-and-answered 72%. Không được nói hệ thống
đúng 90% trên cả 100 câu hoặc tính 20 câu từ chối thành đúng.

Với known cases hoặc input không đủ ground truth, null phải loại khỏi mẫu số
đúng/sai nhưng vẫn tính được coverage trên tập input; không dùng mẫu số 39 cho
joint correctness khi chỉ 25 ca có đủ hai kỳ vọng. Stress không dấu/emoji/ngoài
miền phải báo riêng từng nhóm, không gộp tỷ lệ nhân tạo thành traffic thực.

## 8. Cần dữ liệu gì để đánh giá từ chối nhầm và ngoài miền?

Canonical sentiment/topic không đủ làm ground truth cho “có nên nhận trả lời”.
Cần nhãn riêng cho từng task: `answerability = answerable|unanswerable|ambiguous`,
nhãn kỳ vọng có thể null, nguồn, group_id, reviewer provenance và lý do.
Không lấy việc model đoán sai để tự gán câu đó là unanswerable. `other` vẫn có
thể là câu trong miền hợp lệ. Một câu ngoài miền có thể có cảm xúc rõ nhưng
thiếu topic theo ontology; phải đánh giá cả cặp đúng theo quy tắc mục 6.

Cho phép tạo fixture tự viết để chứng minh logic tests, và challenge đề xuất
có provenance `assistant_proposed`; không coi đó là dữ liệu được người rà độc lập.
Không tự tạo tên người gán nhãn hoặc tuyên bố đã có dataset mới.

Theo CT1, cần nhóm/người đánh giá khác thu tập phản hồi tự nhiên được phép dùng,
không xem model outputs khi gán nhãn, hai người rà và giải quyết bất đồng. Tập
tự nhiên và challenge ngoài miền/emoji/mơ hồ tách riêng. Đề xuất CT1 khoảng
200 câu tự nhiên và cố gắng có 30 mẫu mỗi lớp ít gặp là kế hoạch thực dụng,
không phải bảo đảm thống kê. Ghi support và độ bất định; không tự đặt ngưỡng đạt.

Tách dữ liệu mới dùng phát triển gate khỏi final độc lập theo source groups;
kiểm exact/near-duplicates với corpus/known/stress/augmented. Người giữ final
đóng băng text/nhãn/hash và không mở model results trước khi policy/config chốt.
Nếu thay policy theo final, tập đó đã thành development, không còn là final mù.

Trên phần được gán answerability rõ ràng, báo riêng:

- false reject = rejected answerable / tất cả answerable;
- unsafe accept = accepted unanswerable / tất cả unanswerable;
- precision of abstention = rejected unanswerable / tất cả rejected có nhãn rõ;
- accepted accuracy trên các câu thực sự answerable, theo task và cả cặp.

Ambiguous báo riêng; denominator=0 trả null. Không gọi rejected-but-correct ở
validation là bằng chứng đã đo false reject về mặt ngữ nghĩa. Không suy ra
ngoài miền chỉ từ low margin hoặc từ phép đo “model thô sai”.

**Nếu thiếu tập mới/người rà/đầu vào nghiệp vụ:** vẫn hoàn tất engine, tests,
development run/replay và báo cáo; trạng thái cuối
`engineering_complete_independent_evaluation_pending`. Ghi rõ danh sách còn
thiếu, không bịa dữ liệu, không chạy lại test cũ để gọi là tập mới và không coi
toàn bộ CT5/nghiệm thu độc lập đã hoàn tất. Không chặn phần kỹ thuật chỉ vì
chưa có final set, và cũng không vượt qua phần đánh giá độc lập bằng giả định.

## 9. Code, bằng chứng và kiểm thử

Đường dẫn dự kiến, tương đối với integration-p0:

- `reports/ct5_selective_prediction.py`: extract scores/features, policies,
  grouped split, thresholds, evaluation, CLI run/verify. Module hỗ trợ chỉ khi cần.
- `tests/test_ct5_selective_prediction.py`.
- `docs/quality/ct5-report.md` và `docs/quality/ct5-data-requirements.md`.
- Kế hoạch dưới `docs/superpowers/plans/` dùng ngày thực thi, ledger `ct5-progress.md`.
- `reports/evidence/ct5/`: config, policies/thresholds, metrics, per-row decisions,
  data/answerability status, control hashes, logs, review, receipt.
- `.local-tools/ct5-selective-prediction/<fresh-run>/`: artifacts local; refuses
  live/existing/overlapping outputs, symlink/junction ra ngoài research.

TDD trước code; tests phải có:

1. Word-only, FeatureUnion, word nnz=0/char nnz>0, cả vector=0, classes_ đảo thứ tự.
2. Score gap đúng, tie/boundary gap==threshold, nonfinite/wrong shape/model error.
3. Quantile method và ngưỡng task/model riêng; threshold chỉ học development;
   groups/biến thể không cắt sang audit, subset rỗng và calibration no-signal.
4. Accepted cả cặp/all-or-nothing, raw labels giữ nguyên, reason/null display đúng.
5. Hand-derived coverage/risk/C/N, rejected correct/wrong, null denominator,
   missing classes/support, per-task versus pair-accepted metrics và consistency sums.
6. Truthless/ambiguous/OOD cases không bị tự gán neutral/other/answerability.
7. Fixture lifecycle bằng serialized pipelines thật, **không có test split trên
   disk**; run/replay không fit/retrain, không đổi bất cứ model/control nào.
8. Tamper model/config/source/split/threshold/labels/metrics/payload/receipt,
   incomplete run và exact payload membership (kể cả nested receipt.json).

Receipt phải bind source/runtime, control/model hashes, group partition, policy
config, thresholds và nguồn nhãn, toàn bộ payload và trạng thái deployment;
kiểm schema_version/promotion bằng giá trị rõ ràng. Replay tiến trình mới không
fit tái tạo group/subset/threshold/score/acceptance/metrics chính xác. Không sửa
runner/receipt CT1–CT4 để khiến control verification qua được.

Trước full suite, inventory file hiện có. Browser tests có thể ghi đè ảnh minh
chứng cũ: backup đúng bytes, giữ bản mới trong evidence CT5 và phục hồi bản cũ
nếu thay đổi; kiểm hash sau. Không ghi đè bằng chứng thành viên hoặc dự án khác.

```powershell
$env:TV2_RUN_REAL_DATA='1'
./.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider
./.venv/Scripts/python.exe -B -m pip check
```

Đọc kết quả cuối/exit code, không coi skip là nghiệm thu. Full-suite có thể
kiểm artifact/test lịch sử; runner CT5 không đọc test để chọn policy/threshold.
Không nâng dependency chỉ để xóa warnings. Review độc lập trước bàn giao; ghi
rõ findings đã sửa/còn hoãn, không bịa một lượt review hay full-suite mới.

## 10. Báo cáo và điều kiện dừng

Báo cáo phải cho thấy: control actual hashes, dataset roles và overlap;
coverage–risk table của 5 policies trên mỗi pair; mẫu số cùng IDs; ungated
full-validation riêng; model effect khác gate effect; errors và rejection
reasons; known/stress tách riêng; false reject/unsafe accept chỉ khi có nhãn
answerability thật; phạm vi development/final; tests/replay/review thực tế.

Không cần tìm được một policy tốt hơn để hoàn tất nghiên cứu kỹ thuật. Nếu
coverage giảm mạnh hoặc accepted risk không giảm, ghi kết quả âm. Không mở
rộng threshold sau xem điểm để kiếm số đẹp. Nếu final data hoặc quyết định
coverage/risk chưa có, ghi đúng trạng thái pending theo mục 8; không promote.

Không thêm CT6/Phase 6, batch/Dashboard, LLM/PhoBERT, sửa corpus, API/UI, training,
thu thập ngoài scope, email/slack, upload dataset/model, commit/push/merge hay
thay model demo. Quyền nguồn vẫn unknown; chỉ trusted local artifacts.

## 11. Prompt để người dùng gửi agent

```text
Thực hiện CT5 mốc A theo file:
D:\N.ThanhNhan\Project_AI\student-feedback-ai\.local-tools\integration-p0\docs\quality\ct5-agent-handoff.md

Tôi chọn hướng selective prediction offline trong file: gate zero features và
margin, đo coverage/risk, đối chiếu original và CT4 với cùng dữ liệu. Đọc kỹ
file, protocol CT1, báo cáo/bằng chứng CT4 và hợp đồng API trước khi sửa. Làm
trên linked worktree integration-p0, bảo toàn dirty work và CT1–CT4.

Lập kế hoạch, tests trước code, triển khai engine, finite development run,
fresh replay không fit, full suite, preservation và review. Tự quyết lựa chọn
nhỏ trong phạm vi mô tả, ghi ledger. Không tự chọn chính sách deployment,
thay model hoặc sửa API/UI: mốc B cần tôi duyệt hợp đồng riêng.

Kết quả phải tách coverage, accepted accuracy, selective risk và số câu trả
đúng trên toàn input. Không tính câu từ chối thành đúng hoặc margin thành
confidence. Thiếu final set/answerability được người rà thì vẫn làm phần kỹ
thuật và ghi independent_evaluation_pending, không bịa dữ liệu/kết quả.
Không tự triển khai Phase 6, commit/push/merge hay publish dữ liệu/model.
```
