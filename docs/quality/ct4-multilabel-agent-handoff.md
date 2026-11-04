# Bàn giao: mở rộng demo CT4 theo bộ nhãn người dùng đã chốt

**Ngày:** 2026-11-01.  
**Trạng thái:** Đặc tả yêu cầu và prompt bàn giao; **chưa triển khai**.  
**Mục đích lượt hiện tại:** Chỉ viết tài liệu để người dùng chuyển cho agent khác.
Không suy ra rằng CT4/demo hiện tại đã có các hành vi dưới đây.

## 1. Quyết định nghiệp vụ đã được người dùng xác nhận

Người dùng đã xác nhận toàn bộ bảng nhãn, ví dụ ở cuộc trao đổi và chốt thêm:
**Câu chỉ cung cấp thông tin, không khen cũng không chê, phải có cảm xúc
“Chưa xác định”. “Trung tính” chỉ xuất hiện khi nhận diện được cả tích cực
và tiêu cực trong cùng một đầu vào.** Không hỏi lại quyết định này.

### Cảm xúc — đúng bốn nhãn hiển thị

| Có bằng chứng tích cực? | Có bằng chứng tiêu cực? | Nhãn hiển thị |
| --- | --- | --- |
| Có | Không | **Tích cực** |
| Không | Có | **Tiêu cực** |
| Có | Có | **Trung tính** |
| Không | Không | **Chưa xác định** |

- “Cùng đầu vào” gồm các ý/mệnh đề thuộc cùng câu phản hồi người dùng nhập.
  Hai cảm xúc có thể nói về cùng một đối tượng hoặc các đối tượng khác nhau.
- Không cần hai ý có cường độ bằng nhau. Khi đã nhận diện được cả hai thì
  tổng hợp là Trung tính, không lấy ý mạnh hơn để thắng.
- Câu thuần thông tin, câu thiếu căn cứ, chuỗi không có ý nghĩa cảm xúc rõ:
  Chưa xác định. Nhãn này không đồng nghĩa model bị thiếu/hỏng hoặc server lỗi.
- **Không ánh xạ trực tiếp `neutral` của UIT-VSFC/CT4 thành Trung tính mới.**
  Nhãn neutral cũ không chứng minh có cả hai cảm xúc. Một score nhì cao cũng
  không chứng minh câu thực sự chứa cảm xúc thứ hai.

### Chủ đề — đúng năm nhãn hiển thị

Nhận diện tập chủ đề cốt lõi được đề cập, không đếm số từ khóa hay số lần nhắc:

| Tập chủ đề cốt lõi nhận diện được | Nhãn hiển thị |
| --- | --- |
| Chỉ giảng viên | **Giảng viên** |
| Chỉ chương trình đào tạo | **Chương trình đào tạo** |
| Chỉ cơ sở vật chất | **Cơ sở vật chất** |
| Hai hoặc ba chủ đề trong ba nhóm trên | **Chất lượng giáo dục** |
| Không xác định được nhóm nào trong ba nhóm trên | **Lĩnh vực khác** |

- Chất lượng giáo dục là **nhãn tổng hợp nhiều chủ đề**, không phải một task
  đánh giá chất lượng mới hoặc nhãn cảm xúc.
- Nhắc “thầy” và “cô” vẫn chỉ là một chủ đề Giảng viên; lặp nhiều lần không
  biến thành Chất lượng giáo dục.
- Chủ đề có thể được xác định dù cảm xúc là Chưa xác định. Hai đầu ra độc lập.
- “Lĩnh vực khác” bao gồm cả thiếu thông tin về đối tượng, không đủ căn cứ
  xác định chủ đề và nội dung ngoài ba nhóm. Không tự tuyên bố tất cả những
  câu này là ngoài miền: ví dụ “Tốt” thiếu đối tượng, chưa chứng minh ngoài miền.
- Khi đã có một chủ đề cốt lõi và thêm nội dung ngoài ba nhóm, chỉ riêng nội
  dung ngoài nhóm không đủ tạo Chất lượng giáo dục; cần ít nhất hai nhóm cốt lõi.
- Không tiếp tục dùng “Khác” hoặc “Chưa đủ thông tin” làm **nhãn chủ đề hiển thị**
  trong bản mới; nhãn người dùng đã chốt là Lĩnh vực khác.

## 2. Ma trận ví dụ và tiêu chí chức năng

Đây là ví dụ đặc tả để viết tests, **không phải kết quả model đã chạy hoặc
benchmark độc lập**. Những câu mới do agent đề xuất phải ghi nguồn assistant_proposed;
không bịa người rà hoặc lấy output model làm ground truth.

| Đầu vào | Cảm xúc mong muốn | Chủ đề mong muốn |
| --- | --- | --- |
| Thầy giảng bài rõ ràng và phòng học thì nóng. | Trung tính | Chất lượng giáo dục |
| Giảng viên nhiệt tình và phòng học sạch đẹp. | Tích cực | Chất lượng giáo dục |
| Cô dạy rất hay nhưng đôi lúc giải thích khó hiểu. | Trung tính | Giảng viên |
| Giảng viên thiếu nhiệt tình và phòng thực hành có nhiều máy hỏng. | Tiêu cực | Chất lượng giáo dục |
| Giảng viên nhiệt tình, nội dung môn học thiết thực và phòng học sạch sẽ. | Tích cực | Chất lượng giáo dục |
| Thầy và cô đều giảng bài dễ hiểu. | Tích cực | Giảng viên |
| Chương trình có quá nhiều lý thuyết và thiếu giờ thực hành. | Tiêu cực | Chương trình đào tạo |
| Máy tính trong phòng thực hành thường xuyên bị hỏng. | Tiêu cực | Cơ sở vật chất |
| Môn học có ba tín chỉ. | **Chưa xác định** | Chương trình đào tạo |
| Giảng viên sử dụng slide trong các buổi học. | Chưa xác định | Giảng viên |
| Phòng học có máy chiếu. | Chưa xác định | Cơ sở vật chất |
| Giảng viên thông báo lịch học và phòng học ở tầng hai. | Chưa xác định | Chất lượng giáo dục |
| Tốt. | Tích cực | Lĩnh vực khác |
| Thay giang bai de hieu va rat nhiet tinh. | Tích cực | Giảng viên |
| 🙂🙂🙂 | Chưa xác định | Lĩnh vực khác |

Kiểm thêm sự độc lập: một phần có bằng chứng không được bị xóa chỉ vì phần
còn lại chưa xác định; không trả cùng một nhãn cố định cho mọi input khó.

Phủ định/ngữ cảnh mơ hồ cần ghi riêng. “Bài giảng không khó hiểu như em nghĩ”
là lỗi còn biết của bản hiện tại, **chưa được nghiệm thu là đã sửa** trong
handoff này. Không đếm từ “khó hiểu” hoặc mọi chữ “không” thành bằng chứng
tiêu cực/tích cực một cách máy móc. Nếu cần mở rộng xử lý phủ định chuyên sâu,
đề xuất phạm vi/dữ liệu được rà riêng; không âm thầm hứa đã giải quyết toàn bộ.

## 3. Vào đúng workspace và đọc đúng hiện trạng

Workspace tích hợp:

`D:\N.ThanhNhan\Project_AI\student-feedback-ai\.local-tools\integration-p0`

Linked worktree: `feature/integration-p0`. Checkout ngoài ở nhánh phần Data và
clone lồng `student-feedback-ai/` là các bản khác. Không reset/clean, đổi nhánh,
chép đè công việc thành viên hoặc commit gom dirty work.

Đọc trước khi sửa:

1. AGENTS/hướng dẫn phiên và các skill Superpowers liên quan.
2. **File này**: yêu cầu nghiệp vụ mới nhất; đặc biệt không-khen-không-chê →
   Chưa xác định, không phải Trung tính.
3. `docs/quality/ct4-partial-demo.md`,
   `docs/superpowers/specs/2026-11-01-ct4-partial-demo-design.md`,
   `docs/superpowers/plans/ct4-partial-demo-progress.md`.
4. `demo_v2/policy.py`, `service.py`, `main.py`, `frontend/`;
   `tests/test_demo_v2.py`, `tests/frontend/test_demo_v2_ui.py`.
5. `docs/quality/ct1-protocol.md`, `ct4-report.md`, `ct5-report.md`,
   `reports/evidence/ct4-partial-demo/review.md` và
   `reports/evidence/ct4-partial-demo/handoff-verification.json`.
6. `docs/specs/{api-contract,data-contract}.md`, `ml/labels.py`, các runner
   `reports/ct_evaluation.py`, `ct4_augmentation.py`, `ct5_selective_prediction.py`
   khi cần hiểu ý nghĩa nhãn, model và provenance cũ.

Các mốc hiện tại, phải kiểm tra lại thực tế trên máy agent:

- Baseline: `backend/`, `frontend/`, `models/`, URL local8000 khi server chạy.
- Trial CT4 hiện tại: `demo_v2/`, URL local8001 khi server chạy; API2.0.
- CT4 frozen pair: `.local-tools/ct4-augmentation/run-1/research-selected/`.
  Sentiment=ct3parent_aug100; topic=ct3parent_aug25. Không train lại cặp này.
- CT5 thresholds: `.local-tools/ct5-selective-prediction/run-1/thresholds.json`.
  Demo_v2 dùng q10 riêng từng task; đây là policy thử, không semantic detector.
- Demo_v2 chỉ có phân loại một nhãn/task + gate. **Chưa có nhận diện nhiều
  cảm xúc/chủ đề và quy tắc tổng hợp mới.**
- Kết quả đã lưu:435 tests passed,0 skipped,14 warnings;654 original hashes
  giữ nguyên tại lần bàn giao trước. Đây là lịch sử, không kết quả agent mới chạy.
- Chưa có final/answerability dataset được người rà độc lập; Phase6 chưa làm.

## 4. Hướng kỹ thuật để agent thiết kế trước khi viết code

Người dùng đã chốt **hành vi**, chưa chốt thuật toán mới hoặc cho phép nâng
dependency/train dữ liệu mới. Agent tự quyết chi tiết nhỏ và ghi lý do;
không hỏi lại bảng nhãn đã duyệt. Nếu một thay đổi lớn về dữ liệu/thuật toán
thật sự cần duyệt, trình phương án cụ thể và phần việc có thể làm trước.

### Hướng ưu tiên để thử hữu hạn

Kế thừa CT4 làm thành phần phân tích, thêm lớp nhận diện ý/mệnh đề và bằng chứng
cho từng task rồi tổng hợp theo bảng ở mục1. Tách rõ:

1. **Nhận diện:** những ý nào đủ căn cứ tích cực/tiêu cực; chủ đề cốt lõi nào
   thực sự được đề cập. Câu thuần thông tin không tự thành ý khen/chê.
2. **Tổng hợp:** hai boolean cảm xúc và một tập ba chủ đề, theo quy tắc đã chốt.
3. **Trình bày:** đúng một nhãn cảm xúc và một nhãn chủ đề cuối cùng; bằng chứng
   chi tiết có thể lưu nội bộ để audit, không bắt người dùng hiểu score kỹ thuật.

Đây là hướng đề xuất triển khai, **chưa phải phương pháp đã được chứng minh
đạt yêu cầu**. Một model multiclass CT4 không tự biến thành multilabel chỉ
bằng đổi tên, lấy top2 hoặc hạ threshold. CT4 cũng có thể đoán sai các đoạn con.

Không tách mù quáng mọi chữ “và”: “thầy và cô giảng dễ hiểu” không là hai chủ đề.
Không chỉ hỗ trợ câu có “nhưng”: cảm xúc trái chiều có thể được nối bằng “và”,
dấu câu hoặc cách diễn đạt khác. Không coi việc xuất hiện tên nhóm trong ngữ cảnh
không được đề cập thực sự là đủ bằng chứng. Báo rõ giới hạn của clause segmentation.

Phương án thay thế nếu cần chất lượng tổng quát hơn: model nhận diện đa nhãn/
khía cạnh trên dữ liệu gán nhãn phù hợp. Không tự coi UIT-VSFC hiện tại đã có
ground truth đa nhãn; không tạo giả nhãn nhiều ý từ một nhãn cũ để tuyên bố
đã có dữ liệu chuẩn. Train mới, model/API ngoài, dependency lớn hoặc chi phí
dịch vụ cần được đề xuất riêng, không mặc định được yêu cầu này cho phép.

### Những cách không được dùng để làm đẹp demo

- Không hardcode nguyên các câu ở mục2 hoặc rẽ nhánh theo câu đã biết.
- Không chỉ thấy đồng thời một từ khen và một từ chê là kết luận Trung tính;
  phải xét vai trò/ngữ cảnh, nhất là phủ định và mô tả thuần thông tin.
- Không dùng top2 topic scores làm bằng chứng có hai chủ đề.
- Không gọi model `neutral` cũ là mixed mới; không sửa nhãn/hashes/receipt cũ.
- Không chọn lại ngưỡng theo test lịch sử, không coi rejected là đúng hoặc margin
  là xác suất confidence. Nếu dùng quy tắc/lexicon thử nghiệm, version hóa, nêu
  provenance và giới hạn; kiểm trên biến thể ngoài các câu mẫu đã lộ.

## 5. Ranh giới mã nguồn, API và giao diện

**Đề xuất của người viết handoff:** thêm bản thử nghiệm `demo_v3/` trên8002,
API `/api/v3/predict`, contract_version3.0; giữ nguyên v1/v2 và frozen CT1–CT5.
Đây là lựa chọn nhằm giữ khả năng đối chiếu, không phải yêu cầu người dùng đã
chỉ định tên thư mục/cổng. Agent có thể điều chỉnh tương đương và ghi ledger,
nhưng không làm mất bản CT4 hiện có hoặc phá nguồn dùng replay.

Tên mã nội bộ gợi ý để tránh nhầm ontology cũ:

- sentiment: `positive`, `negative`, **`mixed`** → Trung tính,
  `undetermined` → Chưa xác định.
- topic: `lecturer`, `curriculum`, `facility`, `education_quality`, `other_domain`.
- Bảng hiển thị phải chính xác dấu tiếng Việt như mục1. Không bắt buộc backend
  trả trực tiếp display_label; có thể ánh xạ tập trung ở UI để tránh trùng logic.
- Các mã này là đề xuất schema mới; không thêm vào `ml/labels.py` của model
  cũ hoặc ép artifact CT4 giả vờ có classes mới.

Ví dụ **minh họa hợp đồng đề xuất, không phải response đã triển khai**:

```json
{
  "contract_version": "3.0",
  "sentiment": "mixed",
  "topic": "education_quality"
}
```

Với “Môn học có ba tín chỉ”: sentiment=`undetermined`, topic=`curriculum`.
Với “Tốt”: sentiment=`positive`, topic=`other_domain`.
Không để state machine `complete/partial/insufficient` của v2 tự quyết nhãn
nghiệp vụ v3; agent phải thiết kế lại hoặc bỏ trường đó trong contract mới.

Lỗi kỹ thuật vẫn là lỗi: input sai422, nguồn/model chưa sẵn sàng503, inference
lỗi500. **Không nuốt exception thành Chưa xác định/Lĩnh vực khác.** Input hợp lệ
được phân tích nhưng không đủ bằng chứng có thể trả các nhãn nghiệp vụ này
với HTTP200. Giữ giới hạn5000 Unicode code points, strict string/không blank,
timeout toàn response body, không gửi trùng và không hiển thị kết quả của câu cũ.

UI phải hiện đúng bốn/năm nhãn; không hiện “Hỗn hợp” thay cho Trung tính dù
mã nội bộ là mixed. Có thể thêm chú giải ngắn “Trung tính: có cả ý tích cực
và tiêu cực” để tránh hiểu theo nghĩa neutral cũ. Không hiển thị phần trăm
confidence chưa được hiệu chỉnh.

## 6. Trình tự thực hiện khi người dùng gửi prompt triển khai

1. **Khảo sát và bảo toàn:** Git/worktree/status, đọc file bắt buộc, inventory
   file trước thay đổi; không tính tài liệu vừa tạo là file có trước. Backup đúng
   byte bằng chứng browser cũ trước full suite. Không khởi tạo lại dự án.
2. **Thiết kế/kế hoạch:** ghi thuật toán nhận diện nhiều ý, schema mới, ranh giới
   được quyết định và giới hạn. Viết plan + ledger mới dưới docs/superpowers/;
   bảng nhãn nghiệp vụ đã duyệt không cần xin lại. Không biến hướng kỹ thuật
   đề xuất ở mục4 thành “người dùng đã duyệt thuật toán”.
3. **Tests trước code:** RED rồi GREEN cho bộ tổng hợp độc lập với detector;
   detector thử nghiệm có tests riêng, API và UI có tests riêng.
4. **Thử nghiệm hữu hạn:** đóng băng cấu hình trước đo; kiểm các biến thể chưa
   dùng viết luật. Giữ code/config/hash/input provenance, không tuning vô hạn
   để khớp từng câu hoặc dùng test đã lộ như holdout mới.
5. **Tích hợp demo mới:** giữ CT4 artifact read-only, chính xác nhãn/version mới,
   không sửa app/receipt cũ để test qua; kiểm thiếu/hỏng provenance và runtime.
6. **Kiểm chứng:** scoped tests, Chrome/Edge, full suite có dữ liệu thật,
   pip check, fresh no-fit replay CT1–CT5 và preservation. Chạy independent
   review; các lỗi chặn hành vi có regression RED→GREEN trước bàn giao.
7. **Bàn giao:** server local mới chạy thật, health/API/UI được kiểm lại, link
   đúng phiên bản, ví dụ kết quả thật và giới hạn; không gọi là đã tăng Accuracy
   tổng thể khi chưa có đánh giá cùng ontology trên tập độc lập.

### Tests tối thiểu

- Đủ bốn tổ hợp boolean cảm xúc; true+true luôn Trung tính; false+false luôn
  Chưa xác định, kể cả câu thuần thông tin.
- Đủ tám tập con của ba chủ đề (0,1,2,3 nhóm), deduplicate trước đếm.
- Nhiều cảm xúc/cùng chủ đề; một cảm xúc/nhiều chủ đề; thông tin thuần/nhiều
  chủ đề; một task xác định/task kia fallback.
- Câu ghép dùng “và”, “nhưng”, dấu câu; các biến thể “thầy/cô/giảng viên”
  không tự tăng số chủ đề; có dấu/không dấu/NFC/NFD.
- Kiểm không suy diễn false mixed từ tên nhãn/score nhì/từ khóa bị phủ định;
  trường hợp detector chưa hỗ trợ phải được báo lỗi chất lượng, không che đi.
- Nhãn/prototype/sai kiểu không lọt UI; response khác version không hiển thị;
  input5000/5001, emoji, JSON/Unicode sai, thiếu model/config, inference exception.
- Đổi text trong lúc chờ/sau kết quả không giữ nhãn cũ; timeout bao cả body,
  không gửi trùng, phục hồi sau lỗi, không mock fallback.
- Hash nguyên bản CT1–CT5, baseline/demo_v2 và bằng chứng trước khi thực hiện;
  browser screenshot mới lưu riêng, chỉ phục hồi byte cũ nếu kiểm backup khớp.

### Đánh giá và giới hạn

Bộ nhãn mới khác ontology UIT-VSFC cũ. Không so trực tiếp một Accuracy mới với
89,70%/86,17% hoặc các Macro F1 cũ rồi tuyên bố tăng/giảm nếu khác nhãn/mẫu số.
Tách điểm **detector** với tính đúng quy tắc **aggregator**: aggregator đúng bảng
không chứng minh detector hiểu đúng câu. Báo confusion/per-class/support và
joint exact match trên tập có ground truth theo **định nghĩa mới**, nếu có.

Nếu có abstention nội bộ, báo coverage, accepted accuracy/risk và correct/N riêng;
không dùng nhãn mixed/undetermined/other_domain để che từ chối hoặc lỗi kỹ thuật.
Cần người rà riêng tập mới, không xem output khi gán nhãn; giữ nhãn mixed rõ ràng
khác neutral dữ liệu cũ. Nếu chưa có tập đó, vẫn hoàn tất phần kỹ thuật thử
nghiệm trong phạm vi có thể kiểm, ghi
`engineering_complete_independent_evaluation_pending`; không bịa dữ liệu hoặc
người rà, không tuyên bố đã đạt tổng quát chỉ từ các ví dụ này.

## 7. Phạm vi quyền và điều kiện dừng

- Handoff này chỉ được **soạn** ở lượt hiện tại. Việc triển khai chỉ bắt đầu
  khi người dùng chuyển prompt bên dưới hoặc yêu cầu agent thực hiện.
- Khi được yêu cầu triển khai, được thêm bản demo thử theo nghiệp vụ ở mục1,
  lập kế hoạch/tests/engine/API/UI và kiểm chứng, giữ toàn bộ bản cũ.
- Không tự train lại artifact lịch sử, sửa corpus/nhãn dữ liệu cũ, đổi model
  sang dịch vụ ngoài, thêm API key/chi phí, mở rộng phủ định toàn diện, P1/
  Dashboard/Phase6, commit/push/merge, upload hay công bố dataset/model.
- Các hạn chế về quyền nguồn vẫn unknown; trusted artifacts, chỉ demo local.
- Việc cần thay thuật toán/dữ liệu lớn phải có đề xuất rõ, không ngầm mặc định
  đã được duyệt. Không dừng phần công việc kỹ thuật độc lập chỉ vì thiếu final set.

## 8. Prompt người dùng có thể chuyển cho agent khác

```text
Triển khai mở rộng demo CT4 theo tài liệu:
D:\N.ThanhNhan\Project_AI\student-feedback-ai\.local-tools\integration-p0\docs\quality\ct4-multilabel-agent-handoff.md

Tôi đã chốt nghiệp vụ trong file. Cảm xúc có Tích cực, Tiêu cực, Trung tính,
Chưa xác định. Trung tính CHỈ khi cùng đầu vào có cả bằng chứng tích cực và
tiêu cực; câu thuần thông tin không khen/chê như “Môn học có ba tín chỉ” phải
là Chưa xác định. Không dùng neutral cũ làm bằng chứng mixed mới.

Chủ đề có Giảng viên, Chương trình đào tạo, Cơ sở vật chất, Chất lượng giáo dục,
Lĩnh vực khác. Hai hoặc ba nhóm cốt lõi được nhận diện thì Chất lượng giáo dục;
không nhận diện được nhóm cốt lõi nào thì Lĩnh vực khác. Hai đầu ra độc lập.

Đọc kỹ hiện trạng demo_v2, CT4/CT5 và hợp đồng cũ trước khi sửa. Làm trên linked
worktree integration-p0, bảo toàn dirty work, baseline/demo_v2 và mọi mốc CT1–CT5.
Lập thiết kế/kế hoạch, tests trước code, triển khai bản thử mới có nhận diện
nhiều ý/chủ đề và tổng hợp đúng bảng, API/UI được version hóa. Không chỉ đổi
tên nhãn, không hardcode câu mẫu hoặc lấy top2 score làm hai chủ đề/cảm xúc.

Tự quyết chi tiết nhỏ, ghi ledger và giới hạn. Hướng clause-level + CT4 trong
file là đề xuất kỹ thuật, không là thuật toán tôi đã chốt; đánh giá tính khả thi
trước khi chọn. Nếu cần model/dữ liệu/chi phí mới lớn, đưa phương án để duyệt,
vẫn làm phần kỹ thuật độc lập có thể thực hiện. Không hỏi lại bảng nhãn đã chốt.

Chạy thử hữu hạn, tests API/UI Chrome/Edge, full suite, no-fit replay lịch sử,
preservation và review; khởi động demo mới và gửi link cùng kết quả thực tế.
Phân biệt detector với aggregator và đánh giá theo ontology mới. Thiếu tập mới
có người rà thì ghi independent_evaluation_pending, không bịa Accuracy/dữ liệu.
Chưa tự mở rộng xử lý phủ định chuyên sâu, Phase6, train lại corpus/model cũ,
commit/push/merge hoặc công bố dữ liệu/model.
```
