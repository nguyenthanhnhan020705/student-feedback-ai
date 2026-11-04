# Báo cáo TV4 — Topic

## Trạng thái

Đã triển khai và chạy baseline thật trên local ngày 2026-10-29 theo yêu cầu hoàn thiện TV4.
Kế thừa code Topic commit `74330f3`, bổ sung CLI tùy chọn manifest/figure-dir, đối chiếu
dữ liệu với manifest, tests, notebook, phân tích lỗi và kiểm chứng tải lại.
Các thay đổi chưa commit/push/merge; workspace hiện tại là `feature/data-preprocessing`.
Không coi phần local này là nghiệm thu Backend hoặc leader đã duyệt Data/môi trường.

## Dữ liệu và phương pháp

UIT-VSFC từ Data local, train 11426 / validation 1583 / test 3166. Manifest/checksum nằm
ở `reports/data/manifest.json`; metadata Topic lưu SHA-256 của manifest đó. Giữ một cặp
trùng trong train theo report-only; không có text chuẩn hóa giao nhau giữa split theo Data.
Điều này không chứng minh đã loại trừ mọi near-duplicate hoặc nguồn rò rỉ.

Ba pipeline TF-IDF + NB/LR/LinearSVC độc lập; chỉ fit train. Chọn bằng validation Macro F1,
sau đó Accuracy và thứ tự cố định khi hòa. Không refit hoặc điều chỉnh theo test.
Cấu hình và cách chạy ở [experiment.md](experiment.md).

## Kết quả thực nghiệm

| Split | Model | Accuracy | Macro Precision | Macro Recall | Macro F1 |
|---|---|---:|---:|---:|---:|
| validation | nb | 0.818067 | 0.626486 | 0.481143 | 0.522547 |
| validation | logistic_regression | 0.864814 | 0.826921 | 0.635575 | 0.682239 |
| validation | linear_svm | 0.879975 | 0.810247 | 0.737291 | 0.754173 |
| test | nb | 0.819646 | 0.886575 | 0.500193 | 0.545789 |
| test | logistic_regression | 0.859760 | 0.810086 | 0.658390 | 0.698190 |
| test | linear_svm | 0.861655 | 0.780204 | 0.713869 | 0.735382 |

Winner: **linear_svm**, chọn theo validation. Giá trị đầy đủ trong comparison.json;
selected_test.json kiểm chứng model đã tải lại cho kết quả trùng với winner.

| Nhãn test | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| lecturer | 0.909593 | 0.935808 | 0.922514 | 2290 |
| curriculum | 0.691126 | 0.708042 | 0.699482 | 572 |
| facility | 0.922535 | 0.903448 | 0.912892 | 145 |
| other | 0.597561 | 0.308176 | 0.406639 | 159 |

Confusion matrix (hàng thật, cột dự đoán):

| | lecturer | curriculum | facility | other |
|---|---:|---:|---:|---:|
| lecturer | 2143 | 123 | 5 | 19 |
| curriculum | 151 | 405 | 3 | 13 |
| facility | 3 | 10 | 131 | 1 |
| other | 59 | 48 | 3 | 49 |

Ảnh thực tế: `reports/figures/topic/confusion_matrix.png`.

## Phân tích lỗi

Sai **438/3166** câu. Cặp nhầm lớn nhất là curriculum → lecturer (151),
lecturer → curriculum (123), other → lecturer (59), other → curriculum (48).
Lớp other có recall 30,82%, thấp nhất. Không thể giải thích chỉ bằng ít mẫu:
facility còn ít mẫu test hơn nhưng F1 đạt 91,29%. Phạm vi nghĩa rộng của other,
ngữ cảnh thiếu và giao thoa chủ đề là giả thuyết cần nghiên cứu tiếp.

Đã đọc thủ công các mẫu lỗi theo ID (không xuất nguyên văn corpus):

- `test:000024`: đề nghị phương pháp học lập trình; nhãn lecturer nhưng dự đoán curriculum.
  Nội dung giảng dạy và chương trình dùng từ vựng giao nhau.
- `test:000041`: hành động của người dạy với micro/bảng; nhãn lecturer nhưng dự đoán facility.
  Một câu đề cập cả người và thiết bị, khó biểu diễn bằng một nhãn duy nhất.
- `test:000959`: thiếu chỗ trong phòng thực hành; nhãn facility nhưng dự đoán curriculum.
  Từ vựng về thực hành có thể kéo dự đoán sang nội dung đào tạo.
- `test:000044`, `test:000049`, `test:000126`: câu và nhãn nguồn có vẻ không đồng nhất
  khi đọc riêng câu; cần ngữ cảnh/quy tắc gán nhãn để kết luận. Không tự sửa ground truth.
- `test:000085`: lời nhận xét không nêu đối tượng rõ ràng; thiếu ngữ cảnh để xác định chủ đề.

Ví dụ **tự viết**, không phải mẫu đánh giá: câu khen giảng viên đồng thời chê phòng nóng
được model trả facility; câu về hoạt động đoàn hội được trả lecturer. Đây là hành vi
đo được trong reload.json, không gán kỳ vọng giả thành accuracy. TF-IDF n-gram không
mô hình hóa đầy đủ ngữ cảnh, và hợp đồng chỉ cho một nhãn chủ đề mỗi câu.

## Kiểm chứng và bàn giao

- Tests gồm fixture bốn lớp, dữ liệu sai, vocabulary chỉ train, chọn bằng validation/quy tắc hòa,
  confusion matrix, vòng đời CLI, tải trong tiến trình mới, từ chối checksum/môi trường sai
  và corpus khác manifest. Toàn bộ thư mục tests đạt **63 passed**, không skip, với
  `TV2_RUN_REAL_DATA=1`; gồm 45 Data/Sentiment và 18 Topic.
  Log: `reports/evidence/topic/pytest-local.txt`.
- Review độc lập phát hiện thiếu kiểm tra metadata lồng nhau; đã tái hiện bằng test thất bại,
  sửa kiểm tra metrics validation/thời gian UTC/cấu hình khớp pipeline, rồi chạy lại đủ 63 tests.
- Notebook đã chạy 4 code cell, 0 error outputs bằng runner Python; bằng chứng ở
  `reports/evidence/topic/notebook-execution.json`.
- Winner được serialize lại không fit, tải ở tiến trình mới; 5 câu tự viết có dự đoán
  trước/sau giống nhau. Evaluate lại toàn test khớp comparison đã đóng băng.
- `pip check` đạt. Runtime ML thực tế ghi trong environment.json, requirements-local.txt
  và metadata. Có OptimizeWarning `Unknown solver options: iprint` ở LR với tổ hợp
  scikit-learn/SciPy local; chạy hoàn tất, cần kiểm lại khi leader khóa môi trường.

Artifact: `models/topic_pipeline.joblib` (ignore Git) và `models/topic_metadata.json`.
Backend nhận cả hai, kiểm SHA-256, Python 3.13 và đúng năm phiên bản package trong metadata;
dùng list raw strings, không chuẩn hóa thêm. `load_topic_pipeline` cung cấp kiểm tra
task/labels/checksum/runtime/structure trước suy luận; chỉ load artifact nội bộ đáng tin cậy.
Không có confidence giả. Chưa kiểm tích hợp API thật với cả Sentiment/Topic.

## Còn chờ ngoài triển khai local

- Leader xác nhận quyền sử dụng/phân phối dữ liệu (nguồn license unknown), nghiệm thu M1.
- Khóa môi trường chung và kiểm hai model trong Backend.
- Đưa phần TV4 sang nhánh phù hợp, review/merge vào develop và bàn giao artifact nội bộ.

## Cập nhật xác minh Phase 2 — 2026-10-30

Trên bản tích hợp, artifact/metadata/manifest và năm phiên bản ML khớp môi trường
khóa Phase 1. Tải trong tiến trình mới tái lập cả năm câu reload; metrics
validation/test tính lại khớp comparison và selected_test. Vocabulary/IDF khớp
thống kê train. Cấu hình ba thuật toán và output notebook khớp báo cáo đã lưu;
không train hoặc chọn lại winner. Bộ Data/ML đạt 63 tests, không skip.
Bằng chứng: `reports/evidence/phase-2/`.
Other vẫn có Recall 30,82%, F1 40,66%; giữ cặp trùng train và giới hạn một chủ đề
mỗi câu. Nguồn vẫn license unknown; kế hoạch mới cho phép demo local nhưng
không cho phép phân phối dataset/model. Backend/Frontend chưa được nghiệm thu.
