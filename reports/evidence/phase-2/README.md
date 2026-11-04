# Phase 2 — xác minh Data và hai artifact

Phạm vi ngày 2026-10-30: bản tích hợp `feature/integration-p0`, kế thừa Phase 1.
Không thay thuật toán, dữ liệu, split, metadata, model hoặc metrics gốc.

## Cách kiểm lại

Từ thư mục bản tích hợp, dùng môi trường đã cài từ lock ở Phase 1:

```powershell
$env:TV2_RUN_REAL_DATA='1'
./.local-tools/phase1-verify/Scripts/python.exe -m pytest tests/test_data.py tests/test_labels.py tests/test_preprocessing.py tests/test_sentiment_training.py tests/test_sentiment_artifacts.py tests/test_topic_training.py tests/test_topic_artifacts.py -q -p no:cacheprovider
./.local-tools/phase1-verify/Scripts/python.exe reports/verify_phase2.py
./.local-tools/phase1-verify/Scripts/python.exe -m pip check
```

Có thể dùng venv khác nếu cài đúng `requirements-lock.txt`. `.venv` cũ thiếu
nbformat; dùng môi trường Phase 1 cho kiểm chứng đầy đủ, không nâng gói ML.

## Bằng chứng

- `pytest-locked.txt`: 63 passed, 0 skipped, 11 OptimizeWarning về `iprint` từ
  scikit-learn/SciPy; chạy cả ba bài dữ liệu thật với `TV2_RUN_REAL_DATA=1`.
- `pytest.txt`: cùng 63 tests trên `.venv` tích hợp cũ, không phải bằng chứng
  môi trường khóa đầy đủ.
- `verification.json`: checksum nguồn/manifest/artifact, môi trường, metrics
  validation/test của winner tính lại, dự đoán các câu đối chiếu ở tiến trình mới,
  vocabulary và IDF tái tính từ train bằng đếm tần suất (không fit), hash các đầu
  vào được giữ nguyên.
- `verification.txt`: log chạy script; nbformat cảnh báo notebook thiếu cell ID.
  Validation hiện đạt; chưa chỉnh notebook gốc chỉ để loại cảnh báo định dạng.
- Notebook 01/02/03 có lần lượt 4/3/4 code cells đã chạy, không có error output.
  Bảng metrics của cả ba thuật toán trong notebook 02/03 khớp comparison.json
  đến sáu chữ số thập phân. Output EDA được đối chiếu với manifest.
- Đọc code train/select và tests kiểm fit train, vocabulary, validation và quy
  tắc hòa. Winner không refit train+validation. Không chạy lại notebook train;
  notebook Sentiment có cell train ghi đè đầu ra nên không dùng Run All để audit.

## Kết quả và giới hạn

Dataset: 11426 train / 1583 validation / 3166 test; 9 file nguồn khớp SHA-256.
Một nhóm trùng gồm hai dòng train được giữ, không có text chuẩn hóa giao split.
Không kết luận đã loại mọi near-duplicate hay mọi dạng rò rỉ.

| Task | Winner | Test Accuracy | Test Macro F1 | Hạn chế lớp |
| --- | --- | ---: | ---: | --- |
| Sentiment | linear_svm | 0.897031 | 0.705104 | neutral Recall 0.179641, F1 0.277778 |
| Topic | linear_svm | 0.861655 | 0.735382 | other Recall 0.308176, F1 0.406639 |

Chọn winner trên validation. NB/LR không được lưu thành artifact riêng:
cấu hình và số liệu được đối chiếu code/notebook/báo cáo đã đóng băng, không
tuyên bố đã tái suy luận NB/LR trong Phase 2. Chỉ hai winner được đánh giá lại.

Nguồn vẫn `license unknown`, manifest giữ `pending_leader_review` để bảo toàn
provenance. Chỉ đạo trong kế hoạch 2026-10-30 cho phép demo kỹ thuật local;
không biến thành giấy phép nguồn hoặc quyền công bố dataset/model.

Kernel Jupyter tương tác (`ipykernel`, `nbclient`) chưa có trong runtime lock.
Phase 2 kiểm schema/output đã lưu và chạy kiểm chứng bằng Python, không xác
nhận chạy notebook tương tác. Không cần thêm kernel để chạy API hoặc script này.

Không nghiệm thu Backend/Frontend hoặc toàn dự án ở đây. Ba lỗi đã biết
(UTF-8 JSON, nhãn prototype, timeout body) tiếp tục thuộc Phase 3–4.
