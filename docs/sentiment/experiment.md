# Thiết kế thí nghiệm — Phân loại cảm xúc (Sentiment)

**Trạng thái:** thiết kế. Chưa huấn luyện hay đánh giá trên dữ liệu thật.

## 1. Mục tiêu
Phân loại phản hồi sinh viên tiếng Việt thành 3 nhãn: `negative`, `neutral`, `positive`.

## 2. Dữ liệu (dự kiến)
- Nguồn dự kiến: UIT-VSFC. Số dòng tham khảo từ dataset card: train 11426, validation 1583, test 3166 (chưa phải số kiểm đếm của nhóm).
- Dữ liệu do Data bàn giao (M1) cùng manifest. Điều kiện sử dụng/phân phối chờ leader duyệt; dataset không đưa lên repo public.
- Giữ nguyên split chính thức, không shuffle, không deduplicate trong baseline.

## 3. Tiền xử lý
Dùng `ml.preprocessing.normalize_text` (NFC, lower, gộp khoảng trắng, strip) làm `preprocessor` của TF-IDF. Không xóa dấu, dấu câu, chữ số hay từ phủ định.

## 4. Mô hình baseline
Pipeline `TF-IDF -> classifier`, không grid search.
- TF-IDF: ngram_range=(1,2), min_df=2, max_df=1.0, sublinear_tf=True, norm=l2, strip_accents=None, lowercase=False, token_pattern=`(?u)\b\w+\b`.
- `nb`: MultinomialNB(alpha=1.0).
- `logistic_regression`: C=1.0, solver=lbfgs, max_iter=2000, class_weight=None, random_state=42.
- `linear_svm`: LinearSVC(C=1.0, dual=auto, max_iter=5000, class_weight=None, random_state=42).

## 5. Quy trình
1. Fit cả ba mô hình chỉ trên train (train phải đủ 3 nhãn).
2. Đánh giá trên validation; chọn mô hình có Macro F1 cao nhất.
3. Hòa (chênh <= 0.000001): so Accuracy; vẫn hòa thì theo thứ tự nb, logistic_regression, linear_svm.
4. Đóng băng cấu hình và winner, rồi đánh giá cả ba trên test đúng một lần.
5. Không fit lại trên train+validation, không chỉnh cấu hình sau khi xem test; thí nghiệm bổ sung phải đánh dấu riêng.

## 6. Chỉ số
Accuracy, Macro Precision/Recall/F1 (zero_division=0), chỉ số từng lớp, Confusion Matrix (hàng = thật, cột = dự đoán), thứ tự nhãn: negative, neutral, positive.

## 7. Đầu ra
- `models/sentiment_pipeline.joblib`, `models/sentiment_metadata.json`
- `reports/metrics/sentiment/comparison.json`, `selected_test.json`
- `reports/figures/sentiment/confusion_matrix.png`
- `docs/sentiment/report.md` (bảng so sánh, phân tích lỗi)

## 8. Kiểm thử
- Unit test dùng fixture nhỏ tự tạo, chỉ kiểm tra hành vi của code, không dùng làm kết quả nghiên cứu.
- Kiểm tra tải lại artifact trong tiến trình mới và đối chiếu dự đoán trước/sau khi lưu.

## 9. Hạn chế và rủi ro
- Chưa có số liệu thật.
- Dataset có thể có câu trùng trong/giữa các split (nguy cơ rò rỉ), cần Data báo và leader ghi nhận.
- Lớp `neutral` thường khó phân biệt; sẽ phân tích lỗi sau khi có kết quả.
- LinearSVC không có xác suất, nên không đưa điểm tin cậy giả vào đầu ra.