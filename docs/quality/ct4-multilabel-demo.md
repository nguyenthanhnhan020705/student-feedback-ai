# Demo v3 — cảm xúc và chủ đề theo nghiệp vụ mới

Đặc tả: [tài liệu bàn giao](ct4-multilabel-agent-handoff.md). Bản thử nghiệm mới
được triển khai riêng trong `demo_v3/`; bản baseline và `demo_v2/` được giữ nguyên.
Trạng thái kiểm chứng cuối xem `reports/evidence/ct4-multilabel/README.md` và
`docs/superpowers/plans/ct4-multilabel-progress.md`; tài liệu này không thay log thực thi.

## Nghiệp vụ

| Bằng chứng cảm xúc | Nhãn hiển thị | Mã API |
| --- | --- | --- |
| Chỉ tích cực | Tích cực | positive |
| Chỉ tiêu cực | Tiêu cực | negative |
| Có cả hai | Trung tính | mixed |
| Không nhận diện được ý khen/chê | Chưa xác định | undetermined |

Trung tính ở v3 có nghĩa mới: có cả ý tích cực và tiêu cực trong cùng đầu vào.
Nhãn `neutral` của model cũ không phải bằng chứng cho điều này. Câu chỉ cung cấp
thông tin có thể xác định được chủ đề và vẫn có cảm xúc Chưa xác định.

| Tập chủ đề cốt lõi | Nhãn hiển thị | Mã API |
| --- | --- | --- |
| Chỉ giảng viên | Giảng viên | lecturer |
| Chỉ chương trình đào tạo | Chương trình đào tạo | curriculum |
| Chỉ cơ sở vật chất | Cơ sở vật chất | facility |
| Hai hoặc ba nhóm trên | Chất lượng giáo dục | education_quality |
| Không nhận diện được nhóm trên | Lĩnh vực khác | other_domain |

Tập chủ đề được loại trùng trước khi đếm. Lĩnh vực khác bao gồm cả thiếu đối tượng
và ngoài ba nhóm; nhãn này không chứng minh đầu vào ngoài miền. Nội dung ngoài nhóm
đi kèm một nhóm cốt lõi không tự tạo chủ đề Chất lượng giáo dục.

## Cách triển khai và giới hạn

Bộ tổng hợp thuần túy nhận hai cờ cảm xúc và tập ba chủ đề. Đây là phần có thể
kiểm chứng đầy đủ bằng bảng tổ hợp, độc lập với chất lượng nhận diện ngôn ngữ.

Bộ nhận diện là luật/lexicon thử nghiệm do trợ lý soạn, có phiên bản, checksum,
nguồn và giới hạn trong `demo_v3/rules.json`. Nó xét các đoạn nhận xét, đối tượng,
cụm đánh giá, trích dẫn và một số mẫu phủ định cục bộ. Không phải model đa nhãn
được huấn luyện mới. Không có nhánh hardcode nguyên câu mẫu, dùng top2 score hay
đổi tên nhãn cũ để giả lập nhận diện nhiều ý.

Hai pipeline CT4 và nguồn ngưỡng CT5 được nạp read-only qua cơ chế kiểm provenance,
checksum và runtime hiện có. Suy luận đoạn được lưu trong dấu vết nội bộ để audit;
khác biệt giữa CT4 và luật không tự thêm, xóa hoặc thay bằng chứng quyết định nhãn.
Lỗi suy luận vẫn là lỗi kỹ thuật, kể cả khi câu thiếu bằng chứng nghiệp vụ.

Phủ định dài, phủ định kép, mỉa mai, lời nói gián tiếp, chủ đề ngầm, từ mới và
câu không dấu mơ hồ chưa được giải quyết tổng quát. Bộ nhận diện có thể sai.
Các ví dụ đặc tả và biến thể `assistant_proposed` chỉ là kiểm tra chức năng/thăm dò,
không phải ground truth được người rà độc lập. Chưa có cơ sở tuyên bố tăng Accuracy
so với UIT-VSFC: ontology và mẫu số đã khác.

### Kết quả thăm dò ở mốc đóng băng ban đầu

Sau `core-freeze.json`, trợ lý soạn 36 biến thể rồi chạy hữu hạn, không huấn luyện
và không sửa luật theo kết quả. `evaluation.json` ghi 15/15 ví dụ đặc tả và 32/36
biến thể có cả hai nhãn khớp nhãn đề xuất. Không gộp hai tập thành benchmark.
Confusion matrix, từng lớp/support và dấu vết phân tích nằm trong JSON.

Bốn sai lệch được giữ lại:

| Biến thể | Sai lệch so với nhãn trợ lý đề xuất |
| --- | --- |
| Cô giải thích dễ hiểu; giáo trình quá cũ. | Chỉ nhận tích cực, bỏ sót ý tiêu cực “quá cũ” |
| Cô không giảng khó hiểu. | Trả Tiêu cực thay vì Tích cực; phạm vi phủ định chưa hỗ trợ |
| Không nhận xét về giảng viên. | Vẫn nhận Giảng viên thay vì Lĩnh vực khác |
| Giáo viên chu đáo và lớp học ngột ngạt. | Bỏ sót từ vựng và đối tượng chưa nằm trong bộ luật |

Review độc lập còn phát hiện ba lỗi trong chính các ngữ cảnh đã có guard:
trích dẫn nhiều dòng, phạm vi cụm từ qua ranh giới mệnh đề, và “từ” chỉ nguồn gốc.
Bản sửa được kiểm bằng regression tests riêng. Mốc đóng băng và điểm thăm dò
ban đầu được giữ nguyên; nếu có `evaluation-final.json`, đó là chạy lại tập đã lộ
trên bản sửa, vẫn không phải holdout mới hoặc bằng chứng cải thiện tổng quát.

## API và cách chạy

Từ `.local-tools/integration-p0`:

```powershell
./.venv/Scripts/python.exe -B -m uvicorn demo_v3.main:app --host 127.0.0.1 --port 8002
```

Mở `http://127.0.0.1:8002/`. `GET /api/health` báo readiness;
`POST /api/v3/predict` nhận object chỉ có raw string `text`, không blank,
tối đa 5000 Unicode code point, không lone surrogate.

Response thành công có đúng `contract_version: "3.0"`, `sentiment` và `topic`.
HTTP 200 có thể trả nhãn Chưa xác định/Lĩnh vực khác. Input sai trả 422;
model/nguồn/cấu hình chưa sẵn sàng trả 503; lỗi suy luận trả 500, không nhãn nửa chừng.
Không trả confidence chưa hiệu chỉnh, score, đường dẫn nội bộ hoặc stack trace.

UI kiểm version/nhãn strict, đếm code point, giữ input, timeout cả response body,
chặn gửi trùng và xóa kết quả khi sửa nội dung. Không có mock fallback.

## Kiểm chứng và bảo toàn

Các bằng chứng mới ở `reports/evidence/ct4-multilabel/`. Inventory chụp trước khi
tạo thiết kế/mã mới gồm 708 file gốc. Bằng chứng browser cũ được backup đúng byte;
khi suite làm mới ảnh/JSON cũ, bản mới được giữ riêng rồi phục hồi từ backup có
checksum khớp. Không phục hồi tự động bất kỳ mã nguồn/model/receipt bị đổi nào.

Không train lại artifact lịch sử, không đổi corpus/nhãn cũ, không thêm dependency,
dịch vụ ngoài, API key hay chi phí. Không commit/push/merge/công bố dữ liệu/model;
Phase 6 và P1 vẫn ngoài phạm vi. Quyền phân phối nguồn còn unknown, chỉ demo local.

Thiếu tập mới có người rà độc lập được ghi
`engineering_complete_independent_evaluation_pending` sau khi kỹ thuật đạt;
trạng thái đó không chứng nhận chất lượng tổng quát hay khả năng dùng production.

Kết quả kỹ thuật cuối ngày 2026-11-01: **644 tests đạt, không skip**, 14 cảnh báo
thư viện đã biết; Chrome/Edge đã kiểm. Năm replay lịch sử CT1–CT5 đạt với fitting
bị cấm; 708/708 hash gốc giữ nguyên. Các lỗi review đã có regression RED→GREEN,
và HTTP trên server cuối đã kiểm lại cả bốn ca. Bằng chứng/receipt được lưu tại
`reports/evidence/ct4-multilabel/`; không có lượt review độc lập thứ ba sau sửa R4.
