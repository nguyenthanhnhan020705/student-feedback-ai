# Đánh giá

Các số dưới đây là kết quả **chạy thật ngày 2026-11-04** trong project này, trên dữ liệu UIT-VSFC cục bộ, bằng lệnh ghi ở từng mục.
Chúng là số đo thực nghiệm, không phải cam kết hiệu năng; chạy lại sẽ cho cùng kết quả vì seed cố định (`random_state=42`).

## 1. Baseline (3 nhãn cảm xúc, 4 nhãn chủ đề) — `train` + `experiment baseline`

Chọn mô hình theo macro-F1 trên **validation**; test chỉ để báo cáo.

| Nhiệm vụ | Thuật toán | Validation macro-F1 | Test accuracy | Test macro-F1 |
| --- | --- | --- | --- | --- |
| sentiment | nb | 0.5955 | 0.8572 | 0.5870 |
| sentiment | logistic_regression | 0.6889 | 0.8898 | 0.6484 |
| sentiment | **linear_svm (chọn)** | 0.7530 | 0.8970 | 0.7051 |
| topic | nb | 0.5225 | 0.8196 | 0.5458 |
| topic | logistic_regression | 0.6822 | 0.8598 | 0.6982 |
| topic | **linear_svm (chọn)** | 0.7542 | 0.8617 | 0.7354 |

`evaluate --task topic` trên artifact vừa huấn luyện cho accuracy khớp với `comparison.json` (có test tự động). Macro-F1 thấp hơn accuracy vì lớp thiểu số (neutral, other) nhỏ.

## 2. Thí nghiệm CT2–CT5 — kiểm soát là model phục vụ (CT4 đóng băng)

Validation macro-F1; ứng viên thắng chỉ được chọn trên validation. Mọi kết quả đều `promotion: "not_deployed"`.

| Thí nghiệm | sentiment (kiểm soát → thắng) | topic (kiểm soát → thắng) |
| --- | --- | --- |
| `class_weights` (sqrt_balanced, balanced, minority_x2) | 0.7974 → baseline | 0.7695 → baseline |
| `word_char` (đặc trưng ký tự, trọng số 0.5/1/2) | 0.7974 → baseline (tốt nhất khác: 0.7899) | 0.7695 → baseline (tốt nhất khác: 0.7635) |
| `augmentation` (25/50/100%) | 0.7974 → original | 0.7695 → original |
| `selective` | chính sách `always_answer` trên 791 mẫu audit: accepted accuracy 0.8205; các chính sách khác báo `no_reviewed_answerability` (thiếu nhãn answerability đã duyệt) | |

Kết luận trung thực: trong lần chạy này **không có cải tiến nào vượt model kiểm soát** trên validation, nên không đề xuất thay model phục vụ.

## 3. Hai bộ nhãn

Baseline (UIT-VSFC gốc) và serving v3 (hỗn hợp/chưa xác định, nhiều chủ đề, luật + CT4 audit) khác nhau. **Không dùng điểm trên để tuyên bố độ chính xác của nhãn v3.**
Tương đương hành vi serving so với bản cũ được kiểm bằng `tests/parity` (30 ca, giống nhau), không phải bằng metrics.

## 4. Chưa làm / hạn chế

- CT1 (giao thức đánh giá) và các báo cáo lịch sử trong repo cũ **chưa được chạy lại**; chỉ mang vào logic tái lập CT2–CT5 như trên.
- Chưa so khớp số liệu từng chữ số với báo cáo lịch sử của repo cũ; chỉ xác nhận cùng seed/cấu hình và đầu ra mới nhất quán.
- Không có phân tích lỗi thủ công; `evaluate` ghi `errors.json` (các dòng sai) để phân tích tiếp.
- Cảnh báo đã biết: `OptimizeWarning: Unknown solver options: iprint` (scikit-learn/scipy) và cảnh báo `httpx`/Starlette TestClient; không ảnh hưởng kết quả.
