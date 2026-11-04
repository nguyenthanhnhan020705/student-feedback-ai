# Bàn giao CT4 cho agent triển khai

**Ngày:** 2026-10-31.
**Trạng thái:** Đề xuất CT4 để người dùng chuyển giao; chưa triển khai CT4.
Trong tài liệu cũ chưa có đặc tả CT4 cụ thể đã duyệt. Không diễn giải tài liệu
này thành một quyết định lịch sử của người dùng. Khi người dùng gửi prompt
triển khai kèm file này, thực hiện đúng phạm vi dưới đây.

## 1. Mục tiêu

Thử **data augmentation có kiểm soát: thêm biến thể không dấu từ train** để
khảo sát độ bền với phản hồi không dấu, đồng thời kiểm tra tỷ lệ trả đúng tổng
thể có tăng hay giảm. Đây là thí nghiệm offline; không hứa trước phần trăm tăng.
Không thêm quy tắc đoán nhãn theo từ khóa hoặc vá riêng các câu đã biết.

CT2 cải thiện mất cân bằng lớp; CT3 thử đặc trưng từ + ký tự. Cả hai có cải thiện
Macro F1 nhưng chưa tăng joint accuracy. CT4 đề xuất khảo sát dữ liệu đầu vào
thay vì mở rộng tiếp việc dò hyperparameter. Chọn augmentation không dấu vì
có thể tái lập từ train sẵn có, không cần bịa phản hồi hoặc nhãn mới.

Đây là phép thử có giới hạn: bỏ dấu có thể làm câu mơ hồ/đổi nghĩa; nhãn kế thừa
là giả định weak supervision, không phải nhãn đã được con người xác nhận cho
từng câu biến đổi. Nếu có dữ liệu thật mới, phải có nguồn/quyền dùng, rà nhãn,
chia nhóm và đóng băng riêng; việc thu thập đó không tự nằm trong CT4 này.

## 2. Vào đúng bản dự án

Checkout ngoài:
`D:\N.ThanhNhan\Project_AI\student-feedback-ai`

**Thư mục triển khai thực tế:**
`D:\N.ThanhNhan\Project_AI\student-feedback-ai\.local-tools\integration-p0`

Nhánh `feature/integration-p0`, linked worktree. Có nhiều thay đổi chưa commit
từ các thành viên và các lần tích hợp. Không reset/clean, đổi nhánh, chép đè
checkout, tạo lại dự án hoặc gom toàn bộ dirty work thành commit.
README ở checkout ngoài có thể chậm tiến độ; ưu tiên ledger của bản tích hợp.

Chỉ dẫn đường dẫn bên dưới là tương đối với **bản tích hợp**.

## 3. Đọc trước khi sửa

1. AGENTS.md/hướng dẫn phiên hiện hành và skill using-superpowers.
2. `docs/quality/ct1-protocol.md`: vai trò các tập và quy tắc đánh giá.
3. `docs/quality/ct2-report.md`, `docs/quality/ct3-report.md`.
4. `docs/superpowers/plans/ct3-progress.md` và `course-demo-progress.md`.
5. `reports/ct_evaluation.py`, `reports/ct2_class_weights.py`,
   `reports/ct3_word_char.py` cùng tests tương ứng.
6. `ml/data.py`, `ml/preprocessing.py`, `ml/labels.py`,
   `backend/model_service.py`, `docs/specs/data-contract.md`.

## 4. Trạng thái và các mốc đối chiếu

- App: FastAPI + HTML/CSS/JS, hai pipeline local; một nhãn cảm xúc và một nhãn
  chủ đề/câu. Demo đang dùng baseline gốc; không có confidence.
- Train 11426, validation 1583; test 3166 là tập lịch sử đã xem nhiều lần.
- CT1 chính thức: `reports/evidence/ct1/baseline-v2/` và
  `.local-tools/ct1-baseline-v2/`; 49 đầu vào được bảo vệ.
- CT2 chính thức: `.local-tools/ct2-class-weights/run-2/`;
  run-1 là lịch sử. Research selection: sentiment balanced, topic sqrt_balanced.
- CT3 chính thức: `.local-tools/ct3-word-char/run-1/`.
  Research selection: sentiment char_2_none, topic giữ CT2.
  CT3-only selection khác: sentiment char_2_none, topic char_0.5_ct2.
- Suite gần nhất được lưu: **281 passed, 0 skipped, 14 known warnings**.
  Đây là bằng chứng lịch sử; phải chạy kiểm chứng cho phần CT4 trước khi kết luận.

Các điểm validation đã biết để phát hiện nhầm control, không dùng để tự tạo metrics:

| Mốc | Accuracy cảm xúc | Macro F1 cảm xúc | Accuracy chủ đề | Macro F1 chủ đề | Joint |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original | 91,4719% | 75,2966% | 87,9975% | 75,4173% | 1296/1583 |
| CT2 research | 91,2824% | 77,5003% | 87,8080% | 76,8397% | 1294/1583 |
| Best through CT3 | 91,0929% | 78,9855% | 87,8080% | 76,8397% | 1291/1583 |

Original trong bảng là **validation**, không phải các điểm test 89,70%/86,17%.
Không trộn split khi so sánh phần trăm. Không gán lợi ích Topic CT2 cho CT3.

## 5. Thí nghiệm CT4 hữu hạn — đóng băng trước khi xem điểm

### Augmentation

Tạo biến thể bằng hàm riêng thuộc CT4: Unicode NFC → NFD → bỏ combining marks
→ đ/Đ thành d/D → NFC. Giữ chữ số, dấu câu, emoji, khoảng trắng và case còn lại;
normalizer chính thức vẫn xử lý bên trong pipeline như trước.

Không sửa `ml.preprocessing.normalize_text`, loader hoặc corpus gốc. Không xóa
câu gốc; thêm tối đa một bản không dấu cho mỗi source row được chọn. Câu biến đổi
không khác câu gốc thì không thuộc tập đủ điều kiện. Ghi rõ trường hợp nhiều
câu nguồn biến thành cùng một text, nhãn mâu thuẫn hoặc dữ liệu vốn không dấu.
Không tự đổi nhãn hay deduplicate corpus chính thức.

Các bản thêm kế thừa hai nhãn từ chính source train, có ID riêng và parent_id,
method/version/seed. Không đưa cột parent_id thành feature. Đừng giả vờ đây là
các quan sát độc lập mới; phải báo số source group lẫn số training rows.

Ba mức thêm: **25%, 50%, 100% các source train đủ điều kiện**. Chọn xác định bằng
sắp xếp SHA-256 của `ct4-v1|42|<source-id>`, lấy floor(ratio × số đủ điều kiện).
Các mức lồng nhau, không chọn theo dự đoán hoặc nhãn validation.

### Hai cặp parent cố định

1. Hai pipeline original trong `models/`.
2. Cặp `research-selected/` chính thức của CT3 (bao gồm Topic CT2).

Clone thành pipeline chưa fit; fit lại trên train augmented. Giữ nguyên mọi
tham số của parent, bao gồm class_weight nếu có; **không tính lại class_weight
từ số dòng augmented**, để không trộn hai thay đổi trong cùng phép thử. Ghi
thẳng giới hạn này; trọng số CT2 vốn được suy ra từ train gốc.

Hai parent × ba mức = **sáu cặp ứng viên / 12 lần fit**. Không dò thêm C, ngram,
class_weight, oversampling hay seed sau khi xem điểm. Nếu cần mở rộng, đề xuất
đợt nghiên cứu mới; không lặng lẽ thêm cấu hình. Không fit lại controls không
augmentation chỉ để làm lại CT1–CT3; tải và replay các mốc đã đóng băng.

Đặt tên tường minh, ví dụ `original_aug25`, `ct3parent_aug50`; phải ghi rõ
parent thực tế của từng task, vì CT3 research pair là một bộ ghép.

## 6. Chia dữ liệu và đánh giá

- Chỉ sinh dữ liệu huấn luyện từ **train**. Mọi biến thể cùng parent_id ở cùng
  một nhóm. Không chia lại official splits hoặc chuyển câu đánh giá vào train.
- Validation nguyên bản là development set để xếp hạng theo protocol CT1.
- Có thể tạo thêm bản không dấu của validation **chỉ để đo robustness**, tách
  khỏi train hoàn toàn và không dùng chọn cấu hình. Báo đây là synthetic stress
  set cùng source groups, giả định kế thừa nhãn; không coi là đánh giá độc lập.
  Nếu không tạo stress set, phải nêu CT4 chưa đo trực tiếp khả năng không dấu.
- 39 known cases chỉ kiểm chẩn đoán/hồi quy; nhãn assistant_proposed, null không
  tính đúng/sai. Không dùng để chọn model hoặc biến câu sai thành dữ liệu train.
- Không đọc/suy luận test trong runner CT4 hoặc dùng test để đổi cấu hình.
  Full regression suite hiện có có thể chứa kiểm chứng artifact/test lịch sử;
  tách rõ log đó, không đưa điểm test vào báo cáo xếp hạng CT4.
- Kiểm và báo exact normalized overlap/augmentation collisions với validation
  và known cases, kể cả overlap sau bỏ dấu. Chỉ so bằng text, không chọn/xóa
  train theo nhãn hoặc lỗi dự đoán validation. Không tự sửa validation; nếu phát
  hiện bất đồng nhãn nghiêm trọng phải nêu ảnh hưởng trước khi kết luận.
- Không tuyên bố near-duplicate-free chỉ từ exact hashes. Chưa có tập mới được
  gán nhãn độc lập; không bịa tên người rà, quyền sử dụng hay kết quả.

### Xếp hạng và kết luận

Giữ đúng tiêu chí nghiên cứu CT1: Macro F1 từng task → Accuracy, dung sai 1e-6
tính từ cực đại cố định. Bao gồm original, CT2, CT3 research controls; hòa giữ
control đơn giản/cũ trước rồi thứ tự ứng viên khai báo. Không so hòa dây chuyền.
Ghi cả CT4-only winner và winner gồm controls; đánh giá lại cặp ghép bằng hai
pipeline thật, không suy ra joint từ trung bình Accuracy.

Người dùng quan tâm “trả lời chính xác hơn”. **Không đổi lén tiêu chí xếp hạng
thành joint/Accuracy**, cũng không lấy Macro F1 tăng để trả lời rằng Accuracy
tăng. Báo riêng cả hai; nếu Macro F1 tăng mà joint giảm thì kết luận đúng là
có đánh đổi, chưa tăng tỷ lệ trả đúng tổng thể. Không tự đặt ngưỡng đạt với giảng
viên và không tự thay model demo theo bất cứ điểm xếp hạng nào.

## 7. Code và đầu ra dự kiến

Thêm công cụ offline, bám theo cấu trúc CT2–CT3:

- `reports/ct4_augmentation.py`: transform, chọn nhóm, fit, evaluate, CLI run/verify.
- `tests/test_ct4_augmentation.py`: kiểm hành vi và lifecycle thật với fixture nhỏ.
- `docs/quality/ct4-report.md`: phương pháp, kết quả, lợi ích/tổn thất, giới hạn.
- `docs/superpowers/plans/2026-<ngày-thực-hiện>-ct4-augmentation.md`: kế hoạch
  chi tiết trước code; dùng ngày thực tế, không sao chép mù placeholder này.
- `docs/superpowers/plans/ct4-progress.md`: ledger liên tục.
- `reports/evidence/ct4/`: logs RED/GREEN, config, metrics, provenance, receipt,
  replay, bảo toàn các mốc, full-suite, pip check, review.
- `.local-tools/ct4-augmentation/<fresh-run>/`: research artifacts và dữ liệu
  augmented nếu cần. Không ghi đè run cũ. Dữ liệu/model chỉ local.

Không sửa code CT1–CT3 để làm snapshot cũ verify được. Tái sử dụng hàm scoring
và compare phù hợp; clone được cả pipeline word-only lẫn FeatureUnion. Các control
phải replay bằng nguồn/runtime tương ứng. Kiểm cả source hashes và receipt
semantics, không lặp minor CT3: kiểm schema_version/promotion của receipt CT4.
Minor cũ của CT3 chỉ ghi nhận; không sửa runner CT3 làm vô hiệu run-1.

### Manifest/metadata/replay tối thiểu

- Config hữu hạn, counts source/augmented theo task/lớp, seed, selection policy.
- Parent artifact/metadata hash, source train hash, code/version và môi trường.
- Map augmentation ID → parent_id, transform/version; checksum dữ liệu thêm.
- Pipeline hoàn chỉnh, metadata mô tả **đúng dataset training augmented**. Giữ
  original source manifest hash riêng, thêm augmented manifest/hash rõ ràng;
  không gán bộ augmented là original 11426 rows hoặc gọi nhãn kế thừa là human-reviewed.
- Mọi payload checksum, selection, fit time/warnings, provenance và chính sách
  `research_only`/`not_deployed`. Receipt tạo cuối; run thiếu receipt là chưa hoàn tất.
- Replay ở tiến trình mới **không fit**: tái tạo danh sách source được chọn,
  biến đổi/checksum, effective params, training vocabulary/IDF của từng nhánh
  và classifier class weights; tải lại dự đoán/metrics/ranking/deltas chính xác.
- Mỗi task có baseline/control/candidate metrics, per-class/support/matrix,
  prediction rows và improved/regressed/changed IDs, cả wrong→wrong.
- Thử readiness qua ModelService với contract 1.0; không đổi hợp đồng dùng chung
  chỉ để hợp thức hóa artifact nghiên cứu. Nếu metadata augmented cần trường
  bổ sung, dùng extension rõ ràng, không nói original manifest đại diện cho
  toàn bộ training corpus mới.

## 8. Kiểm thử phải chứng minh điều gì

Viết test trước, quan sát thất bại đúng lý do rồi mới code:

1. Tiếng Việt NFC/NFD, đ/Đ, văn bản đã không dấu, chữ số/dấu câu/emoji; không
   sửa raw source hay normalizer gốc, transformation deterministic/idempotent.
2. Lấy subset theo hash/seed đúng tỷ lệ và lồng nhau; không chọn theo validation;
   parent_id/nhãn/source group đúng; không thêm biến thể trùng chính câu gốc.
3. Không fit vocabulary/IDF lên validation/stress/known cases; xử lý minh bạch
   augmentation collisions và nhãn mâu thuẫn, không tự relabel.
4. Clone không giữ trạng thái fitted hoặc làm đổi parent; hỗ trợ cả word-only
   và word+char; class weights/params đúng parent và không đổi âm thầm.
5. Fixture lifecycle **không có test split trên disk**, đủ các lớp. Run → save →
   fresh reload/verify đạt; replay bị cấm gọi fit. Các controls không đổi hash.
6. Từ chối live output, output cũ, path overlap/symlink ra ngoài trước fit/write;
   incomplete receipt, metadata/config/artifact/data/parent tamper phải bị phát hiện.
7. Xếp hạng global tie bands, control-first; không dùng known/stress/test scores.
8. Joint tính từ cùng source IDs; phân biệt điểm phần trăm và % tương đối, xử
   lý mẫu số 0; null không chấm và mọi ca hồi quy phải được giữ.

Chạy suite phù hợp khi phát triển; cuối cùng chạy toàn suite với dữ liệu thật
và browser, không tính skip là đạt:

```powershell
$env:TV2_RUN_REAL_DATA='1'
./.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider
./.venv/Scripts/python.exe -B -m pip check
```

Không nâng dependencies để làm mất warning lịch sử. Nếu môi trường/đầu vào
khác control, điều tra và báo khác biệt, không sửa hash/metrics để khớp.

## 9. Báo cáo bắt buộc cho người dùng

Bảng Original / CT2 / best through CT3 / CT4-only / best through CT4, cùng split:

- Accuracy, Macro Precision/Recall/F1 mỗi task, per-class và confusion matrix.
- Joint accuracy: số câu cả hai nhãn đúng / tổng số câu.
- Delta so original **và CT3**, đơn vị **điểm phần trăm**; % tương đối tách cột.
- Exact số ca sai→đúng, đúng→sai từng task và joint; full changed IDs.
- Stress không dấu và 39 known cases ghi riêng, không gộp thành một benchmark
  “độ chính xác chung”; tách mẫu số gốc/nhãn có kỳ vọng/null/source groups.
- Train rows mới và chi phí thực tế/artifact size; có lợi ích nào đánh đổi bằng
  hồi quy, độ lớn model hoặc inference time. Không tự đặt SLA.
- Suite/replay/review thực tế, warnings, deferred findings và giới hạn dữ liệu.
- Nêu model đang phục vụ có thay không. Trong phạm vi này câu trả lời là **không**.

Ví dụ cách diễn đạt đúng: 81,87% → 82,50% là +0,63 điểm %, khoảng +0,77%
tương đối. **Đây chỉ là ví dụ tính toán, không phải kết quả CT4.** Nếu kết quả
thật giảm, nói giảm; nếu không có ứng viên vượt control, giữ control và ghi nhận
thí nghiệm âm, không tiếp tục dò cho đến khi có số đẹp.

## 10. Ranh giới và điều kiện hoàn thành

Chỉ CT4 offline. Không API key/dịch vụ ML ngoài, LLM-generated labels,
PhoBERT/Deep Learning, batch/CSV/Dashboard, cơ chế từ chối CT5, Phase 6 hoặc
đổi schema/API/UI. Không tải thêm dữ liệu ngoài hoặc thêm dependencies tự động.
Không tự deploy, đổi SFAI_MODEL_DIR, ghi models/, commit/push/merge, upload hay
công bố dataset/model. Giữ source license unknown đúng hiện trạng.

Hoàn thành khi có finite config + provenance/tests + run thật + fresh replay +
đối chiếu original/CT2/CT3 + kiểm bảo toàn + suite đầy đủ + review độc lập + báo
cáo trung thực. **Không yêu cầu thí nghiệm nhất thiết phải tăng điểm để được
xem là hoàn thành.** Không tuyên bố hệ thống tổng quát tốt hơn chỉ từ validation.

Nếu thiếu dữ liệu local/đúng môi trường, báo chính xác phần thiếu và phần vẫn
làm được; không tạo artifact giả. Các lựa chọn nhỏ trong phạm vi này agent tự
giải quyết và ghi ledger; thay phạm vi hoặc model phục vụ cần người dùng duyệt.

## 11. Prompt ngắn để người dùng gửi

```text
Triển khai CT4 theo file:
D:\N.ThanhNhan\Project_AI\student-feedback-ai\.local-tools\integration-p0\docs\quality\ct4-agent-handoff.md

Tôi chọn hướng CT4 trong file: augmentation không dấu chỉ từ train, thí nghiệm
offline hữu hạn và đối chiếu với original, CT2, CT3. Làm trên linked worktree
.local-tools/integration-p0, bảo toàn toàn bộ công việc hiện có. Đọc file và các
tài liệu được dẫn trước khi sửa. Lập kế hoạch, viết test trước, chạy thí nghiệm
thật, fresh replay, toàn suite và review theo hướng dẫn dự án. Tự xử lý lựa chọn
triển khai nhỏ trong phạm vi đã mô tả, ghi rõ vào ledger.

Kết quả cuối phải trả lời: Accuracy từng task và tỷ lệ cả hai nhãn cùng đúng
tăng/giảm bao nhiêu điểm phần trăm so ban đầu và CT3; Macro F1/neutral/other
đánh đổi thế nào. Không dùng điểm stress/39 ca đã biết để tuyên bố cải thiện
tổng quát. Nếu điểm giảm, báo đúng. Không tự thay model demo, triển khai CT5/
Phase 6, commit/push/merge hay publish dữ liệu/model.
```
