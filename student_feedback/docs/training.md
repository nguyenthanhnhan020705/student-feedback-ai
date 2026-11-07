# Huấn luyện

`feedback-ai --project-root . train --task sentiment|topic --output <thư mục mới>`

- Đặc trưng: TF-IDF (`TFIDF_PARAMS` trong `training/sentiment.py`, `training/topic.py`), fit **chỉ trên train**.
- Ba thuật toán mỗi nhiệm vụ: `nb` (Multinomial NB, alpha=1), `logistic_regression` (C=1, lbfgs, max_iter 2000), `linear_svm` (C=1, max_iter 5000); `random_state=42`.
- **Chọn mô hình bằng validation** (`macro_f1`, quy tắc hòa trong `select_model`); test chỉ để báo cáo sau khi chọn.
- Đầu ra: `<task>_pipeline.joblib`, `<task>_metadata.json` (nhãn, phiên bản thư viện, SHA-256 artifact và manifest dữ liệu,
  tham số, lựa chọn), `comparison.json`, `confusion_matrix.png`.
- Từ chối: thư mục đầu ra đã tồn tại, đường dẫn chứa `serving`, manifest dữ liệu không khớp.
- Không tự thay model phục vụ; muốn dùng model mới phải nhập thủ công thành bundle mới và xác minh lại.

## Thí nghiệm (CT1–CT5)

`feedback-ai --project-root . experiment <tên> --config configs/<tên>.json --output <thư mục mới>`

| Tên | Nội dung | Điều kiện |
| --- | --- | --- |
| `baseline` | Huấn luyện + so sánh ba thuật toán cho cả hai nhiệm vụ | chỉ cần dữ liệu |
| `class_weights` | Thử chiến lược trọng số lớp lên model kiểm soát | model kiểm soát + checksum trong config |
| `word_char` | Thêm đặc trưng ký tự | cần kết quả `class_weights` làm CT2 (dùng `tools/fill_checksums.py`) |
| `augmentation` | Tăng cường dữ liệu theo tỉ lệ | cần CT2 và CT3 |
| `selective` | Ngưỡng/chính sách từ chối dự đoán trên validation | model kiểm soát + checksum |

Checksum của model kiểm soát được kiểm tra trước khi nạp; kết quả ghi `results.json` với `promotion: "not_deployed"`.
Mô hình kiểm soát mặc định là bundle phục vụ (`artifacts/serving/ct4/research-selected`), config đã dựng sẵn trong `configs/`.
Chuỗi: `class_weights` → điền checksum → `word_char` → điền checksum → `augmentation`.
